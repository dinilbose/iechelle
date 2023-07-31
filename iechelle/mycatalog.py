import pandas as pd
from iechelle import config
from pathlib import Path
import os
# import ast

PACKAGEDIR = os.path.abspath(os.path.dirname(__file__))
package_path=str(Path(PACKAGEDIR).parents[0])+'/'

Data_path=config.data_folder

def pointer(catalog='mycatalog',pmemb=0,cluster='',id_mycatalog='',id_gaia='',integrate=True,real=False):
    '''Points to the catalog area'''

    data=''

    mycatalog=pd.read_csv(config.catalog_path)
    mycatalog=mycatalog.query('PMemb>=@pmemb')
    if not id_gaia=='':
        mycatalog=mycatalog.query('id_gaia==@id_gaia')
    if not cluster=='':
        mycatalog=mycatalog.query('cluster==@cluster')

    if real==True:
        whole=pd.read_csv(package_path+'/My_catalog/Source/Collinder_69_aperture_pixel.csv')
        Real_source=whole.drop_duplicates(subset=['pixel_x','pixel_y'],keep='first').id_gaia.unique().tolist()
        mycatalog=mycatalog.query('id_gaia==@Real_source')


    if not id_mycatalog=='':

        mycatalog=mycatalog.query('id_mycatalog==@id_mycatalog')
        id_gaia_n=mycatalog.id_gaia.values.tolist()
        if id_mycatalog=='custom_star':
            mycatalog.loc[0,'id_mycatalog']='custom_star'
            mycatalog.loc[0,'id_gaia']='custom_star'
            mycatalog.loc[0,'cluster']='Custom_star'
            mycatalog.loc[0,'Sector']='[0]'
            mycatalog=mycatalog.fillna(0)

    if catalog=='mycatalog':
        # data=pd.read_csv('My_catalog/my_catalog_v02.csv')
        # data=data.query('PMemb>=@pmemb')
        data=mycatalog

    if catalog=='gaia':
        data=utils.votable_to_pandas(full_path+'My_catalog/Source/Collinder69_gaia.vot')
        data=utils.votable_to_pandas(full_path+'My_catalog/Source/Gaia_open_cluster_members.vot')
        data['Source']='DR2_'+data['Source'].astype(str)
        data['id_gaia']=data['Source']
        data['Cluster'] = data['Cluster'].str.decode('utf-8')
        id_gaia_n=mycatalog.id_gaia.values.tolist()
        data=data.query('id_gaia==@id_gaia_n')

    if catalog=='apogee':
        # /home/dinilbose/PycharmProjects/light_cluster/My_catalog/Source
        # apogee=utils.votable_to_pandas(package_path+'My_Catalog/Source/Apogee.vot')
        apogee=utils.votable_to_pandas('/home/dinilbose/PycharmProjects/light_cluster/My_catalog/Source/Apogee.vot')

        apogee['SourceId']='DR2_'+apogee['SourceId'].astype('str')
        apogee['id_gaia']=apogee['SourceId']
        apogee['Cluster'] = apogee['Cluster'].str.decode('utf-8')
        apogee['APOGEE'] = apogee['APOGEE'].str.decode('utf-8')
        id_gaia_n=mycatalog.id_gaia.values.tolist()
        data=apogee.query('id_gaia==@id_gaia_n')

    if catalog=='oscillation':
        data=pd.read_csv(package_path+'My_catalog/Source/Gaia_all_astrobase_oscillation_source.csv')
        # data['Source']='DR2_'+data['Source'].astype(str)
        data['id_gaia']=data['Source']
        id_gaia_n=mycatalog.id_gaia.values.tolist()
        data=data.query('id_gaia==@id_gaia_n')


    if catalog=='tic':
        tic=utils.votable_to_pandas(package_path+'My_catalog/Source/gaia_mast_crossmatch.xml')
        tic['id_gaia'] = tic['id_gaia'].str.decode('utf-8')
        id_gaia_n=mycatalog.id_gaia.values.tolist()
        data=tic.query('id_gaia==@id_gaia_n')

    if integrate==True:
        data['id_mycatalog'] = data.id_gaia.map(mycatalog.set_index('id_gaia')['id_mycatalog'].to_dict())
    # data['Cluster']=data['Cluster'].str.decode('utf-8')
    return data

