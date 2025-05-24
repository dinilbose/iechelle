import pytest
import numpy as np
import pandas as pd
from astropy.io import fits # For mocking FITS structure
from astropy import units as u
from unittest.mock import patch, mock_open

from iechelle.gui.functions import calculate_synthetic_spectrum
from iechelle.gui.env import Environment # To access env.frequency_unit etc.

# Initialize environment to make units accessible
# This assumes Environment class sets these as class variables or instance variables on init
# If they are instance variables, you might need `env_instance = Environment()`
# and then `env_instance.frequency_unit`. For simplicity, let's assume direct access
# after Environment() call if they are set up that way in env.py, or set them manually for test.

# Setup a minimal Environment for testing purposes if direct import doesn't suffice
# This is a simplified approach. A better way might be to pass env vars or use dependency injection.
@pytest.fixture(scope="module")
def test_env():
    # Mimic how env.py sets up units if they are not directly class variables
    # If Environment() call in main.py sets these globally enough, this might not be needed.
    # Or, if calculate_synthetic_spectrum can take units as params, that's better.
    # For now, let's assume they are accessible after 'from iechelle.gui.env import Environment'
    # and that Environment() in main.py makes them available in some way that tests can see.
    # A more robust test setup might involve instantiating Environment or directly setting
    # the required unit attributes on a mock Environment object if the function expects an instance.
    # Given the current structure of functions.py, it directly imports 'env'
    # from 'from env import Environment as env'.
    # So we need to ensure that `env.frequency_unit` and `env.power_unit` are set.
    # One way is to instantiate:
    Environment() # This should make Environment.frequency_unit etc. available if they are class level
                  # or if the constructor sets them on the class.
    # If functions.py actually does `from env import Environment as env_module` and uses `env_module.Environment.frequency_unit`
    # then the above is fine. If it does `from env import Environment` and then `e = Environment()` and `e.frequency_unit`,
    # then the function itself needs an env instance.
    # The provided code in functions.py is `from env import Environment as env`.
    # This means it expects `env.frequency_unit`.
    # The `Environment()` call in `main.py` implies that `Environment` itself is being used as a namespace,
    # or that its constructor has side effects of setting up these shared attributes.
    # Let's assume the constructor of Environment sets these up in a way that `env.frequency_unit` becomes available.
    pass


