"""
Defines the Interactive class, the core of iEchelle's interactive analysis functionality.

This module provides the `Interactive` class, which manages the primary user
interface for echelle diagram and periodogram analysis. It handles user inputs,
updates Bokeh plots and tables, performs calculations related to seismic mode
identification, and interacts extensively with the shared `Environment` class.
It leverages Bokeh for plotting, Astropy for units, Lightkurve for
periodogram objects, and Apollinaire for some astrophysical calculations
and echelle diagram logic.
"""
import logging
import pandas as pd
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
# from scipy.signal import find_peaks
from bokeh.models import ColumnDataSource
import functions
from astropy import units as u
# from astropy.units import cds

# from lightkurve import MPLSTYLE
# from lightkurve.seismology import utils, stellar_estimators
# from lightkurve.periodogram import SNRPeriodogram
# from lightkurve.utils import LightkurveWarning
from lightkurve.seismology import SeismologyQuantity
import apollinaire as apol

# from astropy import units
# from tessipack.functions import maths
# from tessipack.functions import io
#from iechelle import mycatalog

#import lightkurve
#import Periodo
from env import Environment
#from astropy import units
from bokeh.models import CustomJS, TextInput, Paragraph
# for saving data
from bokeh.models import Button, Select, CategoricalColorMapper, CheckboxGroup, TableColumn, DataTable
from lightkurve import periodogram as lk_prd_module

# Import the optional Bokeh dependency required by ``interact_echelle```,
# or print a friendly error otherwise.
# try:
import bokeh  # Import bokeh first so we get an ImportError we can catch
    # from bokeh.io import show, output_notebook
from bokeh.plotting import figure
from bokeh.models import LogColorMapper, Slider, RangeSlider, Button
    # from bokeh.layouts import layout, Spacer
# except:
    # Nice error will be raised when ``interact_echelle``` is called.
    # pass
# from bokeh.colors import RGB
import bokeh.palettes

log = logging.getLogger(__name__)

from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfilename
    

