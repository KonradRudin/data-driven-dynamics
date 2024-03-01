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

    # predict acceleration -- force
    acc_mat, acc_amt_pred = start_model_prediction(**(info_dict))

    # get correlation between predicted and measured value
    x_forces, y_forces, z_forces = corr_of_acc(acc_mat, acc_amt_pred)

    bench = '-'
    bench_mean = '-'
    rmse_check = '-'
    neg_value = '-'
    if check_corr_ind(thres_x = 0.0121, thres_y=0.0134 , thres_z=0.022 , x=x_forces ,y=y_forces ,z= z_forces):
        bench_mean = 'BENCH_RSME'
    

    # if pred of forces is a straight line
    min_max_diff = min_max_tuple(acc_amt_pred)

    rmse = rmse_between_numpy_arrays(acc_mat, acc_amt_pred)

    # TODO if negative correlation too high
    # TODO if the RMSE value between the predicted and measured value is too big (a certain toleranz is acceptable as e.g the mass is not known)
    if rmse > 6:
        rmse_check = 'too high'
    
    for value in [x_forces, y_forces, z_forces]:
        if value < -0.2:
                neg_value = 'too neg'

    
    return x_forces, y_forces, z_forces, rmse, bench_mean, min_max_diff, rmse_check, neg_value

def corr_of_acc(acc_mat, acc_mat_pred):
    acc_x = acc_mat[:, 0]
    acc_y = acc_mat[:, 1]
    acc_z = acc_mat[:, 2]

    acc_x_pred = acc_mat_pred[:, 0]
    acc_y_pred = acc_mat_pred[:, 1]
    acc_z_pred = acc_mat_pred[:, 2]

    df_actual = pd.DataFrame({'x': acc_x, 'y': acc_y, 'z': acc_z})
    df_pred = pd.DataFrame({'x': acc_x_pred, 'y': acc_y_pred, 'z': acc_z_pred})

    # Calculate the correlation coefficients
    correlation_matrix = df_actual.corrwith(df_pred)

    return correlation_matrix['x'], correlation_matrix['y'], correlation_matrix['z']

def check_corr_ind(thres_x, thres_y, thres_z, x,y,z):
    if np.abs(x) < thres_x and  np.abs(y) < thres_y and np.abs(z) < thres_z:
        return True
    return False


def rmse_between_numpy_arrays(np_array1, np_array2):
    difference_array = np.subtract(np_array1.flatten(), np_array2.flatten())
    squared_array = np.square(difference_array)
    mse = squared_array.mean()
    return math.sqrt(mse)

def min_max_tuple(acc_mat_pred_forces):


    # Initialize lists to store max and min values for each position
    max_values = [float('-inf')] * 3
    min_values = [float('inf')] * 3

    # Iterate through the array and update max and min values for each position
    for tuple_item in acc_mat_pred_forces:
        for i in range(3):
            max_values[i] = max(max_values[i], tuple_item[i])
            min_values[i] = min(min_values[i], tuple_item[i])
    
    min_diff = max(np.abs(max_values[0]-min_values[0]), np.abs(max_values[1]-min_values[1]), np.abs(max_values[2]-min_values[2]))
    
    return min_diff


# log files to check
path_to_folder = '/home/anna/Documents/logs_ulg/flight_log_usb_stick/SysID/bench_simualtion/logs'

# multicopters
valid_vehicle_type = [2,13,14]

data_selction = False


# model -- "resources/quadrotor_model.ulg"
model_results1 = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results/multirotor_model_2023-11-27-14-07-09.yaml'

# === Models for Quadrotors
path_model_result_quad = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_airframes/model_results_quadrotors/model_results_median/'

model_results_median_1002003 = path_model_result_quad + 'median_1002003.yaml'
model_results_median_1230200 = path_model_result_quad +'median_1230200.yaml'
#model_results_median_1230010 = path_model_result_quad +'median_1230010.yaml'
model_results_median_1230010 = path_model_result_quad +'median_1230010_new.yaml'
model_results_median_1300022 = path_model_result_quad +'median_1300022.yaml'
model_results_median_4001    = path_model_result_quad +'median_4001.yaml'
model_results_median_1004001 = path_model_result_quad +'median_1004001.yaml'

