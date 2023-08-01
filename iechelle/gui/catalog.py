from env import Environment
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.models import CustomJS, TextInput, Paragraph,PreText
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
    env=Environment
    def __init__(self):
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
        self.env.open_folder_button = Button(label="Select Directory")
        self.env.open_folder_button.on_click(lambda x: self.select_folder())
        self.env.open_file_button = Button(label="Select Fits File")
        self.env.open_file_button.on_click(lambda x: self.select_file())
    
    def select_folder(self):
        root = Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        dirname = askdirectory()  # blocking
        if dirname:
            self.env.selected_filename_text.text = dirname

    def select_file(self):
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
                                        data_folder=list([]),
                                        ))
            
            self.env.tb_source.data = dict(new_data.data)
            
        
    def update_all(self,attrname, old, new):
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
    #     '''Update'''
    #     self.env.text_banner.text=self.env.Message
    #     self.env.text_flag_source.value=str(self.env.v_flag_source)
    #     self.env.text_flag_check.value=str(self.env.v_flag_check)
    #     self.env.text_flag_duplicate.value=str(self.env.v_flag_duplicate)
    #     self.env.text_Notes.value=str(self.env.v_text_Notes)



    # def initiate_userinput(self):
    #     self.env.text_flag_duplicate = TextInput(value=str(self.env.v_flag_duplicate), title="Flag duplicate",height=50)
    #     self.env.text_flag_source = TextInput(value=str(self.env.v_flag_source), title="Flag source",height=50)
    #     self.env.text_flag_check = TextInput(value=str(self.env.v_flag_check), title="Flag check",height=50)

    #     self.env.text_Notes = TextInput(value=str(self.env.v_text_Notes), title="",height=70,width=1500,align='start')
    #     title_ = Paragraph(text='Notes', align='center')
    #     self.env.text_Notes_w = row([title_, self.env.text_Notes])



    # def text_format(self):
    #     '''Format text for display'''
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
    #     id_mycatalog=self.env.tb_source.data["id_mycatalog"][0]
    #     mycatalog.update(id_mycatalog=id_mycatalog,flag_source=self.env.text_flag_source.value)
    #     mycatalog.update(id_mycatalog=id_mycatalog,flag_check=self.env.text_flag_check.value)
    #     mycatalog.update(id_mycatalog=id_mycatalog,flag_duplicate=self.env.text_flag_duplicate.value)
    #     mycatalog.update(id_mycatalog=id_mycatalog,Notes=self.env.text_Notes.value)


    def next(self):
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
    #     query=self.catalog_all.query('id_mycatalog==@self.env.text_id_mycatalog_query.value')
    #     self.env.tb_source.data["id"][0]=query.index.values[0]
    #     self.env.tb_source.trigger("data",0,1)


    # def update_id(self):

    #     self.env.tb_source.data["id"][0]=int(self.env.text_id_query.value)
    #     self.env.tb_source.trigger("data",0,1)


    def update_selected(self,attr,old,new):

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

 