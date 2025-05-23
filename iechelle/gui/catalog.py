"""
Defines the Catalog class for managing astronomical catalog data and file interactions.

This module provides the `Catalog` class, which handles operations related to
loading astronomical source catalogs, navigating between sources, and managing
the selection of FITS files and data directories through UI interactions.
It uses the `Environment` class to share data and UI states with other
parts of the iEchelle application.
"""
from env import Environment
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.models import CustomJS, TextInput, Paragraph,PreText,Div
from bokeh.models import Button, Select, RadioGroup  # for saving data
from bokeh.plotting import figure
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfile
import ast
from astropy.coordinates import SkyCoord
from astropy import units as unit
import os

from pathlib import Path
from bokeh.layouts import row,column

class Catalog(Environment):
    """
    Manages catalog data, source navigation, and file/directory selection.

    This class initializes UI elements related to catalog operations,
    handles callbacks for opening file and directory dialogs (using Tkinter),
    updates Bokeh ColumnDataSources with information about selected files
    or catalog entries, and manages navigation (next/previous source).

    It interacts heavily with the shared `Environment` object (`self.env`)
    to access and modify UI elements and data sources.
    """
    env=Environment
    def __init__(self):
        """
        Initializes the Catalog UI elements and sets up callbacks.

        Sets up buttons for file/directory opening, source navigation,
        text inputs for catalog queries (though some seem commented out),
        and initializes Bokeh ColumnDataSources for source information.
        It also configures callbacks for these UI elements.
        """
        #self.catalog_all=mycatalog.pointer(catalog='mycatalog')
        #self.env.extra_flag_file=mycatalog.filename(name='extra_flag_file')

        # all_clusters=self.catalog_all.cluster.unique().tolist()
        # self.env.catalog_main=self.catalog_all.query('cluster==@self.env.default_cluster').reset_index(drop=True)
        # self.catalog_all=self.env.catalog_main

        # self.env.text_cluster_query= TextInput(value=self.env.default_cluster, title="Select Cluster")
        # self.env.text_cluster_query = Select(title='Cluster', options=all_clusters, value=all_clusters[0])

        # self.env.update_cluster_button = Button(label="Update cluster", button_type=self.env.button_type,width=150)
        # self.env.update_cluster_button.on_click(self.update_cluster)


        self.env.text_catalog_query= TextInput(value='', title="Catalog query")
        self.env.update_catalog_button = Button(label="Update catalog", button_type=self.env.button_type,width=150)
        # self.env.update_catalog_button.on_click(self.update_catalog)

        # self.env.update_id_mycatalog_button = Button(label="Update id_mycatalog", button_type=self.env.button_type,width=150)
        # self.env.update_id_mycatalog_button.on_click(self.update_id_mycatalog)
        # self.env.update_id_button = Button(label="Update id", button_type=self.env.button_type,width=150)
        # self.env.update_id_button.on_click(self.update_id)


        # self.id_mycatalog_all=list(self.catalog_all.id_mycatalog.values)
        # self.id_all=np.arange(0,len(self.catalog_all))
        # self.id=200
        # self.id_mycatalog=self.id_mycatalog_all[self.id]

        self.id_mycatalog_all=list(['None'])
        self.id_all=np.arange(0,len(self.id_mycatalog_all))
        self.id=0
        self.id_mycatalog=list(['None'])

        #mydata=mycatalog.pointer(id_mycatalog=self.id_mycatalog)
        # sector_list=ast.literal_eval(mydata.Sector.values[0])
        # sector_list=list([str(i) for i in sector_list])
        # self.env.sector=sector_list[0]

        # self.env.int_select_sector = Select(title='Sector', options=sector_list, value=sector_list[0])


        self.env.tb_source = ColumnDataSource(data=dict(id_all=self.id_all,
                                                        id_mycatalog_all=self.id_mycatalog_all,
                                                        path_fits=list(['None']),
                                                        id=[self.id],
                                                        id_mycatalog=[self.id_mycatalog],
                                                        data_folder=list(['nothing']),
                                                        ))
        

        # self.env.tb_catalog_all=ColumnDataSource(self.catalog_all.to_dict('list'))


        self.env.text_id_mycatalog_query = TextInput(value=str(self.id_mycatalog), title="id_mycatalog")
        self.env.text_id_query = TextInput(value=str(self.id), title="id")
        # self.env.tb_catalog_all.selected.on_change('indices',self.update_selected)
        # self.env.tb_catalog_all.selected.indices=[self.id]


        # self.env.text_banner_Gmag = Paragraph(text='', width=1000, height=10)
        # self.env.text_banner_bp_rp = Paragraph(text='', width=1000, height=10)
        # self.env.text_banner_dmin= Paragraph(text='', width=1000, height=10)

        self.env.message_banner = Div(text='', width=1000, height=25)

        self.env.next_button = Button(label="Next Source", button_type=self.env.button_type,width=150)
        self.env.next_button.on_click(self.next)
        self.env.previous_button = Button(label="Previous Source", button_type=self.env.button_type,width=150)
        self.env.previous_button.on_click(self.previous)
        # self.env.save_userinput_button = Button(label="Save User Input", button_type=self.env.button_type,width=100)
        # self.env.save_userinput_button.on_click(self.save_userinput)
        #self.env.text_banner = Paragraph(text=self.env.Message, width=1100, height=30)



        # self.text_format()
        # self.initiate_userinput()

        self.env.selected_filename_text = PreText()
        self.env.selected_filename_fits_text = PreText()
        self.env.selected_filename_pkb_text = PreText()
        self.env.selected_filename_background_text = PreText()


        self.env.open_folder_button = Button(label="Select Directory")
        self.env.open_folder_button.on_click(lambda x: self.select_folder())
        self.env.open_file_button = Button(label="Select Fits File")
        self.env.open_file_button.on_click(lambda x: self.select_file())
        
        self.env.open_catalog_button = Button(label="Select Fits File")
        self.env.open_catalog_button.on_click(lambda x: self.select_catalog())


    def select_catalog(): # No `self` in definition
        """
        Opens a file dialog to select a catalog file (presumably FITS).

        When a file is selected, its path is displayed. It attempts to update
        `self.env.tb_source` (which implies an instance `self` should be available)
        with information from the selected file.

        Uses Tkinter for the file dialog.
        Potential scoping issue: This method is defined without `self` as its
        first argument, yet it attempts to access `self.env`. This may
        lead to a NameError at runtime unless `self` is available through
        other means in its actual execution context.
        """
        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        file = askopenfile()  # blocking
        if file:
            file_name = file.name
            fits_path=os.path.abspath(file_name)
            self.env.selected_filename_text.text = fits_path
            
            id_mycatalog_all=list([Path(file_name).stem])
            id_all = np.arange(0,len(self.id_mycatalog_all))
            path_fits=list([fits_path])
            id=0
            id_mycatalog=list([Path(file_name).stem])
            data_folder=list([])
            new_data=ColumnDataSource(data=dict(id_all=list(id_all),
                                        id_mycatalog_all=list(id_mycatalog_all),
                                        path_fits=path_fits,
                                        id=list([id]),
                                        id_mycatalog=list(self.id_mycatalog),
                                        data_folder=list([str(Path(file_name).parent)]),
                                        ))
            
            self.env.tb_source.data = dict(new_data.data)

    def select_folder(self):
        """
        Opens a directory selection dialog using Tkinter.

        The path of the selected directory is then displayed in
        `self.env.selected_filename_text`.
        """
        root = Tk()
        root.attributes('-topmost', True)
        # root.withdraw()
        dirname = askdirectory()  # blocking
        
        root.lift()
        if dirname:
            self.env.selected_filename_text.text = dirname

    def select_file(self):
        """
        Opens a file selection dialog using Tkinter, intended for FITS files.

        Updates `self.env.selected_filename_text` and
        `self.env.selected_filename_fits_text` with the selected file's path.
        It also updates `self.env.tb_source` with information derived from
        this single file, treating it as the current source.
        """
        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        file = askopenfile()  # blocking
        if file:
            file_name = file.name
            fits_path=os.path.abspath(file_name)
            self.env.selected_filename_text.text = fits_path
            self.env.selected_filename_fits_text.text = fits_path

            id_mycatalog_all=list([Path(file_name).stem])
            id_all = np.arange(0,len(self.id_mycatalog_all))
            path_fits=list([fits_path])
            id=0
            id_mycatalog=list([Path(file_name).stem])
            data_folder=list([])
            new_data=ColumnDataSource(data=dict(id_all=list(id_all),
                                        id_mycatalog_all=list(id_mycatalog_all),
                                        path_fits=path_fits,
                                        id=list([id]),
                                        id_mycatalog=list(self.id_mycatalog),
                                        data_folder=list([str(Path(file_name).parent)]),
                                        ))
            
            self.env.tb_source.data = dict(new_data.data)

        
    def update_all(self,attrname, old, new):
        """
        Callback to update various UI elements when the current source changes.

        This method is typically triggered by a change in `self.env.tb_source.data`.
        It updates the displayed ID, ID mycatalog, and potentially other
        information. It also re-selects the current item in the main catalog table
        (`self.env.tb_catalog_all`). Some functionality appears commented out.

        Args:
            attrname: The attribute name that changed.
            old: The old value of the attribute.
            new: The new value of the attribute.
        """
        # print('aperutre_function')
        self.env.tb_source.data["id"][0]=int(self.env.tb_source.data["id"][0])
        id=self.env.tb_source.data["id"][0]
        self.env.tb_source.data["id_mycatalog"][0]=self.env.tb_source.data["id_mycatalog_all"][id]
        self.id_mycatalog=self.env.tb_source.data["id_mycatalog"][0]
        print(self.env.tb_source.data["id_mycatalog"][0],self.id_mycatalog)


        # self.text_format()
        # self.env.text_banner.text=self.env.Message
        # self.update_format()
        self.env.text_id_mycatalog_query.value=str(self.id_mycatalog)
        self.env.text_id_query.value=str(self.env.tb_source.data["id"][0])
        self.env.tb_catalog_all.selected.indices=[id]
