# IMPORT PACKAGES AND FUNCTIONS
import numpy as np, os, sys, h5py, uproot
from root_utils import files_dict, get_data, final_jets, weights_factor
from sklearn    import utils


# ROOT VARIABLES
scalars  = ['rljet_m_comb'    , 'rljet_pt_calo'   , 'rljet_ECF3'      , 'rljet_C2'       , 'rljet_D2'         ,
            'rljet_Tau1_wta'  , 'rljet_Tau2_wta'  , 'rljet_Tau3_wta'  , 'rljet_Tau32_wta', 'rljet_FoxWolfram2',
            'rljet_PlanarFlow', 'rljet_Angularity', 'rljet_Aplanarity', 'rljet_ZCut12'   , 'rljet_Split12'    ,
            'rljet_Split23'   , 'rljet_KtDR'      , 'rljet_Qw'        , 'rljet_eta'      , 'rljet_phi'        ,
            'weight_mc'       , 'weight_pileup'   , 'rljet_n_constituents', 'rljet_topTag_DNN19_qqb_score'    ]
jet_var  = ['rljet_assoc_cluster_pt', 'rljet_assoc_cluster_eta', 'rljet_assoc_cluster_phi'                    ]
var_list = scalars# + jet_var


# TAG AND VARIABLES LISTS
qcd_tags = ['361023', '361024', '361025', '361026', '361027',
            '361028', '361029', '361030', '361031', '361032']
top_tags = ['410284', '410285', '410286', '410287', '410288']
tag_list = qcd_tags
#tag_list = top_tags


# DATA PATHS
main_path = '/nvme1/atlas/godin/AD_data/rootfiles'
if not os.path.isdir(main_path): main_path = '/lcg/storage18/atlas/pilette/atlasdata/rootfiles'
paths     = sorted([path for path in os.listdir(main_path) if path.split('.')[2] in qcd_tags+top_tags])
#paths     = sorted([path for path in os.listdir(main_path) if 'Pythia8EvtGen' in path or 'PhPy8EG' in path])
files     = files_dict(main_path, paths)
root_list = np.concatenate([files[tag] for tag in tag_list])
#for tag in tag_list:
#    for root_file in files[tag]: print(root_file)
#for key in uproot.open(root_list[0]).keys(): print(key)


# READING AND PROCESSING ROOT DATA
root_data = get_data(root_list, var_list, jet_var)
if np.all([n in var_list for n in jet_var]):
    root_data['jets'] = final_jets({key:root_data.pop(key) for key in jet_var})
root_data['weights'] = root_data.pop('weight_mc') * root_data.pop('weight_pileup')
for key in root_data: print(format(key,'28s'), root_data[key].shape, root_data[key].dtype)


data_path = '/nvme1/atlas/godin/AD_data'
#data      = h5py.File(data_path+'/'+'scalars_top.h5', 'w')
data      = h5py.File(data_path+'/'+'scalars_qcd.h5', 'w')
for key in root_data:
    data.create_dataset(key, data=utils.shuffle(root_data[key],random_state=0), compression='lzf')
#data.create_dataset('JZW', data=np.full_like(root_data['weights'], -1, dtype=np.uint8), compression='lzf')
data.create_dataset('JZW', data=np.full_like(root_data['weights'],  1, dtype=np.uint8), compression='lzf')
data.close()
