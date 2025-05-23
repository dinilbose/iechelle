from astropy import units as u

"""
Defines the Environment class, a central repository for shared application state.

This module provides the `Environment` class, which is instantiated and used
by various components of the iEchelle application to share data, Bokeh
ColumnDataSources, figure handles, UI element states, and global parameters.
This avoids the need to pass around numerous objects or rely on global
variables in a less structured way.
"""


class Environment(object):
    """
    Central repository for shared application state, data, and Bokeh objects.

    This class acts as a namespace to store and share various pieces of
    information and Bokeh model instances across different modules of the
    iEchelle GUI. Attributes are typically initialized to None or default
    values and then populated or modified by different parts of the application
    as it runs.

    Key categories of attributes include:
    - Bokeh ColumnDataSources for tables and plots.
    - Handles to Bokeh figures.
    - UI element states (e.g., selected values, text inputs).
    - Parameters for astrophysical calculations (e.g., dnu, frequency ranges).
    - Configuration settings (e.g., default color palettes, plot dimensions).
    """
    # ---------------------------Light Curve Param----------------------------- #
    # These parameters seem related to light curve processing and display,
    # possibly from a previous or related project context (e.g., "light_cluster").

    default_cluster = "mode_selection"  # Default view or mode for the application
    sigma = 5
    plot_nearby = -1  # set this to 1 and -1 to toggle plotting of nearby source
    draw_nearby_names = 1

    selection_program = None
    text_custom_star_ra = None
    text_custom_star_dec = None
    text_custom_star_sector = None
    custom_star_download_button = None
    selection_program_text = None

    text_banner = None

    v_flag_duplicate = None
    v_flag_source = None
    v_flag_check = None

    text_flag_duplicate = None
    text_flag_source = None
    text_flag_check = None

    text_catalog_query = None
    text_id_mycatalog_query = None
    text_id_query = None
    text_Notes = None
    text_Notes_w = None

    show_error_bar = None

    aperture_setting = 1  # 1 current and -1 default

    # extra_flag_file='/home/dinilbose/PycharmProjects/light_cluster/cluster/Collinder_69/Data/extra_flag.flag'
    extra_flag_file = 'extra_flag.flag'

    current_flux_dataframe = None
    # ----------------------------Source Table--------------------------------- #
    # Bokeh ColumnDataSources and table objects for various data displays

    tb_source = 2  # Likely a ColumnDataSource for main source catalog
    tb_lightcurve = None  # CDS for light curve data
    tb_periodogram = None  # CDS for periodogram data
    tb_tpf = None  # CDS for Target Pixel File data
    tpf_flux = None  # Flux data from TPF
    table_periodogram = None  # Bokeh DataTable widget for periodogram
    tb_periodogram_se_tb = None  # CDS for periodogram in mode selection tab
    tb_nearby = None  # CDS for nearby objects
    tb_catalog_main = None  # CDS for the main astronomical catalog
    tb_catalog_all = None  # CDS for a broader catalog view
    tb_isochrone = None  # CDS for isochrone data
    tb_nearby_star = None  # CDS for nearby stars, possibly for plotting
    tb_nearby_star_table = None  # DataTable for nearby stars

    # Figure handles for catalog-related plots
    fig_hr = None  # HR diagram figure
    fig_position = None  # Sky position plot

    # UI elements for isochrone parameters
    text_age = None  # Input for age
    text_metallicity = None  # Input for metallicity
    text_extinction_av = None  # Input for extinction (Av)
    text_distance = None  # Input for distance
    generate_isochrone_button = None  # Button to generate isochrones
    delete_isochrone_button = None  # Button to delete isochrones
    int_select_sector = None  # Input/selector for TESS/Kepler sector
    sector = 6  # Default sector
    # ----------------------------Figures ------------------------------------ #
    # General plot styling and Bokeh figure handles
    plot_width = 810  # Default width for plots
    plot_height = 300  # Default height for plots
    fiducial_frame = 0 # Reference frame for TPF visualization

    # Styling for selected/unselected glyphs in Bokeh plots
    selection = {'selection_color': "black",
                 'nonselection_fill_alpha': 0.7,
                 'nonselection_fill_color': "grey",
                 'selection_fill_alpha': 1
                 }
    selection_osc = {'line_color': "green",  # Styling for oscillation mode selections
                     'nonselection_line_color': "#1F77B4", 'nonselection_line_alpha': 1}

    selection_l = {'line_color': "#1F77B4",  # Another selection styling variant
                   'nonselection_line_color': "#1F77B4", 'nonselection_line_alpha': 1}

    selection_2 = {'selection_color': "red",  # Yet another selection styling
                   'nonselection_fill_color': "blue",
                   'nonselection_line_color': "blue",
                   'nonselection_line_alpha': 0.7}

    TOOLTIPS = [  # Default tooltips for Bokeh plots
        ("index", "$index"),
        ("(x,y)", "($x, $y)"),
    ]

    # Specific figure handles
    fig_lightcurve = None  # Light curve plot
    fig_tpf = None  # Target Pixel File plot
    fig_stretch = None  # Plot related to color stretch (e.g., for TPF or echelle)
    fig_periodogram = None  # Main periodogram plot
    # --------------------------- Button -------------------------------------#
    # Bokeh Button widgets

    Generate_lc_button = None  # Button to generate light curve
    reset_axis_lc_button = None  # Button to reset light curve axes
    reset_dflt_lc_button = None  # Button to reset light curve to default view

    next_button = None  # Navigation: next item
    previous_button = None  # Navigation: previous item

    # Buttons related to periodogram table management
    reset_axes_prd_button = None  # Reset periodogram axes
    saveas_prd_tb_button = None  # "Save As" for periodogram table
    save_prd_tb_button = None  # "Save" for periodogram table
    reset_prd_tb_button = None  # "Reset" periodogram table
    load_prd_tb_button = None  # "Load" periodogram table
    save_userinput_button = None # Button to save user inputs
    save_current_button = None # Button to save current selections/state
    aperture_selection_button = None # Button for aperture selection
    update_catalog_button = None # Button to update main catalog
    update_id_mycatalog_button = None # Button to update user's catalog
    update_id_button = None # Button to update ID

    # Spinner/loading indicator elements
    div_spinner = None  # Bokeh Div to show a loading spinner
    show_spinner_button = None  # Button to manually show spinner (debug?)

    spinner_text = """  # HTML/CSS for the loading spinner
    <!-- https://www.w3schools.com/howto/howto_css_loader.asp -->
    <div class="loader">
    <style scoped>
    .loader {
        border: 16px solid #f3f3f3; /* Light grey */
        border-top: 16px solid #3498db; /* Blue */
        border-radius: 50%;
        width: 120px;
        height: 120px;
        animation: spin 2s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    </div>
    """

    from bokeh.models.widgets import Div
    div_spinner = Div(text="", width=120, height=120) # Instantiation of the spinner Div


