import numpy as np
import pandas as pd
import importlib

import os
import yaml

from pyulog import *
from pyulog.px4 import *
from pyulog.core import *

import matplotlib.pyplot as plt
import shutil

import sys
sys.path.append('/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model')

from generate_parametric_model import *

import logging
# Set the logging level 
logging.basicConfig(level=logging.INFO)

# ==============================================================================================================================================

info_dict = {'log_path': None , 
            'data_selection': None, 
            'config': None, 
            'normalization': True,
            'plot' : True, 
            'selection_var': 'none',
            'extraction': False
            }

""" 
DATA_SELECTION argument: 
    - False (whole section of the log is used)
    - interactive (select data interactively using vpselector)
"""
info_dict['data_selection']  = False #'interactive'

""" 
CONFIG argument: 
    - Linear Model (L)
            with old/new uorb topics
    - Nonlinear Model (NL)
            with old/new uorb topics
"""
# CONFIG: L, new
# config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll.yaml'
# CONFIG: L, old
# config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll_old.yaml'
# CONFIG: NL, new
info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll_nonlinear.yaml'
# CONFIG: NL, old
# config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll _nonlinear_old_topic.yaml'

""" 
The Log file contains all data needed for the system identification of the specified model as defined in its config file
"""
# LOG-PATH: Estimation of Simulation Data
# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Simulation_data/With_aileron_acutators/13_54_51_selection01.csv'
# LOG-PATH: Estimation of Simulation data - locked aileron
info_dict['log_path'] = '/home/anna/Documents/System_Identification/Simulation_data/gz_new/With_aileron_acutators/new_gz/13_53_25_selection02.csv'
# === LOG-PATH: Loong log data
# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Loong_logs/Log_snippets/006/006_check/same_log_as_estimation/e89126_selection003.csv'

# ==============================================================================================================================================

# predict model parameters
start_model_estimation(**(info_dict))



# path_to_folder = 'Tools/parametric_model/configs/fixedwing_model_roll_NL__bounds_initials'

# with os.scandir(path_to_folder) as entries:
#         for entry in entries:
#             print()
#             print(entry.name)

#             # file name of log file
#             file_name = os.path.join(path_to_folder, entry.name)
#             info_dict['config'] = file_name
#             start_model_estimation(**(info_dict))