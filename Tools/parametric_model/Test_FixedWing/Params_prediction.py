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


data_selction = False


info_dict = {'log_path': None , 
            'data_selection': data_selction, 
            'config': None, 
            'model_results': None}

results = []
i = 0

# plt.ioff()
def show_nothing():
    pass
# plt.show = show_nothing

# === CONFIG ===========================================
# info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll.yaml'
# info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll _nonlinear.yaml'
info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll _nonlinear_old_topic.yaml'

# === MODEL RESULTS =====================================
# == no t_d
# info_dict['model_results'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_estimation_RollModel/simple_fixedwing_model_2024-01-22-09-11-49.yaml'

# == with t_d
# From simualation data
# info_dict['model_results'] = 'model_results_estimation_RollModel/simple_fixedwing_model_2024-01-24-10-27-57.yaml'
# Loong 006
info_dict['model_results'] = 'model_results_estimation_RollModel/simple_fixedwing_model_2024-01-24-14-29-41.yaml'


# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Simulation_data/14_47_07.ulg'
# start_model_prediction(**(info_dict))


# path_to_folder = '/home/anna/Documents/System_Identification/Simulation_data/With_aileron_acutators'
path_to_folder = '/home/anna/Documents/System_Identification/Loong_logs/Log_snippets/006/006_check/same_log_as_estimation'

with os.scandir(path_to_folder) as entries:
        for entry in entries:
            print()
            print(entry.name)

            # file name of log file
            file_name = os.path.join(path_to_folder, entry.name)
            info_dict['log_path'] = file_name
            start_model_prediction(**(info_dict))