#  Analysis Window - Elements for a comparative analysis view
    # These seem to be for a side-by-side or comparative analysis of two datasets/stars

    tb_lc_an1 = None  # CDS for light curve 1 in analysis view
    tb_lc_an2 = None  # CDS for light curve 2 in analysis view
    fig_lc_an1 = None  # Figure for light curve 1
    fig_lc_an2 = None  # Figure for light curve 2
    fig_pr_an1 = None  # Figure for periodogram 1
    fig_pr_an2 = None  # Figure for periodogram 2

    tb_pr_an1 = None  # CDS for periodogram 1
    tb_pr_an2 = None  # CDS for periodogram 2
    # fig_pr_an1 and fig_pr_an2 are already declared above, likely a typo here.

    # Text inputs for period analysis
    text_p1 = None  # Period 1
    text_p0 = None  # Period 0 (reference?)
    text_p2 = None  # Period 2
    text_pe = None  # Period error?

    period_recompute_button = None  # Button to recompute period
    fold_button = None  # Button to fold light curve
    check_analysis = None  # Checkbox to enable/disable analysis view?


# Control Panel - General application controls and catalog settings

    Samp_status = 0  # Status for sampling/data source (0 might mean local)
    Samp_selection = 'Server'  # Data source selection (e.g., 'Server', 'Local')
    Control_function = 'None'  # Current control function active
    catalog_main = ''  # Path or name of the main catalog
    catalog_whole_gaia = None  # CDS for the entire Gaia catalog (potentially large)
    ds9_command_button = None  # Button to send commands to DS9
    ds9_catalog_status = None  # Status of DS9 connection/catalog display
    # Gaia catalog query parameters
    gaia_Gmag_start = None  # Gaia G-magnitude start range
    gaia_Gmag_end = None  # Gaia G-magnitude end range
    whole_gaia_filter = None  # Filter applied to the Gaia catalog

    gaia_Gmag_start_text = None  # Text input for Gaia G-mag start
    gaia_Gmag_end_text = None  # Text input for Gaia G-mag end
    gaia_update_button = None  # Button to update Gaia catalog query
    gaia_radius_text = None  # Text input for Gaia query radius
    isochrone_data = None  # Data store for isochrones
    catalog_find_from_isocrhone = None # Button or mechanism to select stars from isochrone

    # Banner texts for displaying information
    text_banner_Gmag = None
    text_banner_bp_rp = None
    text_banner_dmin = None

    # Parameters for interactive echelle diagram and mode selection (asteroseismology)
    fig_tpfint = None         # Figure for the interactive echelle diagram (likely misnamed, should be fig_echelle_int)
    stretch_sliderint = None  # Slider for echelle diagram color stretch
    dnu_slider = None         # Slider for delta Nu (large frequency separation) value
    r_button = None           # Button for incrementing dnu
    l_button = None           # Button for decrementing dnu
    rr_button = None          # Button for large increment dnu
    ll_button = None          # Button for large decrement dnu

    minimum_frequency = None  # Min frequency for echelle/periodogram display
    maximum_frequency = None  # Max frequency for echelle/periodogram display
    maxdnu = None             # Max dnu value for the dnu_slider
    dnu_val = None            # Current dnu value being used

    # Text inputs for frequency and dnu parameters
    minimum_frequency_text = None
    maximum_frequency_text = None
    maxdnu_text = None        # Text input for max Dnu
    dnu_text = None           # Text input for current Dnu

    update_int_button = None # Button to update interactive plots (echelle/periodogram)

    # MESA oscillation model data and UI elements
    mesa_osc_data = None      # Data from MESA oscillation models
    fig_mesa_int = None       # Figure for interactive MESA model comparison
    mesa_int_slider = None    # Slider for MESA model parameters (e.g., age, mass)
    # ColumnDataSources for MESA oscillation modes (l=0, 1, 2)
    tb_mesa_osc_l0 = None
    tb_mesa_osc_l1 = None
    tb_mesa_osc_l2 = None

    # Input selectors for MESA model parameters
    int_select_mass = None
    int_select_y = None       # Initial Helium fraction?
    int_select_age = None
    int_select_z = None       # Metallicity for MESA model
    int_select_alpha = None   # Mixing length parameter?

    comp_data = None # Data for comparison (e.g. with models)

    interactive_file_control = -1 # Flag or control for interactive file loading/status

    # Source-specific interactive controls (possibly for refining parameters for a single star)
    source_int_slider = None
    frequency_minimum_text1 = None # Min frequency for source-specific view
    frequency_maximum_text1 = None # Max frequency for source-specific view
    frequency_maxdnu_text1 = None  # Max Dnu for source-specific view
    update_int_source_button = None # Button to update source-specific interactive plot

    set_value_dict = None # Dictionary to store set values or parameters

    # ColumnDataSources for theoretical oscillation models (l=0, 1, 2) - separate from MESA?
    tb_oscillation_modell0 = None
    tb_oscillation_modell1 = None
    tb_oscillation_modell2 = None
    plot_mesa_osc = None      # Plot object for MESA oscillations
    text_osc_query = None     # Text input for querying oscillation data


