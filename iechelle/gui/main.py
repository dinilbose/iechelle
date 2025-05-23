"""
Main entry point for the iEchelle Bokeh server application.

This script initializes the different UI components from other modules
(Catalog, Environment, Interactive), arranges them into a layout using
Bokeh layout functions (row, column, Tabs, TabPanel), and adds the
root layout to the current document (`curdoc()`) to be served by Bokeh.
"""
import sys
# Import Bokeh layout and model objects
from bokeh.layouts import row, column
# from bokeh.layouts import grid # grid is not used, can be removed
from bokeh.plotting import curdoc, figure, show # figure and show are not used, can be removed
# from bokeh.models import Panel # Panel is not used
import pandas # pandas is not directly used in this file, but might be by imported modules
# from bokeh.models import Button  # for saving data # Button is not directly used
# from bokeh.models.widgets import Tabs # Tabs is imported from bokeh.models.layouts
# from bokeh.layouts import layout, Spacer # layout and Spacer are not used
from bokeh.models import Div

from bokeh.models.layouts import TabPanel, Tabs

# Import custom GUI components
from catalog import Catalog
from env import Environment
from mode_selection import Interactive

# Instantiate the environment, catalog, and interactive mode selection components
# These objects will hold shared data and UI elements.
env = Environment
Environment()  # Instantiates and likely registers shared elements within the Environment class itself
Catalog()      # Instantiates and sets up catalog-related UI and logic
Interactive()  # Instantiates and sets up interactive analysis UI and logic

# --- Interactive Tab Layout ---
# This section defines the layout for the main interactive analysis tab.

# Next/Previous buttons for source navigation in the interactive tab
# Note: env.next_button and env.previous_button are used in multiple places.
# This specific instance is for the echelle diagram interaction area.
nxt_prv_button = row(env.next_button, env.previous_button, sizing_mode='fixed')

# Column for echelle diagram interaction controls
tab_int_1 = column(
    # This `nxt_prv_button` seems commented out, perhaps was moved or decided against here.
    # nxt_prv_button,
    # Column containing the echelle diagram and its direct controls
    column(row(env.stretch_sliderint, env.check_color_map_lock), # Row for echelle stretch slider and color map lock
           env.fig_tpfint,  # The interactive echelle diagram figure
           ),
    # Row for dnu slider and navigation buttons
    row(env.ll_button,  # Dnu large decrement
        env.l_button,   # Dnu small decrement
        env.dnu_slider, # Delta Nu slider
        env.r_button,   # Dnu small increment
        env.rr_button), # Dnu large increment
    # Row for frequency range and dnu text inputs
    row(env.frequency_minimum_text,
        env.frequency_maximum_text,
        env.frequency_maxdnu_text,
        env.dnu_text,
        env.echelle_noise_cuttoff_text), # Threshold input for echelle grid
    # Row for update button, next/prev source, color palette, and echelle display options
    row(env.update_int_button, # Button to update plots based on text inputs
        nxt_prv_button,        # Re-use of next/previous source buttons for this section
        env.select_color_palette, # Dropdown for echelle color palette
        env.check_reverse_color_palette), # Checkbox to reverse palette
    # Row for grid display options related to the echelle diagram
    row(env.select_grid_menu,       # Dropdown to select which data to grid (Obs, Syn, Sub)
        env.check_make_grid,        # Checkbox to enable/disable echelle grid calculation
        env.check_show_modes_grid,  # Checkbox to show only identified modes on the echelle grid
        env.check_show_echelle,     # Checkbox to show/hide the echelle diagram image itself
        env.grid_circle_size,       # Input for echelle grid marker size
        env.check_show_horizontal_lines, # Checkbox for horizontal lines (e.g. l=0,1,2) on periodogram
        )
)

# Final layout for the interactive echelle diagram and its controls
tab_interactive_layout = column(row(tab_int_1)) # Encapsulating in a row then column might be for specific spacing/alignment

# --- Catalog and Main Controls Layout (layout_catalog) ---
# This section assembles the primary layout which includes file operations,
# the interactive echelle/periodogram components, and mode selection tables.

# Buttons for next/previous source. This seems to be a general navigation control,
# potentially distinct from the one in tab_int_1 or a re-instantiation.
# The multiple layers (next_lay1, next_dflt_lay, layer_1) seem redundant and could likely be simplified
# to just `next_lay1` or `column(row(env.previous_button, env.next_button))` if no other elements are added.
# For now, commenting based on current structure.
next_lay1 = row(env.previous_button,
                env.next_button)
next_dflt_lay = column(next_lay1) # Wrapping a single row in a column
layer_1 = column(next_dflt_lay) # Wrapping a single column in another column

