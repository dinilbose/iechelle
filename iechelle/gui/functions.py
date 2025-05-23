
"""
Provides utility functions for the iEchelle application, primarily for astrophysical calculations.

This module currently contains functions for generating synthetic power spectra
based on observed data and model parameters, utilizing libraries such as
Apollinaire, NumPy, and Pandas.
"""
import apollinaire as apn
import numpy as np
import pandas as pd
from astropy import units as u
from env import Environment as env

def calculate_synthetic_spectrum(fits_file=None, bkg_file=None, pkb_file=None, n_harvey=2):
    """
    Calculates a synthetic power spectrum based on observed data and model parameters.

    This function uses the Apollinaire library to generate a noise-free synthetic
    Power Spectral Density (PSD). It reads an observed periodogram from a FITS file,
    background model parameters from a text file, and peak-bagging parameters
    (oscillation mode properties) from another text file.

    Args:
        fits_file (str, optional): Path to the FITS file containing the observed
            periodogram. The FITS file is expected to have frequency in its
            first data column and power in its second, which will be converted
            to units specified in `env.frequency_unit` (e.g., uHz) and
            `env.power_unit` respectively. Defaults to None.
        bkg_file (str, optional): Path to a text file containing the background
            model parameters. These parameters are loaded using `np.loadtxt`.
            Defaults to None.
        pkb_file (str, optional): Path to a text file containing the peak-bagging
            parameters (e.g., mode frequencies, heights, widths, etc.),
            loadable by `np.loadtxt`. This defines the oscillation modes for the
            synthetic spectrum. Defaults to None.
        n_harvey (int, optional): The number of Harvey-like components to use for
            modeling the background noise in the synthetic spectrum.
            Defaults to 2.

    Returns:
        pandas.DataFrame: A DataFrame with the following columns:
            - 'synthetic_psd': The calculated noise-free synthetic power spectrum.
            - 'freq': The frequency array, converted to `env.frequency_unit`.
            - 'psd': The observed power spectrum from the input FITS file,
                     converted to `env.power_unit`.

    Raises:
        FileNotFoundError: If any of the input files do not exist.
        Exception: Can re-raise exceptions from underlying libraries like
                   `astropy.io.fits.open` or `np.loadtxt` if file formats
                   are incorrect.

    Notes:
        - Relies on `env.frequency_unit` and `env.power_unit` (from `env.py`)
          for unit conversions.
        - Uses `apollinaire.synthetic.create_synthetic_psd` for the core
          calculation.
    """
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


    