# for new model_selection (asteroseismology focused)
    # These are primary elements for the echelle diagram and mode selection tab
    tb_other_periodogram = None # CDS for the main periodogram in the mode selection tab
    fig_other_periodogram = None# Figure for the main periodogram
    tb_grid_source = None       # CDS for the echelle diagram grid points
    table_se_first = None     # CDS for the first mode selection table (e.g. temporary picks)
    table_se_second = None    # CDS for the second mode selection table (e.g. final list)
    test_button = None          # Generic test button
    freq_round = 10             # Decimal places for rounding frequency values
    tb_echelle_diagram = None   # Figure object for the echelle diagram
    # Units for frequency and power, using astropy.units
    frequency_unit_string = 'uHz'
    frequency_unit = u.Unit(frequency_unit_string)
    power_unit_string = 'u.electron/u.s' # Example power unit
    power_unit = u.Unit(power_unit_string)

 #  Buttons and controls for mode selection tab
    clear_se_table1_button = None # Button to clear the first selection table
    find_peaks_button = None      # Button to trigger peak finding algorithm
    echelle_noise_cuttoff_text = None # Text input for echelle diagram noise cutoff
    clear_se_grid_prd_button = None # Button to clear periodogram used for echelle grid
    select_mode_menu = None       # Dropdown/select menu for mode identification (l=0,1,2,3 etc.)
    mode_apply_button = None      # Button to apply selected mode properties
    move_se_1_2_button = None     # Button to move selected modes from table 1 to table 2
    move_se_2_1_button = None     # Button to move selected modes from table 2 to table 1
    tb_other_source = None        # CDS for additional source data in mode selection
    save_table_2_button = None    # Button to save the second (final) mode list
    load_table_2_button = None    # Button to load a mode list into the second table
    inverted_slider = None        # Slider for echelle diagram y-axis inversion or stretch
    select_color_palette = None   # Dropdown to select echelle diagram color palette
    grid_circle_size = None       # Input for size of circles on echelle diagram
    clear_se_table2_button = None # Button to clear the second selection table
    # Checkboxes for various plot options
    check_color_map_lock = None   # Lock/unlock echelle color map scaling
    check_periodogram_axis_scale = None # Toggle periodogram axis scale (log/linear)
    check_show_horizontal_lines = None # Show horizontal lines (e.g. for l values) on echelle
    check_make_grid  = None       # Toggle calculation/display of echelle grid
    check_show_echelle = None     # Toggle visibility of the echelle diagram itself
    check_show_modes_grid = None  # Toggle visibility of identified modes on the echelle grid
    check_reverse_color_palette = None # Reverse the selected color palette
    inverted_slider_max_value_text = None # Text input for max value of inverted_slider
    default_color_palette = "Greys" # Default color palette for echelle
    # List of available Bokeh color palettes
    color_palette_options = [
        "Spectral", "RdBu", "PiYG", "PRGn", "RdYlBu", "RdGy", "PuOr",
        "Greens", "Blues", "Purples", "Oranges", "Reds", "Greys",
        "YlOrBr", "YlGnBu", "YlGn", "Plasma", "Magma", "Inferno", "Viridis", "Cividis",
        "Greys256", "Inferno256", "Magma256", "Plasma256", "Viridis256", "Cividis256", "Turbo256",
    ]

    # Column names for peak-bagging files (.pkb)
    pkb_columns=['n', 'l', 'nu', 'e_nu', 'h', 'e_h', 'w', 'e_w', 'a', 'e_a', 's', 'e_s', 'asym', 'e_asym']
    pkb_columns_extended = [  # Extended column names for peak-bagging files, allowing for asymmetric errors
                                'n', 'l', 'nu', 'err_nu_minus', 'err_nu_plus',
                                'height', 'err_height_minus', 'err_height_plus',
                                'width', 'err_width_minus', 'err_width_plus',
                                'angle', 'err_angle_minus', 'err_angle_plus',
                                'split', 'err_split_minus', 'err_split_plus',
                                'asym', 'err_asym_minus', 'err_asym_plus'
                            ]


    # New buttons for file and catalog interactions (likely in the mode selection/file loading part)
    button_type = "primary"  # Default Bokeh button styling
    selected_filename_text = None # Displays name of selected generic file (deprecated by specific ones below?)
    open_folder_button = None     # Button to open a folder dialog
    open_file_button = None       # Button to open a generic file dialog
    open_catalog_button = None    # Button to open a catalog file

    # Buttons for saving/loading mode lists (.pkb files) and background parameters
    save_as_table_2_button = None                # "Save As" for the final mode list table
    load_from_file_table_2_button = None         # "Load" mode list from a chosen .pkb file
    load_from_specific_file_table_2_button = None # "Load" mode list from a pre-defined/specific file path
    load_bkg_param_from_file_button = None       # Button to load background parameters for synthetic spectrum

    # UI elements for controlling inverted lines on echelle diagram (e.g., for ridges)
    inverted_line_initial_y_text = None # Text input for initial y value of an inverted line
    inverted_line_length_text = None    # Text input for length of the line
    inverted_line_scale_text = None     # Text input for scale factor of the line
    inverted_line_xvalue_text = None    # Text input for x-value (frequency mod dnu) of the line
    inverted_line_update_button = None  # Button to update/draw the inverted line
    check_show_inverted_lines = None    # Checkbox to toggle visibility of these lines
    Message = None                      # For displaying status messages to the user (general purpose)
    message_banner = None               # A more prominent banner for messages
    # Text displays for filenames of loaded data
    selected_filename_background_text = None # Displays name of loaded background parameter file
    selected_filename_pkb_text = None        # Displays name of loaded peak-bagging file
    selected_filename_fits_text = None       # Displays name of loaded FITS periodogram file
    calculate_synthetic_psd_button = None    # Button to trigger synthetic Power Spectral Density calculation
    # For plotting generic data or results
    tb_plot = None      # CDS for a generic plot
    table_plot = None   # DataTable for a generic plot
    select_grid_menu = None # Menu for selecting different grid configurations or types
    show_plot = None    # Button or check to show/hide a generic plot
    # selected_filename = None # Deprecated/Duplicate
    # selected_filename = None # Deprecated/Duplicate





    # update_all=None # Seems to be a placeholder or commented-out feature
    # from bokeh.models.widgets import  Div # Import already done at the top of the class for div_spinner
    # self.env.div_spinner = Div(text="",width=120,height=120) # Instantiation already done
    # Commented out spinner functions, likely handled elsewhere or part of an earlier design
    # def show_spinner():
    #     self.env.div_spinner.text = self.env.spinner_text
    # def hide_spinner():
    #     self.env.div_spinner.text = ""
    # self.env.show_spinner_button = Button(label='Show Spinner', width=100)
    # self.env.show_spinner_button.on_click(show_spinner)

    # The following attributes seem to be from a different application/template
    # and might not be actively used in iEchelle, or are placeholders.
    # doc = None                      # pointer to curdoc()
    # ly = None                       # main bokeh layout
    #
    # bridge_row = None               # messages bridge row to add to the layout
    # tabs = None                     # tabs structure
    # cur_plotted_cols = []           # Current columns list used in all the plots
    #
    # sidebar = None                  # sidebar, actually it is a column
    # tabs_widget = None              # tabs widget
    # flagger_select = None           # flag selection widget
    # wmts_map = None                 # tile server map
    # wmts_map_scatter = None         # scatter for the tile server map
    # flags_control_col = None        # flags control column (visibility and flag updates)
    # show_titles = False             # Whether show titles on plots or not
