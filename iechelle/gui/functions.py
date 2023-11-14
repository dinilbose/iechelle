
import apollinaire as apn
import numpy as np
import pandas as pd
from astropy import units as u


import astropy
from astropy.coordinates import SkyCoord
import numpy as np
import pandas as pd
from scipy import stats
from astropy.io.fits import Undefined
from astropy.wcs import WCS

from astropy.io.votable import parse

def calculate_synthetic_spectrum(fits_file=None, bkg_file=None, pkb_file=None, n_harvey=2):
    '''
    From the filename it calculate synthetic spectrum
    
    '''
    param_back = np.loadtxt (bkg_file)[:,0]
    pkb = np.loadtxt (pkb_file)
    from astropy.io import fits
    import pandas
    with fits.open(
        fits_file
        ) as data:
        df = pandas.DataFrame(data[0].data)

        ff = df[0].values
        pp = df[1].values
        ff = ff.byteswap().newbyteorder()
        pp = pp.byteswap().newbyteorder()

        f = (ff*u.Hz).to(env.frequency_unit)
        p = pp*env.power_unit
        
        ff = f.value
        pp = p.value
    freq = ff
    noise_free, entropy = apn.synthetic.create_synthetic_psd (freq, pkb, param_back=param_back,
                                                         noise_free=True,n_harvey=n_harvey)

    # psd, entropy = apn.synthetic.create_synthetic_psd (freq, pkb, param_back=param_back,
    #                                               entropy=127138838169534406638366956769226291439)

    value_dict={}
    value_dict['synthetic_psd']=noise_free
    value_dict['freq']=freq
    value_dict['psd']=pp
    data_frame=pd.DataFrame(value_dict)
    return data_frame


    


def votable_to_pandas(votable_file):
    print(votable_file)
    votable = parse(votable_file)
    table = votable.get_first_table().to_table(use_names_over_ids=True)
    return table.to_pandas()
