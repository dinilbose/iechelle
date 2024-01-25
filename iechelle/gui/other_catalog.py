import logging
import pandas as pd
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from bokeh.models import ColumnDataSource
import functions
from astropy import units as u
from tkinter import Tk
from lightkurve.seismology import SeismologyQuantity
import apollinaire as apol

from env import Environment
from bokeh.models import CustomJS, TextInput, Paragraph, CheckboxEditor
from bokeh.models import Button, Select, CategoricalColorMapper, CheckboxGroup, TableColumn, DataTable
from lightkurve import periodogram as lk_prd_module

import bokeh  # Import bokeh first so we get an ImportError we can catch
from bokeh.plotting import figure
from bokeh.models import LogColorMapper, Slider, RangeSlider, Button
import bokeh.palettes

log = logging.getLogger(__name__)

from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfile, asksaveasfilename

import config as config
import os
class Other_Catalog(Environment):
    env=Environment
    def __init__(self):
        print('Nothing')

        self.env.open_lund_catalog_button = Button(label="Select lund catalog")
        self.env.open_lund_catalog_star = Button(label="Load Catalog star")
        self.env.open_lund_catalog_star.on_click(self.open_lund_catalog_fits_file)

        #self.env.open_lund_catalog_button.on_click(lambda x: self.select_catalog())

        self.replace_variables()
        self.initiate_lund_catalog()


    def replace_variables(self):
        for attr_name in dir(self.env):
            if not attr_name.startswith("__") and hasattr(config, attr_name):
                config_value = getattr(config, attr_name)
                setattr(self.env, attr_name, config_value)

                print(config_value, attr_name)
        print('after change',self.env.lund_catalog_full_name)
        # self.env.lund_catalog_full_name = config.lund_catalog_full_name
        # print(self.env.lund_catalog_full_name)
        
    def initiate_lund_catalog(self):
        '''
        initiate_lund_catalog
        '''
        #votable_to_pandas('/Users/dp275303/work/Other/iechelle/lund/lund_table1.vot')
        df = pd.DataFrame()
        if not self.env.lund_catalog_full_name == None:
            
            if os.path.exists(self.env.lund_catalog_full_name):
                df = functions.votable_to_pandas(self.env.lund_catalog_full_name)
                print(df)
                if not self.env.lund_catalog_columns==None:
                    df=df[self.env.lund_catalog_columns]

                data_dict = {}

                # Iterate through the columns of the DataFrame and add them to the data dictionary
                for column_name in df.columns:
                    data_dict[column_name] = df[column_name].tolist()
            else:
                data_dict = {}
            # Create the ColumnDataSource using the data dictionary

        else:
            data_dict = {}


        self.env.tb_lund_table_source = ColumnDataSource(data=data_dict)
        if not df.empty:
            columns = [TableColumn(field=col, title=col) for col in df.columns]
        
            self.env.table_lund_table1 = DataTable(source=self.env.tb_lund_table_source, 
                                                   columns=columns, 
                                                   width=1200, 
                                                   height=1200,
                                                   selectable="checkbox",
                                                   editable=True,
                                                   )
        else:
            source = ColumnDataSource(data=dict(Column1=[], Column2=[], Column3=[]))
            source = ColumnDataSource(data=dict(Column1=[], Column2=[], Column3=[]))

            source = ColumnDataSource(data=dict(Column1=[], Column2=[], Column3=[]))

            columns = [TableColumn(field="Column1", title="Column 1"),
                    TableColumn(field="Column2", title="Column 2"),
                    TableColumn(field="Column3", title="Column 3")]

            self.env.table_lund_table1 = DataTable(source=source, 
                                                   columns=columns, 
                                                   width=1200, 
                                                   height=1200,
                                                   selectable="checkbox",
                                                   editable=True)



    def get_lund_plot_info(self):
        '''
        This function get the information of plot to the input values
        '''
        selected=self.env.table_lund_table1
        if len(selected)>0:
            ind = selected[0]
            df = self.env.tb_plot.to_df()
            df = df.loc[ind]
            print ('Selected', df)
            if not df.empty:
                self.env.text_extra_plot_name.value = str(df['name'])
                self.env.text_extra_plot_x_init.value = str(df['x_init'])
                self.env.text_extra_plot_x_scale.value = str(df['x_scale'])
                self.env.text_extra_plot_y_init.value = str(df['y_init'])
                self.env.text_extra_plot_y_scale.value = str(df['y_scale'])
                self.env.select_extra_plot_color.value = str(df['color'])
                self.env.select_extra_plot_style.value = str(df['style'])
            else:
                self.env.text_extra_plot_name.value = ""
                self.env.text_extra_plot_x_init.value = ""
                self.env.text_extra_plot_x_scale.value = ""
                self.env.text_extra_plot_y_init.value = ""
                self.env.text_extra_plot_y_scale.value = ""
                self.env.select_extra_plot_color.value = ""
                self.env.select_extra_plot_style.value = ""
        else:
            print('Nothing selected')

    def open_lund_catalog_fits_file(self):
        '''
        Read extra fits file and do the plot
        '''
        selected=self.env.tb_lund_table_source.selected.indices
        if len(selected)>0:
            ind = selected[0]
            df = self.env.tb_lund_table_source.to_df()
            df = df.loc[ind]
            print ('Selected', df)
        kic_id = df['KIC']
        file_name = functions.lund_catalog_fits_filename(
                    kic_id=kic_id, 
                    lund_catalog_data_location=self.env.lund_catalog_data_location)

        name = Path(file_name).stem
        self.env.text_extra_plot_name.value = name
        self.env.text_extra_plot_file_name = file_name 
        #self.publish_message('Extra fits'+self.env.text_extra_plot_file_name)