@patch('iechelle.gui.functions.fits.open')
@patch('iechelle.gui.functions.np.loadtxt')
@patch('iechelle.gui.functions.apn.synthetic.create_synthetic_psd')
def test_calculate_synthetic_spectrum_valid_inputs(mock_create_psd, mock_loadtxt, mock_fits_open, test_env):
    # 1. Setup Mocks
    # Mock FITS data
    # Create a record array as astropy.io.fits.open().data would for a FITS table
    # The dtypes must match what byteswap().newbyteorder() would expect.
    # FITS typically stores data in big-endian ('>').
    freq_data = np.array([10, 20, 30], dtype='>f8')
    power_data = np.array([1, 2, 3], dtype='>f8')
    
    # The function performs byteswap().newbyteorder() on these. For testing, we can provide
    # data that, after this operation, results in the desired native-endian values.
    # Or, more simply, mock the output of the .byteswap().newbyteorder() calls if possible,
    # but that's harder. Let's assume the function correctly handles the byte swap and
    # our input to the mock should be what the FITS file *would* contain (big-endian).
    
    mock_fits_records = np.core.records.fromarrays([freq_data, power_data], names='0,1')

    # Mock the HDU and HDUList structure
    mock_fits_hdu = fits.BinTableHDU.from_columns(fits.ColDefs(mock_fits_records))
    # In older astropy, it might be PrimaryHDU or a specific table HDU.
    # The important part is that accessing .data on the HDU object (e.g. data[0].data)
    # should yield something convertible to a pandas DataFrame as in the original function.
    # The original code does `df = pandas.DataFrame(data[0].data)`. So data[0] should be an HDU.
    mock_hdulist_obj = fits.HDUList([mock_fits_hdu]) # data[0] will be mock_fits_hdu
    
    # Configure the mock for `with fits.open(...) as data:`
    mock_fits_open.return_value.__enter__.return_value = mock_hdulist_obj


    # Mock background and pkb data
    # np.loadtxt for bkg_file is expected to return a 2D array, and then [:,0] is taken.
    mock_param_back_full = np.array([[0.1, 99], [0.2, 99]]) 
    mock_pkb_array = np.array([[15, 1, 2], [25, 2, 3]]) # Example pkb data
    # np.loadtxt for pkb_file returns the array directly.
    mock_loadtxt.side_effect = [mock_param_back_full, mock_pkb_array]

    # Mock apollinaire's synthetic PSD creation
    expected_synthetic_psd = np.array([0.5, 1.5, 2.5])
    mock_create_psd.return_value = (expected_synthetic_psd, "mock_entropy_value")

    # 2. Call the function
    # Ensure Environment.frequency_unit and Environment.power_unit are set correctly for the test.
    # The test_env fixture calls Environment(), which should set the default units.
    # We can override them here for specific test conditions if needed.
    Environment.frequency_unit = u.Unit("uHz")
    Environment.power_unit = u.Unit("ppm2/uHz") # Example, ensure it's astropy compatible


    result_df = calculate_synthetic_spectrum(
        fits_file="dummy.fits",
        bkg_file="dummy_bkg.txt",
        pkb_file="dummy_pkb.txt",
        n_harvey=2
    )

    # 3. Assertions
    assert isinstance(result_df, pd.DataFrame)
    assert 'synthetic_psd' in result_df.columns
    assert 'freq' in result_df.columns
    assert 'psd' in result_df.columns

    pd.testing.assert_series_equal(result_df['synthetic_psd'], pd.Series(expected_synthetic_psd), check_dtype=False)
    
    # Original data was in native endian after read by pandas.
    # The function converts FITS data (originally big-endian) to native.
    # So, the values [10,20,30] and [1,2,3] are what we expect after internal processing.
    # These are then scaled by units.
    original_freq_values = np.array([10, 20, 30]) 
    original_power_values = np.array([1, 2, 3])

    expected_freq_in_env_units = (original_freq_values * u.Hz).to(Environment.frequency_unit).value
    pd.testing.assert_series_equal(result_df['freq'], pd.Series(expected_freq_in_env_units), check_dtype=False)

    # The function applies unit conversion: p = pp*env.power_unit
    # So, original_power_values should be scaled by the magnitude of env.power_unit if it's not dimensionless.
    # If env.power_unit is just for labelling and doesn't change scale, this is simpler.
    # Given `p = pp*env.power_unit`, it implies multiplication.
    # If env.power_unit = u.Unit("ppm2/uHz"), its value is 1. So no change in magnitude.
    expected_power_in_env_units_value = (original_power_values * Environment.power_unit).value
    pd.testing.assert_series_equal(result_df['psd'], pd.Series(expected_power_in_env_units_value), check_dtype=False)


    mock_fits_open.assert_called_once_with("dummy.fits")
    actual_calls = mock_loadtxt.call_args_list
    assert actual_calls[0][0][0] == "dummy_bkg.txt"
    assert actual_calls[1][0][0] == "dummy_pkb.txt"
    
    # Check if create_synthetic_psd was called with frequency in Environment.frequency_unit
    call_args_apn = mock_create_psd.call_args[0]
    called_freq_arg_apn = call_args_apn[0] 
    assert np.allclose(called_freq_arg_apn, expected_freq_in_env_units)
    assert np.array_equal(call_args_apn[1], mock_pkb_array) # pkb
    assert np.array_equal(call_args_apn[2], mock_param_back_full[:,0]) # param_back (after [:,0])
    assert call_args_apn[4] == 2 # n_harvey
    assert mock_create_psd.call_args[1]['noise_free'] is True # Check kwargs