# Main layout for the application tab
layout_catalog = column(
    # File selection for main FITS data (observed periodogram)
    row(
        env.open_file_button, # Button to trigger file dialog for FITS
        env.selected_filename_text, # Displays selected FITS file path
    ),
    # File selection for background parameters
    row(
        env.load_bkg_param_from_file_button, # Button to load background model file
        env.selected_filename_background_text, # Displays selected background file path
    ),
    # File selection for peak-bagging (PKB) parameters
    row(
        env.load_from_specific_file_table_2_button, # Button to load PKB file for table 2
        env.selected_filename_pkb_text,          # Displays selected PKB file path
    ),
    env.message_banner, # Banner for status messages and current source ID
    # Main row containing the interactive echelle/periodogram and mode selection tables/controls
    row(
        tab_interactive_layout, # Embed the interactive echelle components defined earlier
        # Column for the main periodogram and mode selection tables
        column(
            env.fig_other_periodogram, # The main periodogram figure
            # Controls for inverted lines on the periodogram (often for model ridge comparison)
            row(
                #env.check_periodogram_axis_scale, # Checkbox for log/linear scale on periodogram (commented out)
                env.inverted_slider, # Slider to adjust x-position of inverted lines
                env.inverted_line_initial_y_text, # Input for initial y of inverted line
                env.inverted_line_length_text, # Input for length of inverted line
                env.inverted_line_scale_text, # Input for scaling factor of inverted line
                env.inverted_line_xvalue_text, # Input for x-value (offset) of inverted line
                env.inverted_slider_max_value_text, # Input for max value of inverted_slider
                env.check_show_inverted_lines, # Checkbox to show/hide these lines
                env.inverted_line_update_button, # Button to apply inverted line changes
            ),
            # Mode selection tables and their respective controls
            row(
                # Column for Table 1 (initial/temporary mode selections)
                column(
                        Div(text="<h2 style='text-align: center;'> Table 1 / Selection </h2>", width=500), # Title for Table 1
                        env.table_se_first, # Bokeh DataTable for temporary selections
                        ),
                # Column for buttons interacting with Table 1 and moving modes between tables
                column(
                    Div(text="",width=150,height=100), # Spacer Div
                    env.test_button, # "Get Selection" - populates Table 1 from plot selections
                    env.find_peaks_button, # Finds peaks in selected echelle regions for Table 1
                    env.clear_se_table1_button, # Clears Table 1
                    env.clear_se_grid_prd_button, # Clears selections on periodogram and echelle grid
                    env.select_mode_menu, # Dropdown to assign mode type (l-value)
                    env.mode_apply_button, # Button to apply selected mode type to Table 1 entries
                    env.move_se_1_2_button, # Button to move selected modes from Table 1 to Table 2
                    env.move_se_2_1_button, # Button to move selected modes from Table 2 to Table 1
                ),
                # Column for Table 2 (final/saved mode selections)
                column(
                        Div(text="<h2 style='text-align: center;'> Table 2 / Saving", width=500), # Title for Table 2
                        env.table_se_second, # Bokeh DataTable for final selections
                        ),
                # Column for buttons related to saving/loading Table 2 (PKB files) and synthetic spectra
                column(
                    Div(text="",width=150,height=100), # Spacer Div
                    env.load_table_2_button, # Load from default PKB file to Table 2
                    env.save_table_2_button, # Save Table 2 to default PKB file
                    env.load_from_specific_file_table_2_button, # Load from user-chosen PKB to Table 2 (also sets pkb_text)
                    env.save_as_table_2_button, # Save Table 2 to user-chosen PKB file
                    env.clear_se_table2_button, # Clears Table 2
                    env.calculate_synthetic_psd_button, # Button to calculate and plot synthetic spectrum
                ),
            ),
        ),
        # Column for the plot selection table and its controls
        column(env.table_plot, # Table listing available plots/overlays (Obs, Syn, Sub)
               env.show_plot,  # Button to show/hide plots selected in table_plot
               env.calculate_synthetic_psd_button, # Appears to be a duplicate of the one near Table 2, or for a different context.
               ),
    ),
    # Commented out section, possibly for displaying file paths again or for debugging
    # column(
    #     Div(text="<h2 style='text-align: center;'> FITS:", width=500),env.selected_filename_text,
    #     env.selected_filename_pkb_text,
    #     env.selected_filename_background_text,
    # ),
    sizing_mode="stretch_both",  # Adjusts sizing of the main layout_catalog
    css_classes=["centered-column"], # Custom CSS class (if defined in HTML template)
)

# layout_catalog = env.stretch_sliderint # This line is commented out, would replace entire layout with just a slider if active.

# --- Setup Tabs ---
# Create a tab panel for the main "Mode Selection" view
tab_c = TabPanel(child=layout_catalog, title='Mode Selection')
tabs = Tabs(tabs=[tab_c]) # Create the main tab container, currently with one tab

# Add the root layout to the document and set the browser tab title
curdoc().add_root(tabs)
