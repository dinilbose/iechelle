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
        
            self.env.table_lund_table1 = DataTable(source=self.env.tb_lund_table_source, columns=columns, width=400, height=400)
        else:
            source = ColumnDataSource(data=dict(Column1=[], Column2=[], Column3=[]))
            source = ColumnDataSource(data=dict(Column1=[], Column2=[], Column3=[]))

            source = ColumnDataSource(data=dict(Column1=[], Column2=[], Column3=[]))

            columns = [TableColumn(field="Column1", title="Column 1"),
                    TableColumn(field="Column2", title="Column 2"),
                    TableColumn(field="Column3", title="Column 3")]

            self.env.table_lund_table1 = DataTable(source=source, columns=columns, width=400, height=300)

        #print(table_lund_table1)
