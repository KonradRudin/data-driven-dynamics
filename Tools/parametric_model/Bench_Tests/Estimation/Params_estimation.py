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

# Set the logging level to WARNING
logging.basicConfig(level=logging.WARNING)

# Conditions for further processing
def check_analysis_possible(ulog, px4_ulog, valid_vehicles):
    continue_processing = True
    # No further processing can be done if ...

    # ...if log file is corrupted and information is missing 
    if ulog.file_corruption:
        print('WARNING: Corrupt Log File')
        continue_processing = False

    # ...if duration of log file is 0s
    m ,s = divmod(int((ulog.last_timestamp - ulog.start_timestamp)/1e6), 60)
    if m == 0 and s == 0 :
        print('ERROR: Logging duration is 0s')
        continue_processing = False

    # ... if type of vehicle is wrong
    if ulog.initial_parameters['MAV_TYPE'] not in valid_vehicles:
        print("ERROR_1: This flight log file from vehicle type " + px4_ulog.get_mav_type()+ " cannot be analyzed")
        continue_processing = False

    return continue_processing

def sys_id_quadrotor(file_name, info_dict):
    
    info_dict['log_path'] = file_name

    # predict model parameters
    start_model_estimation(**(info_dict))

    return 

def params_estimation(path_to_folder, mav_type, info_dict):
    i = 0
    with os.scandir(path_to_folder) as entries:
        for entry in entries:
            print()
            print(i, entry.name)

            # file name of log file
            file_name = os.path.join(path_to_folder, entry.name)

            try:
                ulog = ULog(file_name)
                px4_ulog = PX4ULog(ulog)
                px4_ulog.add_roll_pitch_yaw() 

            except:
                raise Exception("ULog has wrong format and won't be analyzed")


            if check_analysis_possible(ulog, px4_ulog, valid_vehicle_type) is False:
                raise Exception("ULog doesn't meet processing-conditions and won't be analyzed")
            
            #sys_id_quadrotor(file_name, info_dict)
            # If quadrotor -> process further
            if ulog.initial_parameters['MAV_TYPE'] == mav_type: # and ulog.initial_parameters['SYS_AUTOSTART'] == 1206900:
                try:

                    sys_id_quadrotor(file_name, info_dict)
                

                except:
                    print('======== System Identification doesnt work', file_name)
                    # destination_file_path = os.path.join('/home/anna/Documents/flight_log_usb_stick/SysID/Quadrotors/good/SYS_ID_NoFurtherProcess', entry.name)
                    # shutil.copy(file_name, destination_file_path)

            else:
                print('Not a Quadrotor')
            i+=1

# ==============================================================================================================================================

path_to_folder = '/home/anna/Documents/logs_ulg/flight_log_usb_stick/SysID/Quadrotors/good/Quadrotors_dronetypes/1230010'

# multicopters
valid_vehicle_type = [2,13,14]

data_selction = False
config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model_1230010 _measured.yaml'

# mav_type = 14 # Octorotor
mav_type = 2 # Quadrotor

info_dict = {'log_path': None , 
            'data_selection': data_selction, 
            'config': config, 
            'normalization': True,
            'plot' : False, 
            'selection_var': 'none',
            'extraction': False
            }

results = []

params_estimation(path_to_folder, mav_type, info_dict)