
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




def pkb_to_a2z(pkb_filename,A2Z_file,split_incl_flag = 0,split_modesp_flag = 0):
    # import numpy as np

    # path_in = input('Give me the path_in: ')
    # print('Do you want to put splittings and inclination angle (1=Yes/0=No)?')
    split_incl_flag = 0
    # print('Do you want to put splittings in the modes p (1=Yes/0=No)?')
    split_modesp_flag = 0

    # path_in = path_in + '/'
    file_pkb_in = pkb_filename
    # A2Z_sfile = 'modes_parameter_selected.a2z'
    # out_path = path_in

    # Reading data from file
    n, l, freq, efreq, h, eh, w, ew = np.genfromtxt(file_pkb_in, skip_header=10, unpack=True, usecols=(0, 1, 2, 3, 4, 5, 6, 7))

    # Sorting by frequencies
    indx_sort = np.argsort(freq)
    n = n[indx_sort]
    l = l[indx_sort]
    freq = freq[indx_sort]
    efreq = efreq[indx_sort]
    h = h[indx_sort]
    eh = eh[indx_sort]
    w = w[indx_sort]
    ew = ew[indx_sort]
    n0 = 0
    n1 = 0
    n2 = 0
    n3 = 0

        # Computing dnu from l=0 assuming all correlatives
    indx_l0 = np.where(l == 0)[0]
    if len(indx_l0) >= 1:
        n0 = len(indx_l0)
    indx_l1 = np.where(l == 1)[0]
    if len(indx_l1) >= 1:
        n1 = len(indx_l1)
    indx_l2 = np.where(l == 2)[0]
    if len(indx_l2) >= 1:
        n2 = len(indx_l2)
    indx_l3 = np.where(l == 3)[0]
    if len(indx_l3) >= 1:
        n3 = len(indx_l3)

    coefficients_l0 = np.polyfit(np.arange(len(indx_l0)), freq[indx_l0], 1)
    dnu = coefficients_l0[0]
    print('Dnu=', dnu)

    # Recomputing n values
    if len(indx_l1) >= 1:
        n[indx_l1] = 10 * freq[indx_l1] / dnu
    if len(indx_l0) >= 1:
        n[indx_l0] = freq[indx_l0] / dnu
    if len(indx_l2) >= 1:
        n[indx_l2] = freq[indx_l2] / dnu - 1
    if len(indx_l3) >= 1:
        n[indx_l3] = freq[indx_l3] / dnu - 1

    # Writing to A2Z_sfile
    with open(A2Z_file, 'w') as f:
        # Header
        #f.write('# n l param extent value error fixed prior_low prior_high prior_fol prior_foh\n')
        #f.write('#----------------------------------------------------------------------------\n')

        # Loop for standard p modes l=0,2,3 ; TO have l=2 and 3 there should be an l=0
        if n0 >= 1:
            for i in range(n0):
                nn = n[indx_l0[i]]
                a0 = np.where(n[indx_l2] == nn-1)[0]
                a3 = np.where(n[indx_l3] == nn-1)[0]

                if len(a0) > 0:
                    f.write(f"{int(n[indx_l2[a0[0]]]):.2f} 2 freq mode {freq[indx_l2[a0[0]]]:.2f} 0.0 0.0 {freq[indx_l2[a0[0]]]-1:.2f} {freq[indx_l2[a0[0]]]+1:.2f}\n")
                f.write(f"{(nn):.0f} 0 freq mode {freq[indx_l0[i]]:.2f} 0.0 0.0 {freq[indx_l0[i]]-1:.2f} {freq[indx_l0[i]]+1:.2f}\n")
                if len(a3) > 0:
                    f.write(f"{int(n[indx_l3[a3[0]]]):.2f} 3 freq mode {freq[indx_l3[a3[0]]]:.2f} 0.0 0.0 {freq[indx_l3[a3[0]]]-1:.2f} {freq[indx_l3[a3[0]]]+1:.2f}\n")

                f.write(f"{int(nn):.0f} a height order {h[indx_l0[i]]*0.5:.2f} 0.0 0.0 5 {h[indx_l0[i]]*10:.2f}\n")
                f.write(f"{int(nn):.0f} a width order 0.3 0.0 0.0 0.001 20\n")

        # Loop for l=1 (mixed) modes
        if n1 >= 1:
            for i in range(n1):
                f.write(f"{int(n[indx_l1[i]]):.0f} 1 freq mode {freq[indx_l1[i]]:.2f} 0.0 0.0 {freq[indx_l1[i]]-1:.2f} {freq[indx_l1[i]]+1:.2f}\n")
                f.write(f"{int(n[indx_l1[i]]):.0f} 1 height mode {h[indx_l1[i]]*0.5:.2f} 0.0 0.0 5 {h[indx_l1[i]]*10:.2f}\n")
                f.write(f"{int(n[indx_l1[i]]):.0f} 1 width mode 0.3 0.0 0.0 0.0001 20\n")
                if split_incl_flag == 1:
                    f.write(f"{int(n[indx_l1[i]]):.0f} 1 split mode 0.1 0.0 0.0 0.01 1.0\n")

        if split_incl_flag == 1 or split_modesp_flag == 1:
            f.write('a a angle global 45.0 0.0 0.0 0.0 90.0\n')
        if split_modesp_flag == 1:
            f.write('a a split global 0.1 0.0 0.0 0.01 1.0\n')
        
        #f.write('#----------------------\n')
        f.write('a 0 amp_l global 1.0 0.0 0.0 0.0 0.0\n')
        f.write('a 1 amp_l global 1.5 0.0 0.0 0.2 2.5\n')
        f.write('a 2 amp_l global 0.7 0.0 0.0 0.2 1.5\n')
        f.write('a 3 amp_l global 0.2 0.0 0.0 0.05 1.0\n')
        #f.write('a 4 amp_l global 0.05 0.0 1.0 0.0 0.0 0.0 0.0\n')
        #f.write('#----------------------\n')    