def filename(name='',id_gaia='',id_mycatalog='',cluster='Collinder_69',sector=''):
    '''Filename manager: Gives file names and path for all the files'''

    #Data_path='/home/dinilbose/PycharmProjects/light_cluster/cluster/Collinder_69/Data/'
    path_sys=Path()

    my_catalog=pointer(catalog='mycatalog')

    if sector=='':
        Sector=''
    else:
        Sector='_s'+str(sector)

    if not id_gaia=='':
        my_catalog=my_catalog.query('id_gaia==@id_gaia')
        cluster=my_catalog['cluster'].values[0]
    if not id_mycatalog=='':
        my_catalog=my_catalog.query('id_mycatalog==@id_mycatalog')
        if id_mycatalog=='custom_star':
            my_catalog=my_catalog.query('id_mycatalog=="7"')
            my_catalog.loc[0,'id_mycatalog']='custom_star'
            my_catalog.loc[0,'id_gaia']='custom_star'
            my_catalog.loc[0,'cluster']='Custom_star'
            my_catalog.loc[0,'Sector']='[0]'
            my_catalog=my_catalog.fillna(0)

        cluster=my_catalog['cluster'].values[0]

    if name=='eleanor_flux':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_ffi.csv'
        full_path=Path(filename)

    if name=='eleanor_flux_current':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_ffic.csv'
        full_path=Path(filename)

    if name=='eleanor_aperture':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_ap.txt'
        full_path=Path(filename)

    if name=='eleanor_aperture_current':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_apc.txt'
        full_path=Path(filename)


    if name=='eleanor_tpf':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_tpf.npy'
        full_path=Path(filename)
    if name=='eleanor_header':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_hd.txt'
        full_path=Path(filename)

    if name=='eleanor_time_flag':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_tflag.txt'
        full_path=Path(filename)

    if name=='bokeh_periodogram_table':
        id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/id_gaia'+'/'+cluster+'_'+id+Sector+'_bkprtb.csv'
        full_path=Path(filename)

    if name=='whole_gaia_data':
        #id=my_catalog.id_gaia.item()
        filename=Data_path+name+'/'+cluster+'.csv'
        full_path=Path(filename)

    if name=='extra_flag_file':
        #id=my_catalog.id_gaia.item()
        filename=Data_path+'extra_flag.flag'
        full_path=Path(filename)

    if name=='cluster_ffi':
        import glob
        filename=Data_path+name+'/'+cluster+'/'+'*.fits'
        filename=glob.glob(filename)
        full_path=filename
    if name=='other_psd':
        data_path=config.data_folder+'other/mode_selection/'+id_mycatalog
        filename=data_path+'/'+id_mycatalog+'.fits'
        filename=Path(filename)
        full_path=filename

    if name=='other_psd_save_freq':
        data_path=config.data_folder+'other/mode_selection/'+id_mycatalog
        filename=data_path+'/'+id_mycatalog+'_save_freq.csv'
        filename=Path(filename)
        full_path=filename

    if name=='temp':
        filename=Data_path+name
        full_path=Path(filename)

    return full_path

def update(id_mycatalog,**kwargs):
        '''Updates Catalog based on user inputs'''
        current_catalog_path= config.catalog_path
        mycatalog=pd.read_csv(current_catalog_path)
        mycatalog=mycatalog.set_index('id_mycatalog')
        for key in kwargs:
            print('Version:',current_catalog_path,'  ',id_mycatalog,"Updated: %s: %s" % (key, kwargs[key]))
            mycatalog.loc[id_mycatalog,key]=kwargs[key]
        mycatalog.to_csv(config.catalog_path)