@patch('iechelle.gui.functions.fits.open', side_effect=FileNotFoundError("Mocked File Not Found"))
def test_calculate_synthetic_spectrum_fits_file_not_found(mock_fits_open, test_env):
    with pytest.raises(FileNotFoundError, match="Mocked File Not Found"):
        calculate_synthetic_spectrum(
            fits_file="non_existent.fits",
            bkg_file="dummy_bkg.txt",
            pkb_file="dummy_pkb.txt"
        )
    mock_fits_open.assert_called_once_with("non_existent.fits")


@patch('iechelle.gui.functions.fits.open') # Let fits.open succeed
@patch('iechelle.gui.functions.np.loadtxt', side_effect=FileNotFoundError("Mocked BKG Not Found"))
def test_calculate_synthetic_spectrum_bkg_file_not_found(mock_loadtxt, mock_fits_open, test_env):
    # Setup mock for fits.open to behave normally for this test
    freq_data = np.array([10, 20, 30], dtype='>f8')
    power_data = np.array([1, 2, 3], dtype='>f8')
    mock_fits_records = np.core.records.fromarrays([freq_data, power_data], names='0,1')
    mock_fits_hdu = fits.BinTableHDU.from_columns(fits.ColDefs(mock_fits_records))
    mock_hdulist_obj = fits.HDUList([mock_fits_hdu])
    mock_fits_open.return_value.__enter__.return_value = mock_hdulist_obj
    
    with pytest.raises(FileNotFoundError, match="Mocked BKG Not Found"):
        calculate_synthetic_spectrum(
            fits_file="dummy.fits",
            bkg_file="non_existent_bkg.txt",
            pkb_file="dummy_pkb.txt"
        )
    # np.loadtxt is called first for bkg_file
    mock_loadtxt.assert_called_once_with("non_existent_bkg.txt")


@patch('iechelle.gui.functions.fits.open') # Let fits.open succeed
@patch('iechelle.gui.functions.np.loadtxt') # Let first np.loadtxt (bkg) succeed
@patch('iechelle.gui.functions.apn.synthetic.create_synthetic_psd') # Mock this to prevent its execution
def test_calculate_synthetic_spectrum_pkb_file_not_found(mock_create_psd, mock_loadtxt, mock_fits_open, test_env):
    # Setup mock for fits.open
    freq_data = np.array([10, 20, 30], dtype='>f8')
    power_data = np.array([1, 2, 3], dtype='>f8')
    mock_fits_records = np.core.records.fromarrays([freq_data, power_data], names='0,1')
    mock_fits_hdu = fits.BinTableHDU.from_columns(fits.ColDefs(mock_fits_records))
    mock_hdulist_obj = fits.HDUList([mock_fits_hdu])
    mock_fits_open.return_value.__enter__.return_value = mock_hdulist_obj

    # Mock np.loadtxt: first call (bkg) returns normally, second call (pkb) raises FileNotFoundError
    mock_param_back_full = np.array([[0.1, 99], [0.2, 99]])
    mock_loadtxt.side_effect = [
        mock_param_back_full, # Successful return for bkg_file
        FileNotFoundError("Mocked PKB Not Found") # Error for pkb_file
    ]

    with pytest.raises(FileNotFoundError, match="Mocked PKB Not Found"):
        calculate_synthetic_spectrum(
            fits_file="dummy.fits",
            bkg_file="dummy_bkg.txt",
            pkb_file="non_existent_pkb.txt"
        )
    
    assert mock_loadtxt.call_count == 2
    actual_calls = mock_loadtxt.call_args_list
    assert actual_calls[0][0][0] == "dummy_bkg.txt"
    assert actual_calls[1][0][0] == "non_existent_pkb.txt"
```