#        self.update_tb_nearby_star()

#        self.env.catalog_find_from_isocrhone()
        print('Ready')

    # def update_format(self):
    #     """
    #     (Commented out) Intended to update UI elements with formatted text.
    #
    #     This method appears to have been responsible for updating various
    #     text banners and flag input fields based on the current source's data.
    #     """
    #     self.env.text_banner.text=self.env.Message
    #     self.env.text_flag_source.value=str(self.env.v_flag_source)
    #     self.env.text_flag_check.value=str(self.env.v_flag_check)
    #     self.env.text_flag_duplicate.value=str(self.env.v_flag_duplicate)
    #     self.env.text_Notes.value=str(self.env.v_text_Notes)



    # def initiate_userinput(self):
    #     """
    #     (Commented out) Intended to initialize UI elements for user input.
    #
    #     This method was likely used to create TextInput widgets for flags
    #     (duplicate, source, check) and notes related to a catalog source.
    #     """
    #     self.env.text_flag_duplicate = TextInput(value=str(self.env.v_flag_duplicate), title="Flag duplicate",height=50)
    #     self.env.text_flag_source = TextInput(value=str(self.env.v_flag_source), title="Flag source",height=50)
    #     self.env.text_flag_check = TextInput(value=str(self.env.v_flag_check), title="Flag check",height=50)

    #     self.env.text_Notes = TextInput(value=str(self.env.v_text_Notes), title="",height=70,width=1500,align='start')
    #     title_ = Paragraph(text='Notes', align='center')
    #     self.env.text_Notes_w = row([title_, self.env.text_Notes])



    # def text_format(self):
    #     """
    #     (Commented out) Intended to format text for display banners.
    #
    #     This method appears to have been responsible for fetching data
    #     using a `mycatalog` object (details unspecified) and formatting
    #     it into a message string for display. It also seems to have
    #     updated flag values in the environment.
    #     """
    #     data=mycatalog.pointer(catalog='mycatalog',id_mycatalog=self.env.tb_source.data["id_mycatalog"][0])
    #     # apogee=mycatalog.pointer(catalog='apogee',id_mycatalog=self.env.tb_source.data["id_mycatalog"][0])
    #     apogee=pd.DataFrame()
    #     Gmag=str(data['Gmag'].values[0])
    #     bp_rp=str(data['bp_rp'].values[0])
    #     PMemb=str(data['PMemb'].values[0])
    #     id_apogee=str(data['id_apogee'].values[0])
    #     name=str(data['id_mycatalog'].values[0])
    #     print(name)

    #     if apogee.empty:
    #         self.env.Message='Soure: '+name+' Gmag:'+Gmag+' bp_rp:'+bp_rp+' PMemb:'+ PMemb+ ' id_apogee:'+id_apogee

    #     else:
    #         apogee_teff=str(apogee['Teff'].values[0])
    #         apogee_Fe_H=str(apogee['[Fe/H]'].values[0])
    #         apogee_logg=str(apogee['logg'].values[0])
    #         self.env.Message='Soure: '+name+' Gmag:'+Gmag+' bp_rp:'+bp_rp+' PMemb:'+ PMemb+ ' id_apogee:'+id_apogee+' apogee_teff:'+apogee_teff+' apogee_Fe_H:'+apogee_Fe_H+' apogee_logg:'+apogee_logg

    #     self.env.v_flag_duplicate=data['flag_duplicate'].values[0]
    #     self.env.v_flag_source=data['flag_source'].values[0]
    #     self.env.v_flag_check=data['flag_check'].values[0]
    #     self.env.v_text_Notes=data['Notes'].values[0]




    # def save_userinput(self):
    #     """
    #     (Commented out) Intended to save user-provided flag and note inputs.
    #
    #     This method would have updated a `mycatalog` entry with values
    #     from various text input fields in the UI.
    #     """
    #     id_mycatalog=self.env.tb_source.data["id_mycatalog"][0]
    #     mycatalog.update(id_mycatalog=id_mycatalog,flag_source=self.env.text_flag_source.value)
    #     mycatalog.update(id_mycatalog=id_mycatalog,flag_check=self.env.text_flag_check.value)
    #     mycatalog.update(id_mycatalog=id_mycatalog,flag_duplicate=self.env.text_flag_duplicate.value)
    #     mycatalog.update(id_mycatalog=id_mycatalog,Notes=self.env.text_Notes.value)


    def next(self):
        """
        Advances the selection to the next source in the catalog.

        Increments the current source ID, updates `self.env.tb_source`
        to reflect the new selection, and calls `update_all` to refresh
        dependent UI elements. It also attempts to load sector information
        for the new source (some `mycatalog` related code is present but may
        depend on external, undefined `mycatalog` object).
        """
        # print(self.env.tb_source.data["id"])
        self.env.tb_source.data["id"][0]=int(self.env.tb_source.data["id"][0])+1
        id=self.env.tb_source.data["id"][0]
        print('All_data', self.env.tb_source.data["id_mycatalog_all"])
        self.env.tb_source.data["id_mycatalog"][0]=self.env.tb_source.data["id_mycatalog_all"][id]
        
        self.id_mycatalog=self.env.tb_source.data["id_mycatalog"][0]
        print(self.env.tb_source.data["id_mycatalog"][0],self.id_mycatalog)

        mydata=mycatalog.pointer(id_mycatalog=self.id_mycatalog)
        sector_list=ast.literal_eval(mydata.Sector.values[0])
        sector_list=list([str(i) for i in sector_list])
        self.env.sector=sector_list[0]
        self.update_all(0,0,0)

    def previous(self):
        """
        Moves the selection to the previous source in the catalog.

        Decrements the current source ID, updates `self.env.tb_source`
        to reflect the new selection, and calls `update_all` to refresh
        dependent UI elements.
        """
        # print(self.env.tb_source.data["id"])
        self.env.tb_source.data["id"][0]=int(self.env.tb_source.data["id"][0])-1
        id=self.env.tb_source.data["id"][0]
        self.env.tb_source.data["id_mycatalog"][0]=self.env.tb_source.data["id_mycatalog_all"][id]
        self.id_mycatalog=self.env.tb_source.data["id_mycatalog"][0]
        self.update_all(0,0,0)

    # def initiate_userinput(self):
    #     self.env.text_flag_duplicate = TextInput(value=str(self.env.v_flag_duplicate), title="Flag duplicate",height=50)
    #     self.env.text_flag_source = TextInput(value=str(self.env.v_flag_source), title="Flag source",height=50)
    #     self.env.text_flag_check = TextInput(value=str(self.env.v_flag_check), title="Flag check",height=50)

    #     self.env.text_Notes = TextInput(value=str(self.env.v_text_Notes), title="",height=70,width=1500,align='start')
    #     title_ = Paragraph(text='Notes', align='center')
    #     self.env.text_Notes_w = row([title_, self.env.text_Notes])



    # def update_catalog(self):
    #     """
    #     (Commented out) Updates the main catalog display based on queries.
    #
    #     This method would query a `mycatalog` object, filter it based on
    #     UI inputs (cluster selection, text query), and update
    #     `self.env.tb_source` and `self.env.tb_catalog_all`
    #     DataSources. It also handled updating sector information.
    #     """
    #     self.catalog_all=mycatalog.pointer(catalog='mycatalog')
    #     # catalog_all=catalog_all.query('flag_source==1 & flag_duplicate==0').reset_index()
    #     # catalog_all=catalog_all.sort_values(by=['Gmag']).reset_index()
    #     self.env.catalog_main=self.catalog_all.query('cluster==@self.env.default_cluster').reset_index()

    #     if not self.env.text_catalog_query.value=='':
    #         print('Query',self.env.text_catalog_query.value)
    #         self.catalog_all=self.env.catalog_main.reset_index(drop=True).query(self.env.text_catalog_query.value).reset_index(drop=True)
    #         print(self.catalog_all)
    #     elif self.env.text_catalog_query.value=='':
    #         self.catalog_all=self.env.catalog_main

    #     self.id_mycatalog_all=self.catalog_all.id_mycatalog
    #     print('newwwwwwwwwww',self.id_mycatalog_all)
    #     self.id_all=np.arange(0,len(self.catalog_all))
    #     self.id=0
    #     self.id_mycatalog=self.id_mycatalog_all[self.id]
    #     # self.env.tb_source = ColumnDataSource(data=dict(id_all=self.id_all,id_mycatalog_all=self.id_mycatalog_all,id=[self.id],id_mycatalog=[self.id_mycatalog]))
    #     old=ColumnDataSource(data=dict(id_all=self.id_all,id_mycatalog_all=self.id_mycatalog_all,id=[self.id],id_mycatalog=[self.id_mycatalog]))
    #     self.env.tb_source.data = old.data
    #     self.env.tb_catalog_all.data=ColumnDataSource(self.catalog_all.to_dict('list')).data
    #     self.env.tb_catalog_all.selected.indices=[self.id]
    #     self.env.tb_catalog_main.data=ColumnDataSource(self.env.catalog_main.to_dict('list')).data

    #     mydata=mycatalog.pointer(id_mycatalog=self.id_mycatalog)
    #     sector_list=ast.literal_eval(mydata.Sector.values[0])
    #     sector_list=list([str(i) for i in sector_list])
    #     self.env.sector=sector_list[0]
        

    # def update_cluster(self):
    #     """
    #     (Commented out) Handles updates when the selected cluster changes.
    #
    #     It would update the `self.env.default_cluster`, reload sector
    #     information for the current source within that cluster, and
    #     then call `update_catalog` to refresh the displayed catalog.
    #     """
    #     #self.catalog_all=mycatalog.pointer(catalog='mycatalog')

    #     self.env.default_cluster=self.env.text_cluster_query.value

    #     mydata=mycatalog.pointer(id_mycatalog=self.id_mycatalog)
    #     print('Update cluster list',self.env.sector,mydata)

    #     sector_list=ast.literal_eval(mydata.Sector.values[0])
    #     sector_list=list([str(i) for i in sector_list])
    #     self.env.sector=sector_list[0]
    #     self.env.int_select_sector.options=sector_list
    #     print('Update cluster list',self.env.sector)
    #     #self.env.catalog_main=self.catalog_all.query('cluster==@self.env.default_cluster').reset_index()
    #     #self.env.tb_catalog_main.data=ColumnDataSource(self.env.catalog_main.to_dict('list')).data
    #     self.update_catalog()



    # def update_id_mycatalog(self):
    #     """
    #     (Commented out) Updates the current selection based on 'id_mycatalog'.
    #
    #     Queries the catalog for a specific `id_mycatalog` (from a text input)
    #     and updates `self.env.tb_source.data["id"]` to match the found entry,
    #     triggering further UI updates.
    #     """
    #     query=self.catalog_all.query('id_mycatalog==@self.env.text_id_mycatalog_query.value')
    #     self.env.tb_source.data["id"][0]=query.index.values[0]
    #     self.env.tb_source.trigger("data",0,1)


    # def update_id(self):
    #     """
    #     (Commented out) Updates the current selection based on a direct 'id'.
    #
    #     Sets `self.env.tb_source.data["id"]` from a text input value,
    #     triggering further UI updates.
    #     """
    #     self.env.tb_source.data["id"][0]=int(self.env.text_id_query.value)
    #     self.env.tb_source.trigger("data",0,1)


    def update_selected(self,attr,old,new):
        """
        Callback for when a selection is made in the main catalog table.

        Updates `self.env.tb_source.data["id"]` to the newly selected index,
        triggering other updates via the `update_all` callback mechanism.

        Args:
            attr: The attribute name that changed (e.g., 'indices').
            old: The old selection.
            new: The new selection (list of selected indices).
        """
        # print(self.se.nonselection_glyph.fill_color,self.se.nonselection_glyph.fill_alpha)
        # self.env.tb_catalog_all.selected.indices=[old[0]]

        if not new==[]:
            print(new,new[0])
            self.env.tb_source.data["id"][0]=new[0]
            # self.env.tb_catalog_all.selected.indices=[new[0]]

            self.env.tb_source.trigger("data",0,1)
        # if new==[]:
        #     self.env.tb_catalog_all.selected.indices=self.env.tb_source.data["id"]
            # self.env.tb_source.trigger("data",0,1)


    # def update_selection_program(self,attr,old,new):
    #     """
    #     (Commented out) Handles logic for switching between 'Catalog' and 'Custom Star' modes.
    #
    #     Depending on the selected program (from a RadioGroup or similar widget),
    #     this method would change UI states (e.g., button appearance) and
    #     update `self.env.tb_source` either with catalog data or with
    #     placeholder data for a custom star. It involves calls to `mycatalog`
    #     and `update_catalog`.
    #
    #     Args:
    #         attr: The attribute that changed.
    #         old: The old value.
    #         new: The new value (typically the active selection index).
    #     """
    #     self.env.selection_program_text = self.env.selection_program.labels[self.env.selection_program.active]
    #     print('Program ',self.env.selection_program_text)

    #     if self.env.selection_program_text=='Catalog':
    #         self.env.custom_star_download_button.button_type='danger'
    #         #self.id_mycatalog=self.env.text_id_mycatalog_query.value
    #         self.catalog_all=mycatalog.pointer(catalog='mycatalog')
    #         # catalog_all=catalog_all.query('flag_source==1 & flag_duplicate==0').reset_index()
    #         # catalog_all=catalog_all.sort_values(by=['Gmag']).reset_index()
    #         self.env.catalog_main=self.catalog_all.query('cluster==@self.env.default_cluster').reset_index()

    #         if not self.env.text_catalog_query.value=='':
    #             print('Query',self.env.text_catalog_query.value)
    #             self.catalog_all=self.env.catalog_main.reset_index(drop=True).query(self.env.text_catalog_query.value).reset_index(drop=True)
    #             print(self.catalog_all)
    #         elif self.env.text_catalog_query.value=='':
    #             self.catalog_all=self.env.catalog_main

    #         self.id_mycatalog_all=self.catalog_all.id_mycatalog


    #         #self.update_catalog()

    #         self.id_mycatalog=self.id_mycatalog_all[0]
    #         print('Current id_mycatalog',self.id_mycatalog)
    #         mydata=mycatalog.pointer(id_mycatalog=self.id_mycatalog)
    #         print('Current data',mydata)
    #         sector_list=ast.literal_eval(mydata.Sector.values[0])
    #         sector_list=list([str(i) for i in sector_list])
    #         print('Sector_list',sector_list)
    #         self.env.int_select_sector.options=sector_list

    #         self.env.sector=sector_list[0]
    #         self.update_catalog()
    #         #tb_source_new = ColumnDataSource(data=dict(id_all=self.id_all,id_mycatalog_all=self.id_mycatalog_all,id=[self.id],id_mycatalog=[self.id_mycatalog]))
    #         #self.env.tb_source.data=tb_source_new.data
    #         self.env.tb_source.trigger("data",0,1)

    #     if self.env.selection_program_text=='Custom Star':
    #         c=2
    #         self.env.sector=1
    #         self.env.custom_star_download_button.button_type='success'
    #         tb_source_new = ColumnDataSource(data=dict(id_all=[0],id_mycatalog_all=['custom_star'],id=[0],id_mycatalog=['custom_star']))
    #         self.env.tb_source.data=tb_source_new.data
    #         print('tb_source from update_selection_program',self.env.tb_source.data)
    #         self.env.tb_source.trigger("data",0,1)

 