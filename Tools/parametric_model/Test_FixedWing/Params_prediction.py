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
info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll.yaml'

# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Loong_logs/004/6daab632-47f7-4a01-8b0c-594fed05f5a6.ulg'
# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Loong_logs/004/66f6c1c8-3951-4b77-ab95-22908dfcebfc.ulg'
# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Loong_logs/004/b83e0f8a-d275-4554-a2f7-f9be54857c6b.ulg'

#info_dict['log_path'] = '/home/anna/Documents/System_Identification/Loong_logs/006/e8912629-ef7c-4461-887d-100b1cb5e75b.ulg'
#info_dict['log_path'] ='/home/anna/Documents/System_Identification/Loong_logs/006/d1201b7e-217d-48ee-b251-4c82a8ba6a66.ulg'
# info_dict['log_path'] ='/home/anna/Documents/System_Identification/Loong_logs/006/b637dc1a-b152-4778-9e9f-c51372437765.ulg'
# info_dict['log_path'] ='/home/anna/Documents/System_Identification/Loong_logs/006/697f5533-4799-48ba-abd6-949f41c956b1.ulg'

# info_dict['log_path'] = '/home/anna/Documents/System_Identification/Loong_logs/003/2cf1e16e-09cc-48d0-b927-95f4b17f18e4.ulg'
info_dict['log_path'] = '/home/anna/Documents/System_Identification/Simulation_data/07_08_58_selection03.csv'

info_dict['model_results'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_estimation_RollModel/simple_fixedwing_model_2024-01-18-09-56-22.yaml'
start_model_prediction(**(info_dict))