# === Models for Octorotors
#model_results_median_12069000 = 'model_results_airframes/model_results_octorotors/model_results_median/median_1206900.yaml'
#model_results_median_12069000 = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_airframes/model_results_octorotors/model_results_median/median_1206900_new.yaml'
model_results_median_12069000 = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_airframes/model_results_octorotors/model_results_median/median_1206900_measured_params.yaml'


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
        
        # If quadrotor and a predicted model exists for the specific dronetype -> process further
        # x,y,z, rmse, bench_mean, bench, x_moments, y_moments, z_moments, min_max_diff = sys_id_quadrotor(file_name, info_dict)
        drone_type = ulog.initial_parameters['SYS_AUTOSTART']
        
        # Quadrotors
        if ulog.initial_parameters['MAV_TYPE'] == 2 and drone_type in [1002003, 1230200, 1230010, 1300022, 4001, 1004001]: 
            
            # load configuration file of quadrotor
            info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model.yaml'

            # get specific estimation model
            if drone_type == 1002003:
                info_dict['model_results'] = model_results_median_1002003
            if drone_type == 1230200:
                info_dict['model_results'] = model_results_median_1230200
            if drone_type == 1230010:
                info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model_1230010.yaml'
                info_dict['model_results'] = model_results_median_1230010
            if drone_type == 1300022:
                info_dict['model_results'] = model_results_median_1300022
            if drone_type == 4001:
                info_dict['model_results'] = model_results_median_4001
            if drone_type == 1004001:
                info_dict['model_results'] = model_results_median_1004001

        # Octorotors
        if ulog.initial_parameters['MAV_TYPE'] == 14 and drone_type in [1206900]: 
            # load configuration file of octorotors
            info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/octorotor_model_1206900_measured.yaml'

            if drone_type == 1206900:
                info_dict['model_results'] = model_results_median_12069000

# =====================================================================================================================================================

        x,y,z, rmse, bench_mean, min_max_diff, rmse_check, neg_value = sys_id_quadrotor(file_name, info_dict)
        try:
            x,y,z, rmse, bench_mean, min_max_diff, rmse_check, neg_value = sys_id_quadrotor(file_name, info_dict)

            m ,s = divmod(int((ulog.last_timestamp - ulog.start_timestamp)/1e6), 60)
            mean = np.mean([np.abs(x), np.abs(y), np.abs(z)])
            results.append({'Filename': entry.name, 'Type': drone_type, 'Duration-min': m,  'Duration-sec': s, 
                            'Corr_x': x, 'Corr_y': y, 'Corr_z': z, 'Mean_corr': mean,
                            'RMSE': rmse , 'Min_max_pred': min_max_diff, 'Bench_mean':bench_mean, 'Rmse_check': rmse_check, 'neg_value': neg_value })


        except:
            print('======== System Identification doesnt work', file_name)
            # destination_file_path = os.path.join('/home/anna/Documents/flight_log_usb_stick/SysID/Quadrotors/good/SYS_ID_NoFurtherProcess', entry.name)
            # shutil.copy(file_name, destination_file_path)
            
            results.append({'Filename': entry.name, 'Type': drone_type, 'Duration-min': '-',  'Duration-sec': '-', 
                                'Corr_x': '-', 'Corr_y': '-', 'Corr_z': '-', 'Mean_corr': '-', 
                                'RMSE': '-' , 'Min_max_pred': '-', 'Bench_mean':'-', 'Rmse_check': '-' , 'neg_value': '-' })

        i+=1

# #Specify the CSV file path
csv_file = '/home/anna/Documents/logs_ulg/flight_log_usb_stick/SysID/Octorotors/Statistics/xxx.csv'

# Create the directories if they don't exist
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

# Specify fieldnames
fieldnames = ['Filename', 'Type', 'Duration-min', 'Duration-sec', 'Corr_x', 'Corr_y', 'Corr_z', 'Mean_corr','RMSE', 'Min_max_pred', 'Bench_mean', 'Rmse_check', 'neg_value']

# Write the results to a CSV file
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Write the data rows
    for result in results:
        writer.writerow(result)

print(f'Data has been saved to {csv_file}')