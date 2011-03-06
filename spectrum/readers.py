
def open_1d_txt(filename):
    import atpy
    T = atpy.Table(filename, type='ascii',
            Reader=atpy.asciitables.asciitable.CommentedHeader, masked=True)
    
    xarr = T.data[T.data.dtype[0]]
    spectrum = T.data[T.data.dtype[1]]
    if len(T.columns) > 2:
        error = T.data[T.data.dtype[2]]

    return xarr,spectrum,error


def open_1d_fits(filename,specnum=0,wcstype='',errspecnum=None):
    """
    Grabs all the relevant pieces of a simple FITS-compliant 1d spectrum

    Inputs:
        wcstype - the suffix on the WCS type to get to
            velocity/frequency/whatever
        specnum - Which # spectrum, along the y-axis, is 
            the data?
        errspecnum - Which # spectrum, along the y-axis,
            is the error spectrum?

    """
    import pyfits
    f = pyfits.open(filename)
    hdr = f[0].header
    spec = f[0].data
    errspec  = None
    if hdr.get('NAXIS') == 2:
        if errspecnum is not None:
            errspec = spec[errspecnum,:]
        if isinstance(specnum,list):
            # allow averaging of multiple spectra (this should be modified
            # - each spectrum should be a Spectrum instance)
            spec = spec[specnum,:].mean(axis=0)
        elif isinstance(specnum,int):
            spec = spec[specnum,:]
        else:
            raise TypeError("Specnum is of wrong type (not a list of integers or an integer).  Type: %s" %
                    str(type(specnum)))
    elif hdr.get('NAXIS') > 2:
        raise ValueError("Too many axes for open_1d - use open_3d instead")
    if hdr.get('CD1_1'+wcstype):
        dv,v0,p3 = hdr['CD1_1'+wcstype],hdr['CRVAL1'+wcstype],hdr['CRPIX1'+wcstype]
    else:
        dv,v0,p3 = hdr['CDELT1'+wcstype],hdr['CRVAL1'+wcstype],hdr['CRPIX1'+wcstype]

    xconv = lambda v: ((v-p3+1)*dv+v0)/conversion_factor
    xarr = xconv(arange(len(spec)))

    return spec,errspec,xarr,hdr

def parse_header(self,hdr,specname=None):
    """
    Parse parameters from a .fits header into required spectrum structure
    parameters
    """
    if hdr.get('CUNIT1'+wcstype) in ['m/s','M/S']:
        self.xunits = 'km/s' # change to km/s because you're converting units
    else:
        self.xunits = hdr.get('CUNIT1'+wcstype)

    if hdr.get('BUNIT'):
        self.units = hdr.get('BUNIT').strip()
    else:
        self.units = 'undefined'

    if hdr.get('REFFREQ'+wcstype):
        self.reffreq = hdr.get('REFFREQ'+wcstype)
    else:
        self.reffreq = None

    if hdr.get('CTYPE1'+wcstype):
        self.xtype = hdr.get('CTYPE1'+wcstype)
    else:
        self.xtype = 'VLSR'

    if specname is not None:
        self.specname = specname
    elif hdr.get('OBJECT'):
        self.specname = hdr.get('OBJECT')