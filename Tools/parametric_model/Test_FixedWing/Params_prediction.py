import numpy as np
import pandas as pd
import importlib


from pyulog import *
from pyulog.px4 import *
from pyulog.core import *

import matplotlib.pyplot as plt
import shutil

import sys
sys.path.append('/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model')
from predict_model import *
from src.models.dynamics_model import DynamicsModel
from src.tools import DataHandler

import csv
import math


data_selction = 'interactive' #False


info_dict = {'log_path': None , 
            'data_selection': data_selction, 
            'config': None, 
            'model_results': None}



# === CONFIG ===========================================
# info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll.yaml'
info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll_nonlinear.yaml'
# info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll _nonlinear_old_topic.yaml'


# === MODEL RESULTS =====================================
info_dict['model_results'] = '/home/anna/Documents/System_Identification/Examples_log_files_roll_model/Simulation_gz_standard_vtol/model_result__13_53_25_selection02.yaml'

# === PATH to LOG FILE ==================================
info_dict['log_path'] = '/home/anna/Documents/System_Identification/Examples_log_files_roll_model/Simulation_gz_standard_vtol/13_48_12.ulg'


start_model_prediction(**(info_dict))