class Interactive(Environment):
    """
    Manages the interactive echelle diagram and periodogram analysis GUI.

    This class is responsible for:
    - Initializing and updating the main periodogram and echelle diagram plots.
    - Handling user interactions with UI elements (sliders, buttons, tables, text inputs).
    - Managing Bokeh ColumnDataSources that back the interactive plots and tables.
    - Reading and processing FITS files to obtain frequency and power data.
    - Implementing the logic for mode identification, selection, and display.
    - Facilitating the saving and loading of mode parameters (PKB files).
    - Calculating and displaying synthetic power spectra.
    - Interacting with the `apollinaire` library for echelle diagram generation
      and other astrophysical computations.
    - Using `tkinter` for file dialogs.

    It inherits from the `Environment` class to access and modify shared application
    state and Bokeh models.
    """
    env = Environment

    def __init__(self):
        """
        Initializes the interactive mode selection GUI components and callbacks.

        Sets up various UI elements including text inputs for frequency ranges,
        delta Nu, noise cutoff, buttons for plot updates, mode selection,
        and table operations. Initializes Bokeh ColumnDataSources for periodograms,
        echelle diagrams, and mode selection tables. Creates the main echelle
        diagram figure and periodogram figure. Sets up numerous callbacks for
        UI interactions and data changes.
        Initializes plot for vertical lines representing selected modes.
        """

        self.mode_color_map = {
                    '999': "grey",
                    '0': "red",
                    '1': "magenta",
                    '2': "blue",
                    '3': "green",
                    }

        self.tb_constants_val = ColumnDataSource(
            data=dict(
                other_prd_cuttoff=list([500]),
                minimum_frequency=list([0])
            )
        )

        self.mode_shape_selection = 'circle'
        self.id_mycatalog = self.env.tb_source.data['id_mycatalog'][0]
        #self.palette = "hot"

        self.env.text_osc_query = TextInput(
            value='n_pg>=0', title="Select Cluster")

        self.env.tb_other_periodogram, self.env.fig_other_periodogram = self.initialize_dnu_periodogram()
        self.env.frequency_minimum_text = TextInput(
            value=str(self.env.minimum_frequency), title="Freq min", width=80)
        self.env.frequency_maximum_text = TextInput(
            value=str(self.env.maximum_frequency), title="Freq max", width=80)
        self.env.frequency_maxdnu_text = TextInput(
            value=str(self.env.maxdnu), title="Maxdnu", width=80)
        self.env.echelle_noise_cuttoff_text = TextInput(
            value=str(0), title="Threshold", width=80)

        self.env.dnu_text = TextInput(
            value=str(self.env.dnu_val), title="Delta Nu", width=100)
        self.env.update_int_button = Button(
            label="Update Plot", button_type=self.env.button_type, width=150)
        self.env.update_int_button.on_click(self.update_value)
        
        self.env.select_mode_menu = Select(title='Mode Select', 
                                         options=['999','0','1','2','3','4','-1','-2'], 
                                         value='999',width=150)
        self.env.mode_apply_button = Button(
                                        label="Select Mode", 
                                        button_type=self.env.button_type, width=150)
        self.env.mode_apply_button.on_click(self.click_mode_apply_button)

        self.env.move_se_1_2_button = Button(
                                        label="Move Tab1 -> Tab2", 
                                        button_type=self.env.button_type, width=150)
        self.env.move_se_1_2_button.on_click(self.click_move_se_1_2_button)
        self.env.move_se_2_1_button = Button(
                                        label="Move Tab2 -> Tab1", 
                                        button_type=self.env.button_type, width=150)
        self.env.move_se_2_1_button.on_click(self.click_move_se_2_1_button)

        self.env.save_table_2_button = Button(
                                        label="Save Tab2", 
                                        button_type=self.env.button_type, width=150)
        self.env.save_table_2_button.on_click(self.save_table_2)

        self.env.load_table_2_button = Button(
                                        label="Load PKB from default file", 
                                        button_type=self.env.button_type, width=150)
        self.env.load_table_2_button.on_click(self.load_table_2)


        self.env.save_as_table_2_button = Button(
                                        label="Save Tab 2 as", 
                                        button_type=self.env.button_type, width=150)
        self.env.save_as_table_2_button.on_click(self.save_as_table_2)

        self.env.load_from_specific_file_table_2_button  = Button(
                                        label="Load PKB from specific file", 
                                        button_type=self.env.button_type, width=150)
        self.env.load_from_specific_file_table_2_button.on_click(self.load_from_file)

        self.env.load_bkg_param_from_file_button  = Button(
                                        label="Load BKG from specific file", 
                                        button_type=self.env.button_type, width=150)
        self.env.load_bkg_param_from_file_button.on_click(self.load_bkg_param_from_file)


        self.env.select_grid_menu = Select(title='Select Grid', 
                                         options=['Obs'], 
                                         value='Obs',
                                         width=150)
        

        self.env.grid_circle_size = TextInput(
            value=str(2), title="Circle Size", width=80)


        self.env.select_color_palette = Select(title='Color Palette', 
                                         options=self.env.color_palette_options, 
                                         value=self.env.default_color_palette,
                                         width=150)
        pal=getattr(bokeh.palettes, self.env.default_color_palette)
        if type(pal)==dict:
            self.palette = pal[9]
        else:
            self.palette = pal       
        self.env.check_reverse_color_palette = CheckboxGroup(
                                                            labels=['Reverse'],
                                                            active=[1],
                                                            height=10,
                                                            width=10)

        self.env.check_make_grid = CheckboxGroup(
                                                labels=['Make Grid'],
                                                active=[0,1],
                                                height=10,
                                                width=100,
                                                )
        
        self.env.check_show_echelle = CheckboxGroup(
                                                labels=['Show Echelle'],
                                                active=[0,1],
                                                height=10,
                                                width=100,
                                                )

        self.env.check_show_horizontal_lines = CheckboxGroup(
                                                labels=['Show lines'],
                                                active=[0,1],
                                                height=10,
                                                width=100,
                                                )

        self.env.check_show_inverted_lines = CheckboxGroup(
                                                labels=['Inverted lines'],
                                                active=[0,1],
                                                height=10,
                                                width=100,
                                                )

        self.env.check_show_modes_grid = CheckboxGroup(
                                        labels=['Show Modes Only'],
                                        active=[1],
                                        height=10,
                                        width=100,
                                        )
        self.env.check_color_map_lock = CheckboxGroup(
                                                labels=['Lock'],
                                                active=[1],
                                                height=10,
                                                width=100,
                                                )
        
        self.env.check_periodogram_axis_scale = CheckboxGroup(
                                                labels=['Log Scale'],
                                                active=[],
                                                height=10,
                                                width=100,
                                                )

        self.env.check_periodogram_axis_scale.on_change("active",
                                                        self.toggle_periodogram_axis_scale)


        self.initialize_selection_tables()
        self.make_tb_echelle_diagram()
        self.interact_echelle()
        self.make_grid()
        self.initilize_plot_table()

        self.env.test_button = Button(
            label="Get Selection", button_type=self.env.button_type, width=150)
        self.env.test_button.on_click(self.get_all_selection_button)
        
        self.env.clear_se_grid_prd_button = Button(
            label="Clear Selection", button_type=self.env.button_type, width=150)
        self.env.clear_se_grid_prd_button.on_click(self.clear_se_grid_prd)

        self.env.clear_se_table1_button = Button(
            label="Clear Table 1", button_type=self.env.button_type, width=150)
        self.env.clear_se_table1_button.on_click(self.clear_se_table1)

        self.env.clear_se_table2_button = Button(
            label="Clear Table 2", button_type=self.env.button_type, width=150)
        self.env.clear_se_table2_button.on_click(self.clear_se_table2)

        self.env.find_peaks_button = Button(
            label="Find Peak", button_type=self.env.button_type, width=150)
        self.env.find_peaks_button.on_click(self.find_peak_frequencies)

        self.env.calculate_synthetic_psd_button = Button(
            label="Calculate Synthetic PSD", button_type=self.env.button_type, width=150)
        self.env.calculate_synthetic_psd_button.on_click(self.calculate_synthetic_psd)

        self.env.show_plot = Button(
            label="Show Plot", button_type=self.env.button_type, width=150)
        self.env.show_plot.on_click(self.show_plot)


        # Inverted line 
        self.env.inverted_line_initial_y_text = TextInput(
            value=str(0), title="Initial y", width=50)
        self.env.inverted_line_length_text = TextInput(
            value=str(10), title="Length", width=50)
        self.env.inverted_line_scale_text = TextInput(
            value=str(-1), title="Scale", width=50)
        self.env.inverted_line_xvalue_text = TextInput(
            value=str(0), title="x value", width=50)        
        self.env.inverted_line_update_button = Button(
            label="Update Slider", 
            button_type=self.env.button_type, 
            width=100)
        self.env.inverted_line_update_button.on_click(
            self.update_inverted_line)


        self.env.inverted_slider_max_value_text = TextInput(
            value=str(400), title="Max x Value", width=50)

        #self.update_selection_tables()
        
        self.env.tb_source.on_change('data',self.update_whole_plot)

        self.plot_vertical_lines()
        self.inverted_slider()
        self.old_frequency_min = 0
        self.old_frequency_max = 0
        self.old_grid_selection = ''
        self.publish_message(text='Select Fits File')

    def initilize_plot_table(self):
        """
        Initializes the table used for selecting which plots to display.

        This table (`self.env.table_plot`) allows users to toggle the visibility
        of different datasets on the main periodogram (e.g., observed, synthetic, subtracted).
        It sets up a `ColumnDataSource` (`self.env.tb_plot`) with default entries
        like 'Grid' and their associated colors.
        """

        self.env.tb_plot = ColumnDataSource(
            data=dict(
                name=list(['Grid']), colour = list(['grey'])
            ))
    
        columns = [
            TableColumn(field="name", title="Name"),
            TableColumn(field="colour", title="Colour"),
        ]

        self.env.table_plot = DataTable(
            source=self.env.tb_plot,
            columns=columns,
            width=200,
            height=400,
            selectable="checkbox",
        )
        self.env.tb_plot.selected.indices = [0]

    def update_source(self,attr,old,new):
        """
        Callback function triggered when the main data source changes.
        (e.g. a new FITS file is loaded).

        This method re-initializes the periodogram by calling `trim_frequency()`,
        clears existing mode selection tables (`clear_se_table1`, `clear_se_table2`),
        and updates the plots via `update_plot()`.

        Args:
            attr: The attribute that changed (unused).
            old: The old data (unused).
            new: The new data (unused).
        """
        # ff, pp = self.read_fits_get_fp()
        # mm = ['999']*(len(pp))
        # f = (ff*u.Hz).to(self.env.frequency_unit)
        # p = pp*self.env.power_unit
        # period = lk_prd_module.Periodogram(f, p)
        # self.periodogram = period
        # old_data= ColumnDataSource(
        #     data=dict(
        #         frequency=list(self.periodogram.frequency.value),
        #         power=list(self.periodogram.power.value),
        #         Mode = mm,
        #     ))
        self.publish_message(text='Updating')
        self.trim_frequency()
        # self.env.tb_other_periodogram.data=dict(old_data.data)
        self.clear_se_table1()
        self.clear_se_table2()
        self.update_plot(0, 0, 0)
        #self.update_value()
        self.publish_message(text='Ready')


    def initialize_dnu_periodogram(self):
        """
        Initializes the main periodogram figure and its associated ColumnDataSource.

        Reads frequency and power data from a FITS file (via `read_fits_get_fp`).
        Sets default frequency ranges, delta Nu, and other parameters.
        Creates a Bokeh figure for the periodogram with tools for zoom, selection, etc.
        Creates a `ColumnDataSource` (`tb_other_periodogram`) to hold frequency,
        power, and mode identification data.
        Plots the periodogram data (frequency vs. power) and a threshold line.

        Returns:
            tuple: A tuple containing:
                - tb_other_periodogram (ColumnDataSource): Source for the periodogram.
                - fig_other_periodogram (Figure): Bokeh figure object for the periodogram.
        """
        ff, pp = self.read_fits_get_fp()
        mm = ['999']*(len(pp))

        self.env.minimum_frequency = 1  # 1
        self.env.maximum_frequency = 8000  # 8000
        self.env.maxdnu = 100
        self.env.dnu_val = 24.8

        f = (ff*u.Hz).to(self.env.frequency_unit)
        p = pp*self.env.power_unit
        if ff.any():
            period = lk_prd_module.Periodogram(f, p)

            self.periodogram = period

            tb_other_periodogram = ColumnDataSource(
                data=dict(
                    frequency=list(self.periodogram.frequency.value),
                    power=list(self.periodogram.power.value),
                    Mode = mm,
                    # cuttoff=list(np.array([0])),
                ))
        else:

            self.periodogram = None

            tb_other_periodogram = ColumnDataSource(
                data=dict(
                    frequency=list([]),
                    power=list([]),
                    Mode = list([]),
                    # cuttoff=list(np.array([0])),
                ))    


        # Intialize other periodgram
        fig_other_periodogram = figure(
            width=1400,
            height=600,
            tools=["box_zoom", "wheel_zoom",
                   "lasso_select", "tap", "reset", "save"],
            title="Other Periodogram", tooltips=self.env.TOOLTIPS,
        )


        color_map = self.mode_color_map
        color_mapper = CategoricalColorMapper(
            factors=list(color_map.keys()), 
            palette=list(color_map.values()))

        fig_other_periodogram.circle("frequency", "power",
                                     source=tb_other_periodogram,
                                     alpha=0.7, 
                                     color = {'field': 'Mode', 
                                                'transform': color_mapper},
                                     **self.env.selection,name='Grid'
                                     )

        fig_other_periodogram.line("frequency", "power",
                                   source=tb_other_periodogram,
                                   alpha=0.7, color="grey",name='Grid')
        #color="#1F77B4"
        fig_other_periodogram.ray(
            y="other_prd_cuttoff",
            x="minimum_frequency",
            source=self.tb_constants_val,
            name='threshold_line',
            length=8000,
            angle=0,
            color='red'
        )





        

        # fig_other_periodogram.circle("freq_values","power_values",
        #                             source=self.env.tb_grid_source,
        #                             alpha=0.7,**self.env.selection,)

        # fig_other_periodogram.line("freq_values","power_values",
        #                             source=self.env.tb_grid_source,
        #                             alpha=0.7,color="#1F77B4")

        #fig_other_periodogram.x_range.start = int(self.env.minimum_frequency)
        #fig_other_periodogram.x_range.end = int(self.env.maximum_frequency)

        #fig_other_periodogram.x_range.start = 200
        #fig_other_periodogram.x_range.end = 800

        return tb_other_periodogram, fig_other_periodogram

    def plot_vertical_lines(self):
        """
        Plots vertical lines on the main periodogram to indicate selected mode frequencies.

        These lines are drawn based on the data in `self.tb_se_second_source` (Table 2,
        the final selection table). The lines are colored according to the mode type ('l' value)
        using `self.mode_color_map`.
        """

        color_map = self.mode_color_map
        color_mapper = CategoricalColorMapper(
            factors=list(color_map.keys()), 
            palette=list(color_map.values()))


        self.env.fig_other_periodogram.ray(x="Frequency",y=0,
                        source= self.tb_se_second_source,
                        length=2137, 
                        angle=np.pi/2,
                        legend_field='Mode',
                        name='vertical_line',
                        color={'field': 'Mode', 
                                                'transform': color_mapper})


    def make_tb_echelle_diagram(self):
        """
        Generates or updates the data for the echelle diagram.

        If the echelle diagram table (`self.env.tb_echelle_diagram`) is not
        initialized, it creates it.
        If the 'Show Echelle' checkbox is active and periodogram data is available,
        it calculates the echelle diagram data using `_clean_echelle()`.
        This involves reshaping the periodogram power based on the current delta Nu.
        The results (image, frequency axes, dimensions) are stored in
        `self.env.tb_echelle_diagram`. If 'Show Echelle' is not active,
        it clears the echelle diagram data.
        """
        if self.env.tb_echelle_diagram == None:
            print('Creating an echelle diagram, Creating column source')
            self.env.tb_echelle_diagram = ColumnDataSource(
                data=dict(image=[],
                          x_f=[],
                          y_f=[],
                          dw=[],
                          dh=[],
                          xmin=[],
                          ymin=[],
                          y_original=[],  # value without
                          # xx=[],
                          # yy=[],
                          # freq_values=[],
                          ))
        else:
            print('Refereshing everything')
         
        if self.env.check_show_echelle.active[0]==0 and not self.env.tb_other_periodogram.to_df().empty:
        # Load the values
            frequency = self.env.tb_other_periodogram.data['frequency'] * \
                self.env.frequency_unit
            power = self.env.tb_other_periodogram.data['power']*self.env.power_unit
            (ep, self.x_echelle, self.y_echelle, y_original,self.xx, self.yy, 
            self.freq_values, self.power_values) = self._clean_echelle(
                                deltanu=self.dnu_val,
                                #minimum_frequency = self.env.minimum_frequency*self.env.frequency_unit,
                                #maximum_frequency = self.env.maximum_frequency*self.env.frequency_unit
                                )

            x_f = self.x_echelle
            y_f = self.y_echelle
            dw = (x_f.flatten().max() - x_f.flatten().min()).value
            dh = (y_f.flatten().max() - y_f.flatten().min()).value
            xmin = x_f.flatten().min().value
            ymin = y_f.flatten().min().value

            new_data = ColumnDataSource(
                data=dict(image=[ep.value],
                        x_f=[x_f.value],
                        y_f=[y_f.value],
                        dw=[dw],
                        dh=[dh],
                        xmin=[xmin],
                        ymin=[ymin],
                        y_original=[y_original],
                        # xx=[xx],
                        # yy=[yy],
                        # freq_values=[freq_values],
                        )
            )

            self.env.tb_echelle_diagram.data = dict(new_data.data)
        else:
            old_data = ColumnDataSource(
                data=dict(image=[],
                          x_f=[],
                          y_f=[],
                          dw=[],
                          dh=[],
                          xmin=[],
                          ymin=[],
                          y_original=[],  # value without
                          # xx=[],
                          # yy=[],
                          # freq_values=[],
                          ))
            self.env.tb_echelle_diagram.data = dict(old_data.data)


    def initialize_selection_tables(self):
        """
        Initializes the ColumnDataSources and Bokeh DataTable widgets for mode selection.

        Creates two tables:
        - `self.env.table_se_first`: For temporary mode selections (Table 1).
        - `self.env.table_se_second`: For final mode selections (Table 2).
        Each table is backed by a `ColumnDataSource` (`self.tb_se_first_source` and
        `self.tb_se_second_source` respectively) and configured with columns for
        'Slicefreq', 'Frequency', 'Power', and 'Mode'.
        """

        # self.tb_se_first_source=ColumnDataSource(data=dict(x=[], y=[],z=[]))
        # self.tb_se_second_source=ColumnDataSource(data=dict(x=[], y=[], z=[]))

        self.tb_se_first_source = ColumnDataSource(
            data=dict(Slicefreq=[], Frequency=[], Power=[], Mode=[], xx=[]))
        self.tb_se_second_source = ColumnDataSource(
            data=dict(Slicefreq=[], Frequency=[], Power=[], Mode=[], xx=[], mode_color=[]))
        columns = [
            TableColumn(field="Slicefreq", title="Slice Freq"),
            TableColumn(field="Frequency", title="Frequency"),
            TableColumn(field="Power", title="Power"),
            TableColumn(field="Mode", title="Mode"),

        ]

        self.env.table_se_first = DataTable(
            source=self.tb_se_first_source,
            columns=columns,
            width=500,
            height=600,
            sortable=True,
            selectable=True,
            editable=True,
        )

        self.env.table_se_second = DataTable(
            source=self.tb_se_second_source,
            columns=columns,
            width=500,
            height=600,
            sortable=True,
            selectable="checkbox",
            editable=True,
        )




        # Figure 
        # self.env.fig_tpfint.circle(x='xx', 
        #                            y='Slicefreq',
        #                            size=2, 
        #                            fill_alpha=1,
        #                            color={'field': 'Mode', 
        #                                   'transform': color_mapper}, 
        #                            source=self.tb_se_second_source )



        # self.mode_color_map
        # self.env.fig_tpfint.circle(x='xx', y='Slicefreq',size=2, 
        #                            fill_alpha=0.2,
        #                            color='mode_color', 
        #                            source=self.tb_se_second_source )

        # from bokeh.transform import linear_cmap
        # from bokeh.palettes import Spectral4
        # self.env.fig_tpfint.circle(x='xx', y='Slicefreq', source=self.tb_se_second_source, 
        #                            size=10, 
        #                            color=linear_cmap('Mode', 
        #                                              palette=Spectral4, 
        #                                              factors=list(color_map.keys())), 
        #                                              legend_field='Mode', 
        #                                              fill_alpha=0.6)



        # self.env.fig_tpfint.circle(x='xx', y='Slicefreq', source=self.tb_se_second_source, 
        #                         size=10, 
        #                         color=linear_cmap('Mode', 
        #                                             palette=list(color_map.values()), 
        #                                             factors=list(color_map.keys())), 
        #                         legend_field='Mode', 
        #                         fill_alpha=0.6)

    def update_selection_tables(self):
        """
        Sets up (or would set up) callbacks for interactions between selection tables and plots.

        This method is largely commented out in the provided code. Its original intent
        was likely to establish JavaScript callbacks (`CustomJS`) or Python callbacks
        to synchronize selections made on the echelle diagram grid (`self.env.tb_grid_source`)
        or the main periodogram (`self.env.tb_other_periodogram`) with the mode selection
        tables (`self.tb_se_first_source`).
        """
        # self.env.tb_grid_source.selected.js_on_change(
        #     "indices",
        #     CustomJS(
        #         args=dict(s1=self.env.tb_grid_source,
        #                   dnu=self.env.dnu_val,
        #                   s2=self.tb_se_first_source,
        #                   table=self.env.table_se_first),

        #         code="""
        #         var inds = cb_obj.indices;
        #         var d1 = s1.data;
        #         var d2 = s2.data;
        #         //d2['SliceFreq'] = []
        #         //d2['Frequency'] = []
        #         for (var i = 0; i < inds.length; i++) {
        #             d2['Slicefreq'].push(d1['yy'][inds[i]])
        #             d2['Frequency'].push(d1['freq_values'][inds[i]])
        #             d2['Power'].push(d1['power_values'][inds[i]])
        #         }
        #         s2.change.emit();
        #         table.change.emit();

        #         var inds = source_data.selected.indices;
        #         var data = source_data.data;
        #         var out = "x, y\\n";
        #         for (i = 0; i < inds.length; i++) {
        #             out += data['x'][inds[i]] + "," + data['y'][inds[i]] + "\\n";
        #         }
        #         var file = new Blob([out], {type: 'text/plain'});

        #     """,
        #     ),
        # )
        print('Commented')
        # self.env.tb_grid_source.selected.on_change(
        #     'indices', self.selection_grid_to_prd_fig)

        # self.env.tb_other_periodogram.selected.on_change(
        #     'indices', self.selection_prd_to_grid_fig)
        
        # self.env.tb_grid_source.selected.on_change(
        #     'indices', self.selection_grid_to_table_fig)


        # self.env.tb_grid_source.selected.on_change(
        #     'indices', self.selection_grid_to_table_fig)

        # self.env.tb_grid_source.selected.on_change(
        #     'indices', self.selection_table_to_prd_fig)

        # self.env.tb_other_periodogram.selected.on_change(
        #     'indices', self.selection_prd_to_grid_fig)
        # print('Nothing')



        




    def make_grid(self):
        """
        Initializes and populates the ColumnDataSource for the echelle diagram grid points.

        If `self.env.tb_grid_source` is None, it's initialized.
        If the 'Make Grid' checkbox is active and periodogram data is available:
        - It filters the echelle diagram points (`self.xx`, `self.yy`,
          `self.freq_values`, `self.power_values` from `_clean_echelle`)
          based on a power threshold (`self.env.echelle_noise_cuttoff_text`).
        - The filtered points are stored in `self.env.tb_grid_source`.
        - It applies existing mode assignments from Table 1 and Table 2 to these grid points.
        - It adjusts the size of circles on the echelle diagram based on `self.env.grid_circle_size`.
        - If 'Show Modes Only' is active, it further filters the grid to show only points with assigned modes.
        If 'Make Grid' is not active, `self.env.tb_grid_source` is cleared.
        """

        if self.env.tb_grid_source == None:
            self.env.tb_grid_source = ColumnDataSource(
                data=dict(
                    xx=[],
                    yy=[],
                    freq_values=[],
                    power_values=[],
                    Mode=[],
                )
            )

            if not self.mode_shape_selection == 'circle':
                # To be done properly
                self.env.fig_tpfint.rect('center_x', 'center_y', width.flatten(), height.flatten(), fill_color='gray',
                                         fill_alpha=0.2, line_color='blue', name='grid', source=self.env.tb_grid_source)
            else:
                

                color_map = self.mode_color_map
                color_mapper = CategoricalColorMapper(
                    factors=list(color_map.keys()), 
                    palette=list(color_map.values()))

                self.env.fig_tpfint.circle(x = 'xx', 
                                        y = 'yy',
                                        size = 2, 
                                        fill_alpha = 0.2,
                                        name='grid_circle', 
                                        line_color = {'field': 'Mode', 
                                                'transform': color_mapper}, 
                                        source=self.env.tb_grid_source,
                                        **self.env.selection)





                # color_mapper = CategoricalColorMapper(
                #     factors=list(color_map.keys()), 
                #     palette=list(color_map.values()))
                
                # self.env.fig_tpfint.circle(x='xx', y='yy',
                #                            size=2, 
                #                            fill_alpha=0.2, 
                #                            line_color='blue', 
                #                            source=self.env.tb_grid_source)

                # self.env.fig_tpfint.circle(x = 'xx', 
                #                            y = 'yy',
                #                            size = 2, 
                #                            fill_alpha = 0.2, 
                #                            color = {'field': 'Mode', 
                #                                   'transform': color_mapper}, 
                #                            source=self.env.tb_grid_source)
                
        #print('Griding',self.env.check_make_grid.active)
        if self.env.check_make_grid.active[0]==0 and not self.env.tb_other_periodogram.to_df().empty:
            cutt_off = float(self.env.echelle_noise_cuttoff_text.value)
            self.tb_constants_val.data['other_prd_cuttoff'] = list([cutt_off])
            
            val = float(self.env.frequency_minimum_text.value)
            self.tb_constants_val.data['minimum_frequency'] = list([val])
            print('Threshold', val)
            ind = np.array(self.power_values) >= cutt_off
            xx = np.array(self.xx)[ind]
            yy = np.array(self.yy)[ind]
            ff = np.array(self.freq_values)[ind]
            pp = np.array(self.power_values)[ind]
            mm = ['999']*(len(pp))

            old_data = ColumnDataSource(
                data=dict(
                    xx=list(xx),
                    yy=list(yy),
                    freq_values=list(ff),
                    power_values=list(pp),
                    Mode = mm,
                )
            )
            self.env.tb_grid_source.data = dict(old_data.data)
            self.apply_modes(table=self.tb_se_first_source.to_df())
            self.apply_modes(table=self.tb_se_second_source.to_df())
            val=int(self.env.grid_circle_size.value)
            print('Circle size',val)
            self.env.fig_tpfint.select('grid_circle').glyph.size = val
            if self.env.check_show_modes_grid.active[0]==0:
                val='999'
                df_grid=self.env.tb_grid_source.to_df().query('Mode !=@val')
                old_data=ColumnDataSource(df_grid.to_dict('list'))
                self.env.tb_grid_source.data = dict(old_data.data)



        else:
            old_data = ColumnDataSource(
                data=dict(
                    xx=[],
                    yy=[],
                    freq_values=[],
                    power_values=[],
                    Mode=[],
                )
            )
            self.env.tb_grid_source.data = dict(old_data.data)

    def read_fits_get_fp(self):
        """
        Reads frequency (f) and power (p) data from a FITS periodogram file.

        The path to the FITS file is obtained from `self.env.tb_source.data['path_fits']`.
        It expects the FITS file to have frequency in the first column and power in
        the second column of the primary HDU's data. Byte swapping is performed
        to ensure correct endianness.

        Returns:
            tuple: A tuple containing:
                - ff (numpy.ndarray): Array of frequency values.
                - pp (numpy.ndarray): Array of power values.
                Returns empty arrays if the file does not exist or cannot be read.
        """
        self.publish_message(text='Reading Fits')
        ff = np.array([])
        pp = np.array([])
        id_mycatalog=self.env.tb_source.data['id_mycatalog'][0]
        # self.id_mycatalog = id_mycatalog
        # filename=mycatalog.filename(
        #     id_mycatalog=id_mycatalog,
        #     name='other_psd')
        filename =Path(self.env.tb_source.data['path_fits'][0])
        print('Running read fits',filename)
        if filename.is_file():
            from astropy.io import fits
            import pandas
            with fits.open(
                #'/Users/dp275303/work/tessipack_developement_test/PSD_ _no_gap.fits'
                filename
                ) as data:
                df = pandas.DataFrame(data[0].data)

            ff = df[0].values
            pp = df[1].values
            ff = ff.byteswap().newbyteorder()
            pp = pp.byteswap().newbyteorder()
        else:
            print('File does not exist')
        self.publish_message(text='Read Fits')

        return ff, pp

    def calculate_synthetic_psd(self):
        """
        Calculates and plots a synthetic Power Spectral Density (PSD).

        This function calls `functions.calculate_synthetic_spectrum` using
        filenames for the observed FITS, background parameters, and peak-bagging
        parameters obtained from the environment (`self.env`).
        It then plots the observed PSD, the calculated synthetic PSD, and their
        subtraction on the main periodogram figure (`self.env.fig_other_periodogram`).
        The plot selection table (`self.env.tb_plot`) is updated to allow toggling
        these new plots.

        Returns:
            pandas.DataFrame: The DataFrame containing the frequency, observed PSD,
                              synthetic PSD, and subtracted PSD, as returned by
                              `functions.calculate_synthetic_spectrum` and filtered
                              by current frequency limits.
        """
        self.publish_message('Calculating Synthetic Spectra; Busy')
        self.env.select_grid_menu.options = ['Obs', 'Syn', 'Sub']

        data = functions. calculate_synthetic_spectrum(fits_file=self.env.selected_filename_text.text,
                                                     bkg_file=self.env.selected_filename_background_text.text,
                                                     pkb_file=self.env.selected_filename_pkb_text.text,
                                                     n_harvey=2)
        data['sub_psd'] = data['psd'] - data ['synthetic_psd']
        freq_min =  float(self.env.frequency_minimum_text.value)
        freq_max =  float(self.env.frequency_maximum_text.value)
        data = data.query('freq>@freq_min & freq<@freq_max')
        
        freq = data.freq.values
        power = data.psd.values
        print('frequecny calculation', freq)
        name= 'Obs'
        self.add_plot_other_periodogram(freq = freq, 
                                        power= power,
                                        name= name, 
                                        color = 'blue')

        freq = data.freq.values
        power = data.synthetic_psd.values
        name= 'Syn'
        self.add_plot_other_periodogram(freq = freq, 
                                        power = power,
                                        name= name, 
                                        color = 'green')
        
                
        freq = data.freq.values
        power = data.sub_psd.values
        name= 'Sub'
        self.add_plot_other_periodogram(freq = freq, 
                                        power= power,
                                        name= name, 
                                        color = 'red')
        old_data=ColumnDataSource(
        data=dict(
            name=list(['Grid', 'Obs' ,'Syn', 'Sub']), colour = list(['grey', 'blue', 'green', 'red'])
        ))
        self.env.tb_plot.data = dict(old_data.data)
        self.env.tb_plot.selected.indices = [0]
        self.publish_message('Ready')

        return data

    def show_plot(self):
        """
        Updates the visibility of plots on the main periodogram based on table selection.

        Iterates through the plot selection table (`self.env.tb_plot`).
        Hides all plots first, then makes visible only those plots whose
        corresponding rows in the table are selected.
        """
        df = self.env.tb_plot.to_df()
        for name in df['name']:
            self.env.fig_other_periodogram.select(name).visible = False
        ind =self.env.tb_plot.selected.indices
        df = df.loc[ind]
        print('df after selection', df)
        for name in df['name']:
            self.env.fig_other_periodogram.select(name).visible = True
        print ('Finished')

    def add_plot_other_periodogram(self,freq =None,power= None,
                                   name= None, color = None ):
        """
        Adds or updates a line plot on the main periodogram figure.

        If a line with the given `name` already exists, its data source is updated.
        Otherwise, a new line is created. The line is initially set to be invisible.

        Args:
            freq (array-like, optional): Frequency values for the plot.
            power (array-like, optional): Power values for the plot.
            name (str, optional): Name for the line glyph (used for selection/update).
            color (str, optional): Color for the line.
        """
        # self.env.fig_other_periodogram.line(freq, power,
        #                    name=name,
        #                     alpha=0.7, color=color)
        # self.env.fig_other_periodogram.select(name).visible = False

        existing_line = None
        for renderer in self.env.fig_other_periodogram.renderers:
            if hasattr(renderer, 'name') and renderer.name == name:
                existing_line = renderer
                break

        if existing_line:
            # Update the existing line's data source
            existing_line.data_source.data['x'] = freq
            existing_line.data_source.data['y'] = power
            existing_line.data_source.trigger('data', existing_line.data_source.data, existing_line.data_source.data)
        else:
            # Create a new line
            self.env.fig_other_periodogram.line(freq, power, name=name, alpha=0.7, color=color)

        # Assuming you still want to set the visibility to False
        self.env.fig_other_periodogram.select(name=name).visible = False


    def update_value(self):
        """
        Updates environment variables from UI text inputs and refreshes plots.

        Reads values for minimum frequency, maximum frequency, maximum delta Nu,
        and current delta Nu from their respective TextInput widgets in `self.env`.
        Updates the `self.env.dnu_slider` value.
        Then calls `update_plot()` to refresh the echelle diagram and related plots.
        """
        self.env.minimum_frequency = float(
            self.env.frequency_minimum_text.value)
        self.env.maximum_frequency = float(
            self.env.frequency_maximum_text.value)
        self.env.maxdnu = float(self.env.frequency_maxdnu_text.value)
        self.env.dnu_val = float(self.env.dnu_text.value)
        self.env.dnu_slider.value = self.env.dnu_val

        print('Values transfering', self.env.minimum_frequency,
              self.env.maximum_frequency, self.env.maxdnu)
        
        #print('range', self.env.fig_other_periodogram.x_range.end)

        #print(self.env.fig_other_periodogram.x_range.end)
        self.update_plot(0, 0, 0)
        #self.env.fig_other_periodogram.x_range.start = int(self.env.minimum_frequency)
        #self.env.fig_other_periodogram.x_range.end = int(self.env.maximum_frequency)
        start = int(self.env.minimum_frequency)
        end = int(self.env.maximum_frequency)

        #self.env.fig_other_periodogram.x_range=(start, end)
        #print(self.env.fig_other_periodogram.x_range.end)

    def check_change_in_frequency_limit(self):
        """
        Checks if the frequency limits or selected grid type have changed.

        Compares the current values of `self.env.minimum_frequency`,
        `self.env.maximum_frequency`, and `self.env.select_grid_menu.value`
        with their previously stored values (`self.old_frequency_min`,
        `self.old_frequency_max`, `self.old_grid_selection`).
        Updates the stored "old" values for the next check.

        Returns:
            bool: True if any of the monitored values have changed, False otherwise.
        """
        #Get new frequency values
    
        self.env.minimum_frequency = float(
            self.env.frequency_minimum_text.value)
        self.env.maximum_frequency = float(
            self.env.frequency_maximum_text.value)
        self.grid_selection = self.env.select_grid_menu.value
        if  (self.env.minimum_frequency == self.old_frequency_min) and (
            self.env.maximum_frequency == self.old_frequency_max) and (
            self.grid_selection == self.old_grid_selection) :
            print('No change in Min and Max Freq Cuttoff or Grid')
            value = False
        else:
            print('Change in Frequency or Grid')
            value = True
            
        self.old_frequency_min = self.env.minimum_frequency
        self.old_frequency_max = self.env.maximum_frequency
        self.old_grid_selection = self.grid_selection

        return value

    def update_whole_plot(self,attr, old , new):
        """
        Comprehensive update callback, typically triggered by a change in the main source.

        This method orchestrates a full refresh of the mode selection interface:
        1. Calls `trim_frequency()` to reload and filter periodogram data.
        2. Clears both mode selection tables (`clear_se_table1`, `clear_se_table2`).
        3. Calls `update_plot()` to regenerate echelle diagram and grid.
        4. Updates the echelle diagram's x-axis label with the current delta Nu.
        5. Adjusts color mapping and stretch slider for the echelle diagram image.
        6. Updates visibility of horizontal lines based on checkbox state.

        Args:
            attr: The attribute that changed (unused).
            old: The old data (unused).
            new: The new data (unused).
        """
        self.trim_frequency()
        self.clear_se_table1()
        self.clear_se_table2()
        self.update_plot(0, 0, 0)


        self.id_mycatalog = self.env.tb_source.data['id_mycatalog'][0]
        dnu = self.dnu_val
        self.env.fig_tpfint.xaxis.axis_label = r'Frequency / {:.3f} Mod. 1'.format(
            dnu)

        self.make_tb_echelle_diagram()

        ep = self.env.tb_echelle_diagram.data['image']*self.env.power_unit
        lo, hi = np.nanpercentile(ep.value, [0.1, 99.9])
        vlo, vhi = 0.3 * lo, 1.7 * hi
        vstep = (lo - hi)/500
                # self.palette = getattr(bokeh.palettes, 
                #                     self.env.select_color_palette.value)[9] 
        pal=getattr(bokeh.palettes, self.env.select_color_palette.value)
        if type(pal)==dict:
            self.palette = pal[9]
        else:
            self.palette = pal  
                
            if self.env.check_reverse_color_palette.active[0]!=1:
                self.palette = list(reversed(self.palette))
        # Lock color mapper
        if self.env.check_color_map_lock.active[0]==1:
            print('Value of colormap check',self.env.check_color_map_lock.active[0])
            color_mapper = LogColorMapper(palette=self.palette, low=lo, high=hi)
            self.env.fig_tpfint.select(
                'img').glyph.color_mapper.low = color_mapper.low
            self.env.fig_tpfint.select(
                'img').glyph.color_mapper.high = color_mapper.high
            self.env.fig_tpfint.select(
                'img').glyph.color_mapper.palette = getattr(color_mapper,'palette')
            self.env.stretch_sliderint.start = vlo
            self.env.stretch_sliderint.end = vhi
            self.env.stretch_sliderint.value = (lo, hi)
        self.env.dnu_slider.start = 0.01
        self.env.dnu_slider.end = self.env.maxdnu
        if self.env.check_show_horizontal_lines.active[0]==0:
            self.env.fig_other_periodogram.select('vertical_line').visible = True
        else:
            self.env.fig_other_periodogram.select('vertical_line').visible = False
        
        self.publish_message(text='Ready')




    def update_plot(self, attr, old, new):
        """
        Core callback function to update plots when parameters change.

        This method is called when various UI elements (like sliders or text inputs
        for frequency, delta Nu, etc.) are modified.
        It performs the following steps:
        1. Checks if frequency limits have changed (`check_change_in_frequency_limit`)
           and calls `trim_frequency()` if they have.
        2. Updates the echelle diagram's x-axis label.
        3. Calls `make_tb_echelle_diagram()` to regenerate echelle data.
        4. If the echelle diagram is visible:
            - Calculates color stretch limits (lo, hi) from the echelle image power.
            - Updates the color palette and potentially reverses it.
            - If color map is not locked, updates the echelle image's color mapper
              and the stretch slider's range and value.
            - Updates the delta Nu slider's range.
        5. Updates visibility of vertical lines on the periodogram (mode markers).
        6. Calls `make_grid()` to regenerate the echelle grid points.

        Args:
            attr: The attribute that changed (unused).
            old: The old value (unused).
            new: The new value (unused).
        """
        self.publish_message(text='Updating Plot')
        if self.check_change_in_frequency_limit():
            print('Triming Frequency')
            self.trim_frequency()

        self.id_mycatalog = self.env.tb_source.data['id_mycatalog'][0]
        dnu = self.dnu_val
        self.env.fig_tpfint.xaxis.axis_label = r'Frequency / {:.3f} Mod. 1'.format(
            dnu)

        self.make_tb_echelle_diagram()
        if self.env.check_show_echelle.active[0]==0:

            ep = self.env.tb_echelle_diagram.data['image']*self.env.power_unit
            if ep.value.any():
                lo, hi = np.nanpercentile(ep.value, [0.1, 99.9])
                vlo, vhi = 0.3 * lo, 1.7 * hi
                vstep = (lo - hi)/500
                # self.palette = getattr(bokeh.palettes,
                #                     self.env.select_color_palette.value)[9]

                pal=getattr(bokeh.palettes, self.env.select_color_palette.value)
                if type(pal)==dict:
                    self.palette = pal[9]
                else:
                    self.palette = pal

                if self.env.check_reverse_color_palette.active[0]!=1:
                    self.palette = list(reversed(self.palette))
                if self.env.check_color_map_lock.active[0]==1:
                    print('Value of colormap check',self.env.check_color_map_lock.active[0])
                    color_mapper = LogColorMapper(palette=self.palette, low=lo, high=hi)
                    self.env.fig_tpfint.select(
                        'img').glyph.color_mapper.low = color_mapper.low
                    self.env.fig_tpfint.select(
                        'img').glyph.color_mapper.high = color_mapper.high
                    self.env.fig_tpfint.select(
                        'img').glyph.color_mapper.palette = getattr(color_mapper,'palette')
                    self.env.stretch_sliderint.start = vlo
                    self.env.stretch_sliderint.end = vhi
                    self.env.stretch_sliderint.value = (lo, hi)
                self.env.dnu_slider.start = 0.01
                self.env.dnu_slider.end = self.env.maxdnu
            if self.env.check_show_horizontal_lines.active[0]==0:
                self.env.fig_other_periodogram.select('vertical_line').visible = True
                # self.env.fig_other_periodogram.select('vertical_inverted_line').visible = True
            else:
                self.env.fig_other_periodogram.select('vertical_line').visible = False
                # self.env.fig_other_periodogram.select('vertical_inverted_line').visible = False

        self.make_grid()
        self.publish_message(text='Ready')

    def _validate_numax(self, numax):
        """
        Validates the nu_max (frequency of maximum power) value.

        If `numax` is None, it attempts to return `self.numax` (if set, though
        this attribute is not explicitly defined in this class, suggesting it might
        be from a parent or intended for future use).

        Args:
            numax (float or None): The nu_max value to validate.

        Returns:
            float: The validated nu_max value.

        Raises:
            AttributeError: If `numax` is None and `self.numax` is not available.
        """
        if numax is None:
            try:
                return self.numax
            except AttributeError:
                raise AttributeError(
                    "You need to call `Seismology.estimate_numax()` first.") # Or have self.numax defined
        return numax

    def _validate_deltanu(self, deltanu):
        """
        Validates the delta Nu (large frequency separation) value.

        If `deltanu` is None, it returns `self.dnu_val` (the current delta Nu
        value from the UI or environment).

        Args:
            deltanu (float or None): The delta Nu value to validate.

        Returns:
            float: The validated delta Nu value.

        Raises:
            AttributeError: If `deltanu` is None and `self.dnu_val` is not available
                            (should not happen in normal operation).
        """
        if deltanu is None:
            try:
                print('Check here') # Debug print
                return self.dnu_val
            except AttributeError:
                raise AttributeError(
                    "You need to call `Seismology.estimate_deltanu()` first.") # Or have self.dnu_val defined
        return deltanu

    def _clean_echelle(self, deltanu=None, numax=None,
                       minimum_frequency=None, maximum_frequency=None,
                       smooth_filter_width=None, scale='linear'):
        """
        Processes periodogram data to generate arrays for an echelle diagram.

        Validates deltanu and numax inputs. Filters the periodogram data based
        on frequency limits (either derived from numax or explicit min/max frequencies).
        Uses an adaptation of echelle diagram generation logic (similar to that
        found in Lightkurve or other asteroseismology tools, here specifically
        calling `self.apollinaire_echelle` for the core processing) to reshape
        the frequency and power arrays.

        Args:
            deltanu (float, optional): Large frequency separation in units consistent
                with the periodogram's frequency. If None, uses `self.dnu_val`.
            numax (float, optional): Frequency of maximum oscillation power. Used to
                set default frequency ranges if min/max_frequency are not provided.
                Units should be consistent with periodogram frequency.
            minimum_frequency (float, optional): Minimum frequency for the echelle.
                Units should be consistent with periodogram frequency.
            maximum_frequency (float, optional): Maximum frequency for the echelle.
                Units should be consistent with periodogram frequency.
            smooth_filter_width (float, optional): Width for smoothing the periodogram
                before echelle generation. Units should be consistent.
            scale (str, optional): Scale for power in the echelle diagram ('linear'
                or 'log'). Defaults to 'linear'.

        Returns:
            tuple: Contains:
                - ep (Quantity): 2D array of power values for the echelle diagram.
                - x_f (Quantity): 1D array for the x-axis of the echelle (frequency modulo deltanu).
                - y_f (Quantity): 1D array for the y-axis of the echelle (frequency slices).
                - y_original (Quantity): Original y-axis frequency values before centering.
                - xx (list): Flattened x-coordinates for scatter points on echelle.
                - yy (list): Flattened y-coordinates for scatter points on echelle.
                - freq_values (list): Flattened original frequency values corresponding to xx, yy.
                - power_values (list): Flattened original power values corresponding to xx, yy.
        """
        # if (minimum_frequency is None) & (maximum_frequency is None):
        #     numax = self._validate_numax(numax) # numax validation handled if used
        deltanu = self._validate_deltanu(deltanu)

        # if (not hasattr(numax, 'unit')) & (numax is not None):
        #     numax = numax * self.periodogram.frequency.unit
        # if (not hasattr(deltanu, 'unit')) & (deltanu is not None):
        #     deltanu = deltanu * self.periodogram.frequency.unit
        deltanu = deltanu * self.periodogram.frequency.unit

        # freq = self.env.tb_other_periodogram.data['frequency'] * \
        #     self.env.frequency_unit
        # power = self.env.tb_other_periodogram.data['power']*self.env.power_unit

        # fmin = freq[0]
        # fmax = freq[-1]

        # # Check for any superfluous input
        # if (numax is not None) & (any([a is not None for a in [minimum_frequency, maximum_frequency]])):
        #     warnings.warn("You have passed both a numax and a frequency limit. "
        #                   "The frequency limit will override the numax input.",
        #                   LightkurveWarning)

        # # Ensure input numax is in the correct units (if there is one)
        # if numax is not None:
        #     numax = u.Quantity(numax, freq.unit).value
        #     if numax > freq[-1].value:
        #         raise ValueError("You can't pass in a numax outside the"
        #                          "frequency range of the periodogram.")

        #     fwhm = utils.get_fwhm(self.periodogram, numax)

        #     fmin = numax - 2*fwhm
        #     if fmin < freq[0].value:
        #         fmin = freq[0].value

        #     fmax = numax + 2*fwhm
        #     if fmax > freq[-1].value:
        #         fmax = freq[-1].value

        # # Set limits and set them in the right units
        # if minimum_frequency is not None:
        #     fmin = u.Quantity(minimum_frequency, freq.unit).value
        #     if fmin > freq[-1].value:
        #         raise ValueError('Fmin', fmin, "You can't pass in a limit outside the "
        #                          "frequency range of the periodogram.")

        # if maximum_frequency is not None:
        #     fmax = u.Quantity(maximum_frequency, freq.unit).value
        #     if fmax > freq[-1].value:
        #         raise ValueError('Fmax', fmax, "You can't pass in a limit outside the "
        #                          "frequency range of the periodogram.")

        # # Make sure fmin and fmax are Quantities or code below will break
        # fmin = u.Quantity(fmin, freq.unit)
        # fmax = u.Quantity(fmax, freq.unit)

        # # Add on 1x deltanu so we don't miss off any important range due to rounding
        # if fmax < freq[-1] - 1.5*deltanu:
        #     fmax += deltanu

        # fs = np.median(np.diff(freq))
        # x0 = int(freq[0] / fs)

        # ff = freq[int(fmin/fs)-x0:int(fmax/fs)-x0]  # Selected frequency range
        # pp = power[int(fmin/fs)-x0:int(fmax/fs)-x0]  # Power range

        # # Reshape the power into n_rows of n_columns
        # # When modulus ~ zero, deltanu divides into frequency without remainder
        # mod_zeros = find_peaks(-1.0*(ff % deltanu))[0]

        # # The bottom left corner of the plot is the lowest frequency that
        # # divides into deltanu with almost zero remainder
        # start = mod_zeros[0]

        # # The top left corner of the plot is the highest frequency that
        # # divides into deltanu with almost zero remainder.  This index is the
        # # approximate end, because we fix an integer number of rows and columns
        # approx_end = mod_zeros[-1]

        # # The number of rows is the number of times you can partition your
        # # frequency range into chunks of size deltanu, start and ending at
        # # frequencies that divide nearly evenly into deltanu
        # n_rows = len(mod_zeros) - 1

        # # The number of columns is the total number of frequency points divided
        # # by the number of rows, floor divided to the nearest integer value
        # n_columns = int((approx_end - start) / n_rows)

        # # The exact end point is therefore the ncolumns*nrows away from the start
        # end = start + n_columns*n_rows

        # ep = np.reshape(pp[start: end], (n_rows, n_columns))

        # if scale == 'log':
        #     ep = np.log10(ep)

        # # Reshape the freq into n_rowss of n_columnss & create arays
        # ef = np.reshape(ff[start: end], (n_rows, n_columns))
        # x_f = ((ef[0, :]-ef[0, 0]) % deltanu)
        # # Test : Scaling
        # x_f = ((ef[0, :]) % deltanu)
        # # print('x_f max',x_f.max(),deltanu)
        # y_f = (ef[:, 0])

        freq = self.env.tb_other_periodogram.data['frequency']
        power = self.env.tb_other_periodogram.data['power']

        data_frame = pd.DataFrame()
        data_frame['freq'] = freq
        data_frame['power'] = power

        minf = int(self.env.minimum_frequency)
        maxf = int(self.env.maximum_frequency)
        data_frame = data_frame.query('freq<@maxf & freq>@minf')
        if data_frame.empty:
            ep=np.array([])
            x_f=np.array([])
            y_f=np.array([])
            freq_values=np.array([])
            power_values=np.array([])
            y_original=np.array([])
            xx=np.array([])
            yy=np.array([])
        else:    
            ep, x_f, y_f, xx, yy, freq_values, power_values = self.apollinaire_echelle(
                data_frame.freq.values,
                data_frame.power.values,
                deltanu.value
            )

            y_original = y_f
            mean_diff = np.mean(np.diff(y_f))
            y_f_extra = y_f-(mean_diff/2)
            val = y_f[-1]+(mean_diff/2)
            center_y = np.append(y_f_extra, val)
            y_f = center_y

        ep = ep*self.env.power_unit
        x_f = x_f*self.env.frequency_unit
        y_f = y_f*self.env.frequency_unit
        return ep, x_f, y_f, y_original, xx, yy, freq_values, power_values

    def inverted_slider(self):
        """
        Initializes and configures the "Inverted Slider" and associated plot elements.

        This slider (`self.env.inverted_slider`) is likely used to adjust the
        position or appearance of "inverted lines" on the main periodogram, which
        might represent theoretical mode ridge locations or similar features.
        - If the slider doesn't exist, it's created.
        - A `ColumnDataSource` (`self.inverted_slider_source`) is set up to hold data
          for these lines, derived from `self.tb_se_second_source`.
        - Segments (lines) are plotted on `self.env.fig_other_periodogram` based on this source.
        - A callback (`self.update_inverted_slider`) is attached to the slider's value change.
        """
        if self.env.inverted_slider ==None:
            sld_val = float(self.env.inverted_slider_max_value_text.value)
            self.env.inverted_slider = Slider(start=-1*sld_val,
                                            end=sld_val,
                                            value=0,
                                            step=1,
                                            title="Inverted Slider",
                                            width=900)

            color_map = self.mode_color_map
            color_mapper = CategoricalColorMapper(
                factors=list(color_map.keys()), 
                palette=list(color_map.values()))


            df_second=self.tb_se_second_source.to_df()
            df_second['initial_y'] =  0
            length=10
            factor=-1
            df_second['final_y'] = factor*df_second['Power'] + length  
            df_second=df_second[['Frequency','initial_y','final_y','Power','Mode']]
            self.inverted_slider_source = ColumnDataSource(df_second.to_dict('list'))
            # self.env.fig_other_periodogram.ray(x="Frequency",
            #                             y=-300,
            #                             source= self.inverted_slider_source,
            #                             length=300, 
            #                             angle=np.pi/2,
            #                             name='vertical_inverted_line',
            #                             line_dash='dotted',
            #                             color={'field': 'Mode', 
            #                             'transform': color_mapper})
            
            self.env.fig_other_periodogram.segment(x0='Frequency', 
                                                   y0='initial_y', 
                                                   x1='Frequency', 
                                                   y1='final_y',
                                                   name='vertical_inverted_line',
                                                   source= self.inverted_slider_source, 
                                                   line_dash='dotted', 
                                                   color={'field': 'Mode', 
                                                   'transform': color_mapper})


            self.env.inverted_slider.on_change(
                'value',self.update_inverted_slider)
        # else:
        #     self.update_inverted_slide(0,0,0)

    def update_inverted_slider(self, attr,old, new):
        """
        Callback for when the 'Inverted Slider' value changes.

        Updates the `self.env.inverted_line_xvalue_text` input with the new
        slider value, and then calls `update_inverted_line()` to refresh the
        plotted lines.

        Args:
            attr: The attribute that changed (unused).
            old: The old slider value (unused).
            new: The new slider value.
        """
        self.env.inverted_line_xvalue_text.value = str(
                            self.env.inverted_slider.value)
        self.update_inverted_line()

    def update_inverted_line(self):
        """
        Updates the plotted "inverted lines" based on current UI parameters.

        - Adjusts the start and end range of `self.env.inverted_slider` based on
          `self.env.inverted_slider_max_value_text`.
        - Recalculates the positions of the inverted lines using data from
          `self.tb_se_second_source` and parameters from various text inputs
          (`inverted_line_initial_y_text`, `inverted_line_length_text`,
          `inverted_line_scale_text`, `inverted_line_xvalue_text`).
        - Updates `self.inverted_slider_source.data` with the new line coordinates.
        - Toggles the visibility of these lines based on
          `self.env.check_show_inverted_lines.active`.
        """
        sld_val = float(self.env.inverted_slider_max_value_text.value)
        self.env.inverted_slider.start = -1*sld_val
        self.env.inverted_slider.end = 1*sld_val


        df_second=self.tb_se_second_source.to_df()
        df_second['initial_y'] = float(self.env.inverted_line_initial_y_text.value)
        length=float(self.env.inverted_line_length_text.value)
        factor=float(self.env.inverted_line_scale_text.value)
        df_second['final_y'] = factor*df_second['Power'] + length  
        df_second=df_second[['Frequency','initial_y','final_y','Power','Mode']]
        value = float(self.env.inverted_line_xvalue_text.value)
        df_second['Frequency']=df_second['Frequency']+value
        old_data = ColumnDataSource(df_second.to_dict('list'))
        self.inverted_slider_source.data=dict(old_data.data)

        if self.env.check_show_inverted_lines.active[0]==0:
            # print('Showing inverted line')
            # self.env.fig_other_periodogram.select('vertical_line').visible = True
            self.env.fig_other_periodogram.select(
                'vertical_inverted_line').visible = True
        else:
            # print('Turn off inverted line')
            old_data = ColumnDataSource(data=dict())
            self.inverted_slider_source.data=dict(old_data.data)

            # self.env.fig_other_periodogram.select('vertical_line').visible = False
            self.env.fig_other_periodogram.select(
                'vertical_inverted_line').visible = False



    def _make_echelle_elements(self, deltanu, cmap='hot',
                               minimum_frequency=None, maximum_frequency=None, smooth_filter_width=None,
                               scale='linear', width=490, height=340, title='Echelle'):
        """
        Helper function to create Bokeh figure and widgets for the echelle diagram.

        This function constructs the main Bokeh figure for the echelle diagram,
        configures its axes and tooltips. It sets up a `LogColorMapper` for the
        echelle image based on the power distribution. An image glyph is added to
        the figure, sourced from `self.env.tb_echelle_diagram`.
        It also creates a `RangeSlider` (`stretch_slider`) for adjusting the
        color stretch of the echelle image and defines its callback.

        Args:
            deltanu (Quantity): The large frequency separation, used for axis labeling.
            cmap (str, optional): Colormap name (though self.palette is often used). Defaults to 'hot'.
            minimum_frequency (float, optional): Minimum frequency (not directly used for plot range here).
            maximum_frequency (float, optional): Maximum frequency (not directly used for plot range here).
            smooth_filter_width (float, optional): Smoothing width (not used here).
            scale (str, optional): Power scale ('linear' or 'log'). Defaults to 'linear'.
            width (int, optional): Width of the figure. Defaults to 490. (Figure width is actually set to 800).
            height (int, optional): Height of the figure. Defaults to 340. (Figure height is actually set to 800).
            title (str, optional): Title for the echelle diagram figure. Defaults to 'Echelle'.

        Returns:
            tuple:
                - fig (Figure): The Bokeh figure object for the echelle diagram.
                - stretch_slider (RangeSlider): The Bokeh RangeSlider for color stretch.
        """

        freq = self.env.tb_other_periodogram.data['frequency'] * \
            self.env.frequency_unit
        ep = self.env.tb_echelle_diagram.data['image']*self.env.power_unit
        x_f = self.env.tb_echelle_diagram.data['x_f']*self.env.frequency_unit
        y_f = self.env.tb_echelle_diagram.data['y_f']*self.env.frequency_unit

        fig = figure(width=800, height=800,
                     # x_range=(0, 1), y_range=(y_f[0].value, y_f[-1].value),
                     title=title, tools='pan,box_zoom,reset,lasso_select',
                     toolbar_location="above",
                     border_fill_color="white", tooltips=self.env.TOOLTIPS)

        fig.yaxis.axis_label = r'Frequency [{}]'.format(freq.unit.to_string())
        fig.xaxis.axis_label = r'Frequency / {:.3f} Mod. 1'.format(deltanu)
        if ep.value.any():
            lo, hi = np.nanpercentile(ep.value, [0.1, 99.9])
        else:
            lo=10
            hi=100
        vlo, vhi = 0.3 * lo, 1.7 * hi
        vstep = (lo - hi)/500
        color_mapper = LogColorMapper(palette=self.palette, low=lo, high=hi)

        fig.image(image='image',
                  x='xmin',
                  y='ymin',
                  dw='dw',
                  dh='dh',
                  color_mapper=color_mapper,
                  name='img',
                  source=self.env.tb_echelle_diagram)
        # from bokeh.models import Div
        # style = Div(
        #     text="""
        # <style>
        #     .custom-slider .bk-input-group {
        #         height:300px;
        #     }
        # </style>
        # """
        # )
        stretch_slider = RangeSlider(start=vlo,
                                     end=vhi,
                                     step=vstep,
                                     title='',
                                     value=(lo, hi),
                                    #  orientation='vertical',
                                    width=700,
                                    height=50,
                                     direction='ltr',
                                    # css_classes=["custom- slider"],
                                     show_value=True,
                                     #sizing_mode='fixed',
                                     name='stretch')

        def stretch_change_callback(attr, old, new):
            """TPF stretch slider callback."""
            fig.select('img')[0].glyph.color_mapper.high = new[1]
            fig.select('img')[0].glyph.color_mapper.low = new[0]

        stretch_slider.on_change('value', stretch_change_callback)

        return fig, stretch_slider

    def interact_echelle(self, notebook_url="localhost:8888", **kwargs):
        """
        Sets up the interactive components of the echelle diagram.

        This method creates the main echelle diagram figure and associated
        sliders for delta Nu (`dnu_slider`) and color stretch
        (`stretch_sliderint`). It defines callbacks for these widgets to
        update the echelle diagram when their values change.
        The `_make_echelle_elements` helper function is used to create the
        figure and stretch slider. Navigation buttons for delta Nu are also
        initialized here.

        Args:
            notebook_url (str, optional): Location of the Jupyter notebook page.
                Defaults to "localhost:8888". (Primarily for Bokeh server setups).
            **kwargs: Additional keyword arguments passed to `_make_echelle_elements`.
        """
        # try:
        #     import bokeh
        #     if bokeh.__version__[0] == '0':
        #         warnings.warn(
        #             "interact() requires Bokeh version 1.0 or later", LightkurveWarning)
        # except ImportError:
        #     log.error("The interact() tool requires the `bokeh` Python package; "
        #               "you can install bokeh using e.g. `conda install bokeh`.")
        #     return None

        # maximum_frequency = kwargs.pop(
        #     'maximum_frequency', self.periodogram.frequency.max().value)
        # minimum_frequency = kwargs.pop(
        #     'minimum_frequency', self.periodogram.frequency. min().value)

        dnu = SeismologyQuantity(quantity=self.env.dnu_val*u.microhertz,
                                 name='deltanu', method='echelle')

        def create_interact_ui():
            self.env.fig_tpfint, self.env.stretch_sliderint = self._make_echelle_elements(deltanu=dnu,
                                                                                        #   maximum_frequency=maximum_frequency,
                                                                                        #   minimum_frequency=minimum_frequency,
                                                                                          **kwargs)
            # maxdnu = self.periodogram.frequency.max().value/5
            maxdnu = self.env.maxdnu
            # Interactive slider widgets
            self.env.dnu_slider = Slider(start=0.01,
                                         end=maxdnu,
                                         value=dnu.value,
                                         step=0.01,
                                         title="Delta Nu",
                                         width=290)
            self.env.r_button = Button(
                label=">", button_type=self.env.button_type, width=30)
            self.env.l_button = Button(
                label="<", button_type=self.env.button_type, width=30)
            self.env.rr_button = Button(
                label=">>", button_type=self.env.button_type, width=30)
            self.env.ll_button = Button(
                label="<<", button_type=self.env.button_type, width=30)

            def update(attr, old, new):
                """Callback to take action when dnu slider changes"""
                dnu = SeismologyQuantity(quantity=self.env.dnu_slider.value*self.env.frequency_unit,
                                         name='deltanu',
                                         method='echelle')

                self.make_tb_echelle_diagram()
                self.make_grid()

                self.env.fig_tpfint.xaxis.axis_label = r'Frequency / {:.3f} Mod. 1'.format(
                    dnu)
                self.env.dnu_val = self.env.dnu_slider.value
                self.env.dnu_text.value = str(self.env.dnu_slider.value)

            def go_right_by_one_small():
                """Step forward in time by a single cadence"""
                existing_value = self.env.dnu_slider.value
                if existing_value < self.env.maxdnu:
                    self.env.dnu_slider.value = existing_value + 0.1

            def go_left_by_one_small():
                """Step back in time by a single cadence"""
                existing_value = self.dnu_slider.value
                if existing_value > 0:
                    self.env.dnu_slider.value = existing_value - 0.1

            def go_right_by_one():
                """Step forward in time by a single cadence"""
                existing_value = self.env.dnu_slider.value
                if existing_value < self.env.maxdnu:
                    self.env.dnu_slider.value = existing_value + 1

            def go_left_by_one():
                """Step back in time by a single cadence"""
                existing_value = self.env.dnu_slider.value
                if existing_value > 0:
                    self.env.dnu_slider.value = existing_value - 1

            self.env.dnu_slider.on_change('value', update)
            self.env.r_button.on_click(go_right_by_one_small)
            self.env.l_button.on_click(go_left_by_one_small)
            self.env.rr_button.on_click(go_right_by_one)
            self.env.ll_button.on_click(go_left_by_one)

        create_interact_ui()

    def apollinaire_echelle(self, freq, PSD, dnu, twice=False, fig=None, index=111,
                            figsize=(16, 16), title=None,
                            smooth=10, cmap='cividis', cmap_scale='linear',
                            mode_freq=None, mode_freq_err=None,
                            vmin=None, vmax=None, scatter_color='white', fmt='+', ylim=None,
                            shading='gouraud', mfc='none', ms=20, index_offset=None,
                            mec=None, xlabel=None, ylabel=None, **kwargs):
            """
            Builds the echelle diagram data from a given Power Spectral Density (PSD).

            This method takes frequency and PSD arrays, and a delta Nu value,
            and reshapes the PSD into an echelle diagram format. It determines the
            number of slices and the length of each slice based on delta Nu and
            the frequency resolution.

            This is largely based on the echelle diagram generation logic from the
            Apollinaire library or similar tools.

            Args:
                freq (ndarray): Input vector of frequencies.
                PSD (ndarray): Input vector of power. Must be of same size as freq.
                dnu (float): The large frequency separation used to cut slices.
                twice (bool, optional): If True, slice using 2 * dnu. Defaults to False.
                fig (matplotlib.figure.Figure, optional): Matplotlib figure (not used in current Bokeh context).
                index (int, optional): Subplot index (not used in current Bokeh context).
                figsize (tuple, optional): Figure size (not used in current Bokeh context).
                title (str, optional): Plot title (not used in current Bokeh context).
                smooth (int, optional): Window size for rolling mean smoothing of PSD (not directly used here, smoothing expected before call).
                cmap (str, optional): Colormap (handled by Bokeh).
                cmap_scale (str, optional): Scale for colormap ('linear' or 'logarithmic').
                mode_freq (ndarray or tuple, optional): Frequencies of modes to overplot (not used here).
                mode_freq_err (ndarray or tuple, optional): Uncertainties for mode_freq (not used here).
                vmin (float, optional): Minimum value for colormap.
                vmax (float,optional): Maximum value for colormap.
                scatter_color (str, optional): Color for scatter points (not used here).
                fmt (str or tuple, optional): Format for error bars (not used here).
                ylim (tuple, optional): Y-axis limits for plot.
                shading (str, optional): Shading for pcolormesh (e.g., 'gouraud', 'flat').
                mfc (str, optional): Marker face color.
                ms (float, optional): Marker size.
                index_offset (int, optional): Offset for slicing PSD and freq arrays.
                mec (str, optional): Marker edge color.
                xlabel (str, optional): X-axis label.
                ylabel (str, optional): Y-axis label.
                **kwargs: Additional arguments.

            Returns:
                tuple:
                    - ed (ndarray): The 2D echelle diagram power array.
                    - x_freq (ndarray): The x-coordinates (frequency modulo dnu).
                    - y_freq (ndarray): The y-coordinates (base frequency of each slice).
                    - xx (list): Flattened x-coordinates of the full grid.
                    - yy (list): Flattened y-coordinates of the full grid.
                    - freq_values (list): Flattened original frequency values on the grid.
                    - power_values (list): Flattened power values on the grid.
            """

        # if cmap_scale not in ['linear', 'logarithmic'] :
        #     raise Exception ("cmap_scale should be set to 'linear' or 'logarithmic'.")

        # if cmap_scale=='logarithmic':
        #     norm = colors.LogNorm (vmin=vmin, vmax=vmax)
        # elif cmap_scale=='linear' :
        #     norm = colors.Normalize (vmin=vmin, vmax=vmax)

        # if smooth != 1 :
        #     PSD = pd.Series(data=PSD).rolling (window=smooth, min_periods=1,
        #                             center=True).mean().to_numpy()

        # if twice==True :
        #     dnu = 2.*dnu
        # print('freq',freq)
        res = freq[2]-freq[1]

        # if index_offset is not None :
        #     PSD = PSD[index_offset:]
        #     freq = freq[index_offset:]

        n_slice = int(np.floor_divide(freq[-1]-freq[0], dnu))
        len_slice = int(np.floor_divide(dnu, res))

        if (n_slice*len_slice > PSD.size):
            len_slice -= 1

        ed = PSD[:len_slice*n_slice]
        ed = np.reshape(ed, (n_slice, len_slice))

        freq_ed = freq[:len_slice*n_slice]
        freq_ed = np.reshape(freq_ed, (n_slice, len_slice))
        # x_freq = freq_ed[0,:] - freq_ed[0,0]
        x_freq = freq_ed[0, :]
        y_freq = freq_ed[:, 0]

        # if fig is None :
        #     fig = plt.figure (figsize=figsize)
        # ax = fig.add_subplot (index)
        # ax.pcolormesh (x_freq, y_freq, ed, cmap=cmap,
        #                 norm=norm, shading=shading)

        # if mode_freq is not None :
        #     if type (mode_freq) is not tuple :
        #     mode_freq = (mode_freq,)
        #     mode_freq_err = (mode_freq_err,)
        #     if type (scatter_color) is str :
        #     scatter_color = np.repeat (scatter_color, len (mode_freq))
        #     if type (fmt) is str :
        #     fmt = np.repeat (fmt, len (mode_freq))
        #     if type (ms) in [float, int] :
        #     ms = np.repeat (ms, len (mode_freq))
        #     if type (mfc) is str :
        #     mfc = np.repeat (mfc, len (mode_freq))
        #     if mec is None :
        #     mec = scatter_color
        #     if type (mec) is str :
        #     mec = np.repeat (mec, len (mode_freq))

        # for m_freq, m_freq_err, color, m_fmt, s, fc, edge in zip (mode_freq, mode_freq_err,
        #                                                         scatter_color, fmt, ms, mfc, mec) :
        # x_mode = np.zeros (m_freq.size)
        # y_mode = np.zeros (m_freq.size)
        # for ii, elt in enumerate (m_freq) :
        #     aux_1 = elt - y_freq
        #     aux_2 = y_freq[aux_1>0]
        #     aux_1 = aux_1[aux_1>0]
        #     jj = np.argmin (aux_1)
        #     x_mode[ii] = aux_1[jj]
        #     y_mode[ii] = aux_2[jj]
        # print (x_mode[ii], y_mode[ii], x_mode[ii]+y_mode[ii], elt)
        # ax.errorbar (x=x_mode, y=y_mode, xerr=m_freq_err, fmt=m_fmt, color=color, barsabove=True,
        #             mfc=fc, ms=s, mec=edge, **kwargs)

        # if xlabel is None :
        #     xlabel = r'$\nu$ mod. {:.1f} $\mu$Hz'.format (len_slice*res)
        # if ylabel is None :
        #     ylabel = r'$\nu$ ($\mu$Hz)'
        # ax.set_xlabel (xlabel)
        # ax.set_ylabel (ylabel)

        # ax.set_xlim (left=0, right=x_freq[-1])

        # if ylim is not None :
        #     ax.set_ylim (ylim[0], ylim[1])

        # if title is not None :
        #     ax.set_title (title)

        value = freq_ed
        x = x_freq
        y = y_freq
        xx, yy = np.meshgrid(x, y, sparse=False)
        xx = xx.reshape(-1, 1).flatten().tolist()
        yy = yy.reshape(-1, 1).flatten().tolist()
        freq_values = value.reshape(-1, 1).flatten().tolist()

        power_values = ed.reshape(-1, 1).flatten().tolist()

        return ed, x_freq, y_freq, xx, yy, freq_values, power_values

    def clear_se_table1(self):
        """Clears all data from the first mode selection table (Table 1)."""

        old_data = ColumnDataSource(
            data=dict(Slicefreq=[], Frequency=[], Power=[],Mode=[], xx=[]))
        self.tb_se_first_source.data = dict(old_data.data)

    def clear_se_table2(self):
        """Clears all data from the second mode selection table (Table 2)."""

        old_data = ColumnDataSource(
            data=dict(Slicefreq=[], Frequency=[], Power=[],Mode=[], xx=[]))
        self.tb_se_second_source.data = dict(old_data.data)

    def find_peak_frequencies(self):
        """
        Identifies and selects peak frequencies within currently selected echelle grid regions.

        For the points currently selected in `self.env.tb_grid_source` (the echelle
        diagram grid), this function groups them by their y-coordinate (`yy`,
        representing frequency slices). Within each group (slice), it finds the point
        with the maximum power.
        It then updates the selection in `self.env.tb_grid_source` to only these
        peak frequencies and calls `get_all_selection_button()` to populate Table 1
        with these peaks. It also clears selections on the main periodogram.
        """

        df_se = pd.DataFrame()
        yy = self.env.tb_grid_source.data['yy']
        xx = self.env.tb_grid_source.data['xx']
        freq_values = self.env.tb_grid_source.data['freq_values']
        power_values = self.env.tb_grid_source.data['power_values']

        df_se['freq_values'] = freq_values
        df_se['power_values'] = power_values
        df_se['xx'] = xx
        df_se['yy'] = yy

        se_indices = self.env.tb_grid_source.selected.indices
        real_freq = df_se.freq_values.loc[se_indices]
        real_power = df_se.power_values.loc[se_indices]
        xx_f = df_se.xx.loc[se_indices]
        yy_f = df_se.yy.loc[se_indices]
        df_se_freq = pd.DataFrame()
        df_se_freq['indices'] = se_indices
        df_se_freq['real_freq'] = real_freq.values
        df_se_freq['real_power'] = real_power.values
        df_se_freq['xx'] = xx_f.values
        df_se_freq['yy'] = yy_f.values

        # print(' All selected freq', df_se_freq)
        max_indices = df_se_freq.groupby('yy')['real_power'].idxmax()
        # print(' Max indices', max_indices)
        df_se_freq = df_se_freq.loc[max_indices]
        # print(' filetered', df_se_freq)

        self.tb_other_periodogram.selected.indices = list([])


        self.env.tb_grid_source.selected.indices = df_se_freq['indices'].to_list(
        )
        self.clear_se_table1()
        self.get_all_selection_button()
        #print('Selected indices', self.env.tb_grid_source.selected.indices)

        # Clear prd selections

        # self.selection_grid_to_prd_fig(0,0,0)
        # self.update_plot(0, 0, 0)

        #self.get_all_selection_button()


    def selection_prd_to_grid_fig(self, attrname, old, new):
        """
        Synchronizes selections from the main periodogram to the echelle diagram grid.

        When points are selected on `self.env.tb_other_periodogram`, this callback
        finds the corresponding points (by frequency) in `self.env.tb_grid_source`
        and selects them. This helps visualize where periodogram selections fall
        on the echelle diagram.

        Args:
            attrname: The attribute that changed (e.g., 'indices').
            old: The old selection.
            new: The new selection (list of selected indices in periodogram).
        """
        
        se_indices = self.tb_other_periodogram.selected.indices

        df_prd = self.env.tb_other_periodogram.to_df()
        df_prd = df_prd.loc[se_indices]

        selected_freq = list(np.round(df_prd.frequency.values, self.env.freq_round))

        se_indices = self.env.tb_grid_source.selected.indices
        df_grid = self.env.tb_grid_source.to_df()

        df_grid['freq_values'] = df_grid['freq_values'].round(self.env.freq_round)
        
        df_grid = df_grid.query('freq_values==@selected_freq')
        
        all_list = df_grid.index.to_list() + se_indices 

        #print('all list', all_list)
        if set(all_list) != set(se_indices):
            self.tb_grid_source.selected.indices = list(set(all_list))
            self.update_plot(0, 0, 0)
        self.env.fig_other_periodogram.x_range.start = int(self.env.minimum_frequency)
        self.env.fig_other_periodogram.x_range.end = int(self.env.maximum_frequency)


    def selection_grid_to_table_fig(self, attrname, old, new):
        """
        Populates Table 1 with data from selected points on the echelle diagram grid.

        When points are selected in `self.env.tb_grid_source`, this callback
        extracts their 'yy' (Slicefreq), 'freq_values' (Frequency),
        'power_values' (Power), 'Mode', and 'xx' attributes.
        This data is then added to `self.tb_se_first_source` (Table 1),
        avoiding duplicate entries based on frequency.

        Args:
            attrname: The attribute that changed (e.g., 'indices').
            old: The old selection.
            new: The new selection (list of selected indices in grid).
        """
        
        se_indices = self.env.tb_grid_source.selected.indices
        # print('Grid2Table se_indices', se_indices)
        df_grid = self.env.tb_grid_source.to_df()
        df_grid = df_grid.loc[se_indices]
        df_table = self.tb_se_first_source.to_df()
        df_grid.rename(columns={'yy':'Slicefreq', 
                       'freq_values':'Frequency',
                       'power_values':'Power'},
                       inplace=True,)
        df_grid = df_grid[['Slicefreq', 'Frequency', 'Power', 'Mode','xx']]
        all_data = pd.concat([df_table, df_grid],ignore_index=True)
        # print(all_data)
        all_data['Frequency'] = all_data['Frequency'].round(self.env.freq_round)
        all_data = all_data.drop_duplicates(subset=['Frequency'])
        #print(all_data.to_dict())
        #old_data = ColumnDataSource.from_df(all_data)
        df=all_data
        old_data = ColumnDataSource(
                    data=dict(Slicefreq = df['Slicefreq'].to_list(), 
                            Frequency = df['Frequency'].to_list(), 
                            Power = df['Power'].to_list(),
                            Mode = df['Mode'].to_list(),
                            xx = df['xx'].to_list()
                            ))

        self.tb_se_first_source.data = dict(old_data.data)




    def selection_grid_to_prd_fig(self, attrname, old, new):
        """
        Synchronizes selections from the echelle diagram grid to the main periodogram.

        (Note: Docstring in code says "This function will not be used, slowing the system")
        When points are selected on `self.env.tb_grid_source`, this callback
        finds the corresponding points (by frequency) in `self.env.tb_other_periodogram`
        and selects them.

        Args:
            attrname: The attribute that changed (e.g., 'indices').
            old: The old selection.
            new: The new selection (list of selected indices in grid).
        """

        df_se = pd.DataFrame()
        yy = self.env.tb_grid_source.data['yy']
        xx = self.env.tb_grid_source.data['xx']
        freq_values = self.env.tb_grid_source.data['freq_values']

        df_se['xx'] = xx
        df_se['yy'] = yy
        df_se['freq_values'] = freq_values

        se_indices = self.env.tb_grid_source.selected.indices
        slice_freq = df_se.loc[se_indices]['yy']
        mod_val = df_se.loc[se_indices]['xx']

        real_freq = slice_freq+(self.dnu_val*mod_val)
        real_freq = real_freq.round(self.env.freq_round)
        real_freq = mod_val

        real_freq = df_se.freq_values.loc[se_indices]

        real_freq = np.round(real_freq, self.env.freq_round)
        real_freq = real_freq.tolist()

        df_prd = self.env.tb_other_periodogram.to_df()
        df_prd['frequency'] = df_prd['frequency'].round(self.env.freq_round)
        df_prd = df_prd.query('frequency==@real_freq')
        all_list = self.env.tb_other_periodogram.selected.indices + df_prd.index.to_list()
        
        
        if set(all_list) != set(self.env.tb_other_periodogram.selected.indices):
            self.env.tb_other_periodogram.selected.indices = list(set(all_list))

        

    def selection_table_to_prd_fig(self, attrname, old, new):
        """
        Synchronizes selections from Table 1 to the main periodogram.

        When data in `self.tb_se_first_source` changes (implicitly, when items
        are selected or added), this function would take the frequencies from
        Table 1 and select corresponding points in `self.env.tb_other_periodogram`.

        Args:
            attrname: The attribute that changed.
            old: The old data/selection.
            new: The new data/selection.
        """

        df_table = self.tb_se_first_source.to_df()
        selected_freq = df_table['Frequency'].round(self.env.freq_round)
        selected_freq = selected_freq.to_list()

        df_prd = self.env.tb_other_periodogram.to_df()
        df_prd['frequency'] = df_prd['frequency'].round(self.env.freq_round)  
        df_prd = df_prd.query('frequency==@selected_freq')

        all_list = self.env.tb_other_periodogram.selected.indices + df_prd.index.to_list()
        
        
        if set(all_list) != set(self.env.tb_other_periodogram.selected.indices):
            self.env.tb_other_periodogram.selected.indices = list(set(all_list))


    def selection_table2_to_prd_fig(self, attrname, old, new):
        """
        Synchronizes selections from Table 2 to the main periodogram.

        Similar to `selection_table_to_prd_fig` but operates on
        `self.tb_se_second_source` (Table 2, the final selection table).
        When data in Table 2 changes, this function selects corresponding
        frequencies in the main periodogram.

        Args:
            attrname: The attribute that changed.
            old: The old data/selection.
            new: The new data/selection.
        """

        df_table = self.tb_se_second_source.to_df()
        selected_freq = df_table['Frequency'].round(self.env.freq_round)
        selected_freq = selected_freq.to_list()

        df_prd = self.env.tb_other_periodogram.to_df()
        df_prd['frequency'] = df_prd['frequency'].round(self.env.freq_round)  
        df_prd = df_prd.query('frequency==@selected_freq')

        all_list = self.env.tb_other_periodogram.selected.indices + df_prd.index.to_list()
        
        
        if set(all_list) != set(self.env.tb_other_periodogram.selected.indices):
            self.env.tb_other_periodogram.selected.indices = list(set(all_list))



    def get_all_selection_button(self):
        """
        Callback for the "Get Selection" button.

        This function triggers a chain of selection synchronization methods
        to ensure consistency between the echelle grid, periodogram, and Table 1.
        Specifically, it calls:
        - `selection_grid_to_prd_fig()`: echelle grid -> periodogram
        - `selection_prd_to_grid_fig()`: periodogram -> echelle grid
        - `selection_grid_to_table_fig()`: echelle grid -> Table 1
        A message is published to the UI.
        (Some parts of the original code here are commented out, suggesting
         different or more complex synchronization logic might have been tried).
        """

       
        # self.selection_grid_to_prd_fig(0,0,0)

        # self.selection_prd_to_grid_fig(0,0,0)
        
        # self.selection_grid_to_table_fig(0,0,0)
        # self.selection_table_to_prd_fig(0,0,0)
        # self.selection_prd_to_grid_fig(0,0,0)
        # self.selection_grid_to_table_fig(0,0,0)
        # self.selection_table_to_prd_fig(0,0,0)
        # self.selection_prd_to_grid_fig(0,0,0)
        
        # self.selection_grid_to_table_fig(0,0,0)
        # self.selection_table_to_prd_fig(0,0,0)
        # self.selection_prd_to_grid_fig(0,0,0)

        # #Ideal Way
        # self.selection_grid_to_table_fig(0,0,0)
        # self.selection_prd_to_table_fig(0,0,0)
        # self.selection_table_to_grid_fig(0,0,0)
        # self.selection_table_to_prd_fig(0,0,0)
        self.publish_message('Getting Selection')
        self.selection_grid_to_prd_fig(0,0,0)
        self.selection_prd_to_grid_fig(0,0,0)
        self.selection_grid_to_table_fig(0,0,0)
        self.publish_message('Ready')



    def clear_se_grid_prd(self):
        """
        Clears selections on both the main periodogram and the echelle diagram grid.

        Sets `selected.indices` to an empty list for both
        `self.tb_other_periodogram` and `self.env.tb_grid_source`.
        Calls `update_plot()` to refresh the visuals.
        """
        self.tb_other_periodogram.selected.indices = list([])
        self.env.tb_grid_source.selected.indices = list([])
        self.update_plot(0, 0, 0)



    def click_mode_apply_button(self):
        """
        Applies the selected mode label to frequencies currently in Table 1.

        Takes the mode label selected in `self.env.select_mode_menu` and
        applies it to the 'Mode' column for all frequencies listed in
        `self.tb_se_first_source`. It updates the corresponding entries
        in the main periodogram data source (`self.env.tb_other_periodogram`)
        and the echelle grid data source (`self.env.tb_grid_source`) to reflect
        this mode assignment. Finally, it clears Table 1.
        """
        df_first=self.tb_se_first_source.to_df()
        df_first['Frequency']=df_first['Frequency'].round(
            self.env.freq_round)
        list_freq = df_first['Frequency'].to_list()
        
        print('Drop down value is', self.env.select_mode_menu.value,list_freq)
        #ind = self.env.tb_grid_source.selected.indices 

        df_grid = self.env.tb_grid_source.to_df()
        df_grid['freq_values'] = df_grid['freq_values'].round(
            self.env.freq_round)
        ind = df_grid.query('freq_values == @list_freq').index

        df_grid.loc[ind,'Mode'] = self.env.select_mode_menu.value
        old_data = ColumnDataSource(df_grid.to_dict('list'))
        self.env.tb_grid_source.data = dict(old_data.data)

        #ind = self.env.tb_other_periodogram.selected.indices

        df_other = self.env.tb_other_periodogram.to_df()
        df_other['frequency'] = df_other['frequency'].round(
            self.env.freq_round)
        ind = df_other.query('frequency == @list_freq').index

        df_other.loc[ind,'Mode'] = self.env.select_mode_menu.value
        print('df_other',df_other.loc[ind])
        old_data = ColumnDataSource(df_other.to_dict('list'))
        self.env.tb_other_periodogram.data = dict(old_data.data)
        self.selection_table_to_prd_fig(0,0,0)
        self.selection_prd_to_grid_fig(0,0,0)
        self.clear_se_table1()
        self.selection_grid_to_table_fig(0,0,0)


    # def get_index_from_frequency(self,df=None,name='Frequency',val_list=''):
        
    #     df['name']=df['name'].round(self.env.freq_round)






    def click_move_se_1_2_button(self):
        """
        Moves selected modes from Table 1 to Table 2.

        Filters rows in `self.tb_se_first_source` (Table 1) that match the
        mode currently selected in `self.env.select_mode_menu`.
        These matching rows are removed from Table 1 and appended to
        `self.tb_se_second_source` (Table 2).
        """

        mode = self.env.select_mode_menu.value
        df_table1 = self.tb_se_first_source.to_df()
        df_table1_se = df_table1.query('Mode == @mode')
        print(df_table1_se)
        #df_table1_left = df_table1[~df_table1.index.isin(df_table1_se.index)]
        df_table1_left = df_table1.query('Mode != @mode')
        print(df_table1_left.to_dict('list'))
        old_data = ColumnDataSource(df_table1_left.to_dict('list'))
        self.tb_se_first_source.data = dict(old_data.data)
        # Second table
        df_table2 = self.tb_se_second_source.to_df()
        #df_table1_se = df_table1.query('Mode == @mode')
        all_data = pd.concat([df_table2, df_table1_se], ignore_index=True)

        #all_data['mode_color']= self.assign_mode_color(all_data.Mode.values)
        #df_table2
        old_data = ColumnDataSource(all_data.to_dict('list'))
        self.tb_se_second_source.data = dict(old_data.data)

    def click_move_se_2_1_button(self):
        """
        Moves selected modes from Table 2 back to Table 1.

        Filters rows in `self.tb_se_second_source` (Table 2) that match the
        mode currently selected in `self.env.select_mode_menu`.
        These matching rows are removed from Table 2.
        It then finds the corresponding full data for these frequencies from the
        echelle grid (`self.env.tb_grid_source`) and appends them to
        `self.tb_se_first_source` (Table 1), ensuring no duplicates in Table 1.
        """
        # self.selection_table2_to_prd_fig(0,0,0)
        # self.selection_prd_to_grid_fig(0,0,0)
        # self.selection_grid_to_table_fig(0,0,0)

        mode = self.env.select_mode_menu.value
        df_table2 = self.tb_se_second_source.to_df()
        df_table2_se = df_table2.query('Mode == @mode')
        print('mode_selected',df_table2_se)
        #df_table1_left = df_table1[~df_table1.index.isin(df_table1_se.index)]
        df_table2_left = df_table2.query('Mode != @mode')
        # print(df_table2_left.to_dict('list'))

        old_data = ColumnDataSource(df_table2_left.to_dict('list'))
        self.tb_se_second_source.data = dict(old_data.data)
        # Second table
        df_table1 = self.tb_se_first_source.to_df()
        #df_table1_se = df_table1.query('Mode == @mode')
        
        selected_freq = list(np.round(df_table2_se.Frequency.values, self.env.freq_round))
        df_grid = self.env.tb_grid_source.to_df()
        df_grid['freq_values'] = df_grid['freq_values'].round(self.env.freq_round)
        df_grid = df_grid.query('freq_values==@selected_freq')
        df_grid.rename(columns={'yy':'Slicefreq', 
                        'freq_values':'Frequency',
                        'power_values':'Power'},
                        inplace=True,)
        
        df_final = df_grid[['Slicefreq', 'Frequency', 'Power', 'Mode','xx']]
        df_final['mode_color'] = '' 
        
        all_data = pd.concat([df_table1, df_final], ignore_index=True)
        all_data =all_data.drop('mode_color',axis=1)
        print(all_data)
        all_data = all_data.drop_duplicates(subset=['Frequency'],
                                            ignore_index=True)
        #df_table2
        print(all_data.to_dict('list'))
        old_data = ColumnDataSource(all_data.to_dict('list'))
        self.tb_se_first_source.data = dict(old_data.data)

        #self.selection_table_to_prd_fig(0,0,0)
        #self.selection_prd_to_grid_fig(0,0,0)
        # self.selection_grid_to_table_fig(0,0,0)


    def assign_mode_color(self,modes):
        """
        Assigns colors to modes based on their 'l' value.

        (Currently seems unused or part of an incomplete feature for coloring
        Table 2 directly, as `mode_color` column isn't standard in tables).
        Takes a list of mode labels (e.g., '0', '1', '999') and maps them to
        colors defined in `self.mode_color_map`.

        Args:
            modes (iterable): An iterable of mode labels (as strings or convertible to strings).

        Returns:
            list: A list of color strings corresponding to the input modes.
        """
        val=list(modes)
        val= map(str, val)

        val = list(map(lambda x: x.replace('999', self.mode_color_map[-1]),val)) # Should be self.mode_color_map['999']
        val = list(map(lambda x: x.replace('0', self.mode_color_map[0]), val))   # Should be self.mode_color_map['0']
        val = list(map(lambda x: x.replace('1', self.mode_color_map[1]), val))   # etc.
        val = list(map(lambda x: x.replace('2', self.mode_color_map[2]), val))
        return val
    
    def trim_frequency(self):
        """
        Reloads and filters the periodogram data based on current frequency limits and selected grid type.

        - Determines the source of frequency/power data based on `self.env.select_grid_menu.value`:
            - 'Obs': Reads from FITS file using `read_fits_get_fp()`.
            - 'Syn': Calculates synthetic spectrum using `calculate_synthetic_psd()` and uses synthetic power.
            - 'Sub': Calculates synthetic spectrum and uses subtracted power (observed - synthetic).
        - Converts frequencies to the current `self.env.frequency_unit` and power to `self.env.power_unit`.
        - Filters the data to the range specified by `self.env.minimum_frequency` and
          `self.env.maximum_frequency`.
        - If data remains after filtering, creates a new `lk_prd_module.Periodogram` object,
          stores it in `self.periodogram`, and updates `self.env.tb_other_periodogram.data`.
        - If no data remains, `self.env.tb_other_periodogram.data` is cleared.
        """
        print ('Value of selection:', self.env.select_grid_menu.value)
        if self.env.select_grid_menu.value == 'Obs':
            ff, pp = self.read_fits_get_fp()
            ff = (ff*u.Hz).to(self.env.frequency_unit).value
            pp = pp*self.env.power_unit
            pp = pp.value
        if self.env.select_grid_menu.value == 'Syn':
            data = self.calculate_synthetic_psd()
            ff = data.freq.values
            pp = data.synthetic_psd.values
        if self.env.select_grid_menu.value == 'Sub':
            data = self.calculate_synthetic_psd()
            data['sub_psd'] = data['psd'] - data ['synthetic_psd']
            ff = data.freq.values
            pp = data.sub_psd.values

        min_freq = int(self.env.minimum_frequency)*self.env.frequency_unit
        max_freq = int(self.env.maximum_frequency)*self.env.frequency_unit


        
        ind=(ff <= max_freq.value) & (ff >= min_freq.value)

        f = ff[ind]
        p = pp[ind]
        if f.any():
            f = f*self.env.frequency_unit
            p = p*self.env.power_unit
            mm = ['999']*(len(p))

            #self.env.minimum_frequency = f.min().value
            #self.env.maximum_frequency = f.max().value

            #print(f,p)
            period = lk_prd_module.Periodogram(f, p)
            self.periodogram = period

            old_data= ColumnDataSource(
                data=dict(
                    frequency=list(self.periodogram.frequency.value),
                    power=list(self.periodogram.power.value),
                    Mode = mm,
                    # cuttoff=list(np.array([0])),
                ))  
            self.env.tb_other_periodogram.data=dict(old_data.data)
        else:
            old_data= ColumnDataSource(
                data=dict(
                    frequency=list([]),
                    power=list([]),
                    Mode = list([]),
                    # cuttoff=list(np.array([0])),
                ))
             
            self.env.tb_other_periodogram.data=dict(old_data.data)
             


    def save_table_2(self):
        """
        Saves the contents of Table 2 to a CSV and a PKB file.

        The data from `self.tb_se_second_source` is saved as a CSV file named
        'modes_parameter_selected.csv' in the source's data folder.
        Additionally, it converts the table data into the PKB (peak-bagging)
        format (calculating 'n' values based on delta Nu) and saves it as
        'modes_parameter_selected.pkb' using `apollinaire.peakbagging.save_pkb`.
        A message is published to the UI upon completion.
        """

        df=self.tb_se_second_source.to_df()
        id=self.env.tb_source.data['id'][0]
        data_folder = self.env.tb_source.data['data_folder'][id]
        id_mycatalog=self.env.tb_source.data['id_mycatalog_all'][id]
        file_name=data_folder+'/'+'modes_parameter_selected.csv'
        df.to_csv(file_name,index=False)
        
        df_pkb=pd.DataFrame(columns=[self.env.pkb_columns])
        df_pkb['nu']=df['Frequency'].to_list()
        df_pkb['h']=df['Power'].to_list()
        df_pkb['l']=df['Mode'].astype(float).to_list()
        deltanu = self.env.dnu_val
        df_pkb['n']=np.rint(df['Frequency']/deltanu).astype(int)
        print('deltanu',deltanu)
        print(df_pkb['n'])
        df_pkb =df_pkb.fillna(0)

        pkb_array=df_pkb.values
        file_name=data_folder+'/'+'modes_parameter_selected.pkb'

        apol.peakbagging.save_pkb(file_name,pkb_array)
        print('PKB file saved to ',file_name)
        fulltext='Saving '+ file_name + ' :Ready'
        self.publish_message(text=fulltext)

    def load_pkb_to_second_tab(self, file_name):
        """
        Loads mode data from a PKB file and prepares it for display in Table 2.

        Reads a PKB file (text format) specified by `file_name`.
        It handles both standard (14 columns) and extended (20 columns) PKB formats.
        The loaded mode frequencies ('nu' column) are matched to the closest
        frequencies in the current echelle grid (`self.env.tb_grid_source`)
        to associate them with echelle diagram coordinates ('Slicefreq', 'xx', 'yy').
        It filters out modes where the frequency difference is too large ( > 1 unit).

        Args:
            file_name (str or Path): The path to the PKB file.

        Returns:
            pandas.DataFrame: A DataFrame formatted for `self.tb_se_second_source`,
                              containing 'Slicefreq', 'Frequency', 'Power', 'Mode', 'xx'.
        """

        pkb_array = np.loadtxt (file_name, skiprows=0)
        #pkb_array = apol.peakbagging.fit_tools.read_pkb(file_name)
        if pkb_array.shape[1]==20:
            print('Using extended PKB array')
            pkb_array = pkb_array.reshape(-1, len(self.env.pkb_columns_extended))
            df_pkb = pd.DataFrame(pkb_array,columns=self.env.pkb_columns_extended)          
        else:
            pkb_array = pkb_array.reshape(-1, len(self.env.pkb_columns))
            df_pkb = pd.DataFrame(pkb_array,columns=self.env.pkb_columns)
        df_pkb['nu'] = df_pkb['nu'].astype(float).round(4)

        df_grid = self.env.tb_grid_source.to_df()
        df_grid['freq_values'] = df_grid['freq_values'].round(self.env.freq_round)

        def find_nearest_value(x):
            return df_grid['freq_values'].iloc[(df_grid['freq_values'] - x).abs().idxmin()]
        
        df_pkb['closest_frequency'] = df_pkb['nu'].apply(find_nearest_value)
        df_pkb_merged = df_pkb.merge(df_grid,left_on='closest_frequency', right_on='freq_values', how='left')
        df_pkb_merged['freq_diff']= abs(df_pkb_merged.nu - df_pkb_merged.closest_frequency)
        df_pkb_merged['Mode']=df_pkb_merged['l'].astype(int)
        df_pkb_merged['Mode']=df_pkb_merged['Mode'].astype(str)
        print(df_pkb_merged)
        if not df_pkb_merged.query('freq_diff>1').empty:

            print('Warning frequency with greater than difference 1 is present, change frequency limit')
        df_pkb=df_pkb_merged.query('freq_diff<1')
        df_pkb.rename(columns={'yy':'Slicefreq', 
                       'freq_values':'Frequency',
                       'power_values':'Power'},
                       inplace=True,)
        df_pkb = df_pkb[['Slicefreq', 'Frequency', 'Power', 'Mode','xx']]

        return df_pkb

    def load_table_2(self):
        """
        Loads mode data from a default PKB file into Table 2.

        Constructs the path to a default PKB file ('modes_parameter_selected.pkb')
        located in the current source's data folder.
        Calls `load_pkb_to_second_tab()` to process this file.
        The returned DataFrame is used to update `self.tb_se_second_source.data`.
        Calls `apply_modes()` to update mode assignments on plots based on the loaded data.
        A message is published to the UI.
        """
        self.publish_message(text='Loading pkb')
        id=self.env.tb_source.data['id'][0]
        data_folder = self.env.tb_source.data['data_folder'][id]
        id_mycatalog = self.env.tb_source.data['id_mycatalog_all'][id]
        #file_name = data_folder+'/'+'modes_param.pkb'
        file_name = data_folder+'/'+'modes_parameter_selected.pkb'
        #modes_parameter_selected.pkb


        df=self.load_pkb_to_second_tab(file_name)

        old_data = ColumnDataSource(
                    data=dict(Slicefreq = df['Slicefreq'].to_list(),
                            Frequency = df['Frequency'].to_list(),
                            Power = df['Power'].to_list(),
                            Mode = df['Mode'].to_list(),
                            xx = df['xx'].to_list()
                            ))
        self.tb_se_second_source.data = dict(old_data.data)
        self.apply_modes(df)
        print('Loaded', file_name)
        fulltext='Loaded '+ file_name + ' :Ready'
        self.publish_message(text=fulltext)





        # closest_frequency=df_pkb['closest_frequency'].to_list()
        # print(closest_frequency)
        # df_grid_selected = df_grid.query('freq_values==@closest_frequency')
        # df_pkb['yy'] = df_grid_selected['yy'].to_list()
        # df_pkb['xx'] = df_grid_selected['xx'].to_list()
        # print('selected PKB', df_pkb)



        # df_pkb['nu'] = df_pkb['nu'].astype(str)
        # merged_df = df_grid.merge(df_pkb, left_on='freq_values', right_on='closest_frequency', how='left')
        # merged_df['Mode'] = merged_df['l'].combine_first(merged_df['Mode'])
        # df_grid = merged_df[df_grid_col]
        # self.env.tb_grid_source.data = df_grid.to_dict('list')
        # df_grid.rename(columns={'yy':'Slicefreq', 
        #                'freq_values':'Frequency',
        #                'power_values':'Power'},
        #                inplace=True,)
        # df_grid = df_grid[['Slicefreq', 'Frequency', 'Power', 'Mode','xx']]

        # val='999'
        # df = df_grid.query('Mode!=@val')
        # print(df)
        # old_data = ColumnDataSource(
        #             data=dict(Slicefreq = df['Slicefreq'].to_list(), 
        #                     Frequency = df['Frequency'].to_list(), 
        #                     Power = df['Power'].to_list(),
        #                     Mode = df['Mode'].to_list(),
        #                     xx = df['xx'].to_list()
        #                     ))

        # self.tb_se_second_source.data = dict(old_data.data)


        # filename=mycatalog.filename(
        #     id_mycatalog=self.id_mycatalog,
        #     name='other_psd_save_freq')
        # df = pd.read_csv(filename)
        # df['Mode']=df['Mode'].astype(str)
        # df['Frequency']=df['Frequency'].astype(float)
        # print('Loaded values',df)    
        

        
        
        # old_data = ColumnDataSource(df.to_dict('list'))
        # self.tb_se_second_source.data = dict(old_data.data)
        # print('Load saved Table 2 values',
        #       filename,
        #       self.tb_se_second_source.data)
        # df_second=self.tb_se_second_source.to_df()
        # self.apply_modes(df_second)




        # df_second['Frequency']=df_second['Frequency'].round(
        #     self.env.freq_round)
        # list_freq = df_second['Frequency'].to_list()

        # for mode in df_second.Mode.unique():
        #     print('Applying', mode,df_second.Mode.unique())
        #     list_freq = df_second.query(
        #             'Mode==@mode')['Frequency'].to_list()
            
        #     df_grid = self.env.tb_grid_source.to_df()
        #     df_grid['freq_values'] = df_grid['freq_values'].round(
        #         self.env.freq_round)
        #     ind = df_grid.query('freq_values == @list_freq').index

        #     df_grid.loc[ind,'Mode'] = str(mode)
        #     old_data = ColumnDataSource(df_grid.to_dict('list'))
        #     self.env.tb_grid_source.data = dict(old_data.data)

        #     #ind = self.env.tb_other_periodogram.selected.indices

        #     df_other = self.env.tb_other_periodogram.to_df()
        #     df_other['frequency'] = df_other['frequency'].round(
        #         self.env.freq_round)
        #     ind = df_other.query('frequency == @list_freq').index

        #     df_other.loc[ind,'Mode'] = str(mode)
        #     old_data = ColumnDataself.env.selected_filename_textSource(df_other.to_dict('list'))
        #     self.env.tb_other_periodogram.data = dict(old_data.data)
    def publish_message(self,text=''):
        """
        Displays a status message in the application's message banner.

        The message is prefixed with the current source's ID (`id_mycatalog`).

        Args:
            text (str, optional): The message text to display. Defaults to ''.
        """
        id=self.env.tb_source.data['id'][0]
        id_mycatalog=self.env.tb_source.data['id_mycatalog_all'][id]
        #id_text=self.env.tb_source.data['id_mycatalog'][0]
        #print('Whole data',self.env.tb_source.data )
        full_text = str(id_mycatalog) + ': ' + text
        # full_text = """
        # <h1 style="text-align:center;">Welcome to My Bokeh App</h1>
        # <p style="text-align:center;">This is a centered text banner.</p>
        # """
        
        self.env.message_banner.text=full_text

    def apply_modes(self,table):
        """
        Applies mode assignments from a given table to the periodogram and echelle grid.

        Iterates through unique mode labels in the input `table`. For each mode,
        it identifies the corresponding frequencies and updates the 'Mode' column
        in both `self.env.tb_grid_source` (echelle grid) and
        `self.env.tb_other_periodogram` (main periodogram).
        This visually updates the coloring of points on these plots.

        Args:
            table (pandas.DataFrame): A DataFrame containing at least 'Frequency'
                                      and 'Mode' columns. Typically, this is
                                      `self.tb_se_second_source.to_df()`.
        """
        self.publish_message(text='Applying Modes')
        df_second=table
        df_second['Mode']=df_second['Mode'].astype(str)
        df_second['Frequency']=df_second['Frequency'].round(
        self.env.freq_round)
        for mode in df_second.Mode.unique():
            print('Applying', mode,df_second.Mode.unique())
            list_freq = df_second.query(
                    'Mode==@mode')['Frequency'].to_list()
            
            df_grid = self.env.tb_grid_source.to_df()
            df_grid['freq_values'] = df_grid['freq_values'].round(
                self.env.freq_round)
            ind = df_grid.query('freq_values == @list_freq').index

            df_grid.loc[ind,'Mode'] = str(mode)
            old_data = ColumnDataSource(df_grid.to_dict('list'))
            self.env.tb_grid_source.data = dict(old_data.data)

            #ind = self.env.tb_other_periodogram.selected.indices

            df_other = self.env.tb_other_periodogram.to_df()
            df_other['frequency'] = df_other['frequency'].round(
                self.env.freq_round)
            ind = df_other.query('frequency == @list_freq').index

            df_other.loc[ind,'Mode'] = str(mode)
            old_data = ColumnDataSource(df_other.to_dict('list'))
            self.env.tb_other_periodogram.data = dict(old_data.data)
        self.publish_message(text='Ready')


    def load_from_file(self):
        """
        Loads mode data from a user-selected PKB file into Table 2.

        Opens a Tkinter file dialog for the user to select a PKB file.
        If a file is selected:
        - Calls `load_pkb_to_second_tab()` to process the file.
        - Updates `self.tb_se_second_source.data` with the loaded data.
        - Calls `apply_modes()` to reflect changes on plots.
        - Updates `self.env.selected_filename_pkb_text` with the chosen filename.
        - Publishes status messages.
        """
        self.publish_message(text='Loading from File')

        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        file_name = askopenfile()  # blocking
        if file_name:

            id=self.env.tb_source.data['id'][0]
            data_folder = self.env.tb_source.data['data_folder'][id]
            id_mycatalog = self.env.tb_source.data['id_mycatalog_all'][id]
            self.publish_message(text='Loading from File')
            df=self.load_pkb_to_second_tab(file_name)
            
            old_data = ColumnDataSource(
                        data=dict(Slicefreq = df['Slicefreq'].to_list(),
                                Frequency = df['Frequency'].to_list(),
                                Power = df['Power'].to_list(),
                                Mode = df['Mode'].to_list(),
                                xx = df['xx'].to_list()
                                ))
            self.tb_se_second_source.data = dict(old_data.data)
            self.apply_modes(df)
            print('Loaded', file_name)
            self.env.selected_filename_pkb_text.text = file_name.name
            self.publish_message(text='File Loaded, Ready')


    def load_bkg_param_from_file(self):
        """
        Loads background parameters from a user-selected file.

        Opens a Tkinter file dialog for the user to select a file.
        If a file is selected, its path is stored in
        `self.env.selected_filename_background_text`. This filename is then
        used by `calculate_synthetic_psd()`.
        Publishes status messages.
        """
        self.publish_message(text='Loading BKG from File')

        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        file_name = askopenfile()  # blocking
        if file_name:

            self.env.selected_filename_background_text.text = file_name.name
        self.publish_message(text='Ready')

            # id=self.env.tb_source.data['id'][0]
            # data_folder = self.env.tb_source.data['data_folder'][id]
            # id_mycatalog = self.env.tb_source.data['id_mycatalog_all'][id]

            # df=self.load_pkb_to_second_tab(file_name)
            
            # old_data = ColumnDataSource(
            #             data=dict(Slicefreq = df['Slicefreq'].to_list(),
            #                     Frequency = df['Frequency'].to_list(),
            #                     Power = df['Power'].to_list(),
            #                     Mode = df['Mode'].to_list(),
            #                     xx = df['xx'].to_list()
            #                     ))
            # self.tb_se_second_source.data = dict(old_data.data)
            # self.apply_modes(df)
            # print('Loaded', file_name)
            # self.env.selected_filename_pkb_text.text = file_name
            # self.publish_message(text='File Loaded, Ready')


    def save_as_table_2(self):
        """
        Saves the contents of Table 2 to a user-specified PKB file.

        Opens a Tkinter "save as" dialog for the user to choose a filename
        (default extension .pkb).
        If a filename is provided:
        - Data from `self.tb_se_second_source` is retrieved.
        - It's converted to PKB format (calculating 'n' values from delta Nu).
        - The data is saved to the chosen file using `apollinaire.peakbagging.save_pkb`.
        - A status message is published.
        """
        self.publish_message(text='Saving File')
        print('Load from file')
        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        filename = asksaveasfilename(defaultextension=".pkb")
        if filename:
            print(filename)
            df=self.tb_se_second_source.to_df()
            id=self.env.tb_source.data['id'][0]
            data_folder = self.env.tb_source.data['data_folder'][id]
            file_name=filename

            
            df_pkb=pd.DataFrame(columns=[self.env.pkb_columns])
            df_pkb['nu']=df['Frequency'].to_list()
            df_pkb['h']=df['Power'].to_list()
            df_pkb['l']=df['Mode'].astype(float).to_list()
            deltanu = self.env.dnu_val
            df_pkb['n']=np.rint(df['Frequency']/deltanu).astype(int)
            print('deltanu',deltanu)
            print(df_pkb['n'])
            df_pkb =df_pkb.fillna(0)
            pkb_array=df_pkb.values

            apol.peakbagging.save_pkb(file_name,pkb_array)
            print('PKB file saved to ',file_name)
            fulltext='PKB file saved to '+file_name+': Ready'
            self.publish_message(text=fulltext)

    def toggle_periodogram_axis_scale(self, attr, old, new):
        """
        Toggles the y-axis and x-axis scales of the main periodogram between linear and log.

        (Note: Docstring in code says "Changing periodogram scale: Not working")
        If the 'Log Scale' checkbox (`self.env.check_periodogram_axis_scale`) is active (0 in `new`),
        it attempts to set both X and Y scales of `self.env.fig_other_periodogram`
        to `LogScale`. Otherwise, it sets them to `LinearScale`.
        This function may require further refinement to work correctly with Bokeh's
        range and scale update mechanisms.

        Args:
            attr: The attribute that changed (e.g., 'active').
            old: The old list of active indices.
            new: The new list of active indices for the checkbox group.
        """

        print('Changing periodogram scale: Not working')
        from bokeh.models import Range1d, LogScale, LinearScale

        if 0 in new:
            # Set to logarithmic scale
            self.env.fig_other_periodogram.y_range = Range1d(start=0.1, end=10, bounds="auto")
            self.env.fig_other_periodogram.x_range = Range1d(start=0.1, end=10, bounds="auto")
            self.env.fig_other_periodogram.y_scale = LogScale()
            self.env.fig_other_periodogram.x_scale = LogScale()
        else:
            # Set to linear scale
            self.env.fig_other_periodogram.y_range = Range1d(start=0, end=10, bounds="auto") # Example range, might need dynamic update
            self.env.fig_other_periodogram.x_range = Range1d(start=0, end=10, bounds="auto") # Example range, might need dynamic update
            self.env.fig_other_periodogram.y_scale = LinearScale()
            self.env.fig_other_periodogram.x_scale = LinearScale()

        #self.env.fig_other_periodogram.reset.emit() # May not be the correct way to force refresh

