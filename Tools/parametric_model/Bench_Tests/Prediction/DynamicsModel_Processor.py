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

def save_to_csv(results, csv_file):
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    fieldnames = ['Filename', 'Type', 'Duration-min', 'Duration-sec', 'Corr_x', 'Corr_y', 'Corr_z', 'Mean_corr',
                    'RMSE', 'Bench_mean', 'Rmse_check', 'neg_value']
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    print(f'Data has been saved to {csv_file}')


class DynamicsModel_Processor:
    def __init__(self, file_name, ulog):
        
        self.ulog = ulog
        self.file_name = file_name        
        self.drone_type = self.ulog.initial_parameters['SYS_AUTOSTART']
        self.data_selction = False

        self.info_dict = {'log_path': self.file_name,
                'data_selection': self.data_selction,
                'config': None,
                'model_results': None}
        
        self.results = {'Filename': self.file_name, 'Type': self.drone_type, 'Duration-min': '-', 'Duration-sec': '-',
                            'Corr_x': '-', 'Corr_y': '-', 'Corr_z': '-', 'Mean_corr': '-',
                            'RMSE': '-', 'Bench_mean': '-', 'Rmse_check': '-', 'neg_value': '-'}

    def process_files(self):

        if self.ulog.initial_parameters['MAV_TYPE'] == 2 and self.drone_type in [1002003, 1230200, 1230010, 1300022, 4001, 1004001]:
            self.data_quadrotor()

        elif self.ulog.initial_parameters['MAV_TYPE'] == 14 and self.drone_type in [1206900]:
            self.data_octorotor()
        
        else:
            return print('No further processing: No Configuration file for this drone type exists')
        
        # make model prediction
        try:
            acc_mat, acc_mat_pred = start_model_prediction(**(self.info_dict))
            result = self.evaluation(acc_mat, acc_mat_pred)
            print(result)
        except:
            return print('=== Prediciton doesnt work ')


    def data_quadrotor(self):
        
        # load configuration file of quadrotor -- default
        self.info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model.yaml'
        
        # === Models for Quadrotors
        path_model_result_quad = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_airframes/model_results_quadrotors/model_results_median/'

        # get specific estimation model
        if self.drone_type == 1002003:
            self.info_dict['model_results'] = path_model_result_quad + 'median_1002003.yaml'
        
        if self.drone_type == 1230200:
            self.info_dict['model_results'] = path_model_result_quad +'median_1230200.yaml'
        
        if self.drone_type == 1230010:
            self.info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model_1230010 _measured.yaml'
            self.info_dict['model_results'] = path_model_result_quad +'median_1230010_measured_params.yaml'

        if self.drone_type == 1300022:
            self.info_dict['model_results'] =  path_model_result_quad +'median_1300022.yaml'
        
        if self.drone_type == 4001:
            self.info_dict['model_results'] = path_model_result_quad +'median_4001.yaml'
        
        if self.drone_type == 1004001:
            self.info_dict['model_results'] = path_model_result_quad +'median_1004001.yaml'
        
    def data_octorotor(self):
        
        # load configuration file of octorotors -- default
        self.info_dict['config'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/octorotor_model_1206900_measured.yaml'
       
        # === Models for Octorotors
        self.info_dict['model_results'] = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/model_results_airframes/model_results_octorotors/model_results_median/median_1206900_measured_params.yaml'

    def evaluation(self, acc_mat, acc_mat_pred):

        # get correlation between predicted and measured value
        x_corr, y_corr, z_corr = self.corr_of_acc(acc_mat, acc_mat_pred)
        rmse = self.rmse_between_numpy_arrays(acc_mat, acc_mat_pred)

        if rmse > 6:
            return 'Poor Model Performace - No further analysis'
        
        for value in [x_corr, y_corr, z_corr]:
            if value < -0.2:
                    return 'Incident: Correlation too negativ'
        
        if self.check_corr_ind(thres_x = 0.0121, thres_y=0.0134 , thres_z=0.022 , x=x_corr ,y=y_corr ,z= z_corr):
            return 'BENCH TEST'

        return 'Good'
    
    def results_list(self):

        bench_mean = '-'
        rmse_check = '-'
        neg_value = '-'
        
        try: 
            acc_mat, acc_mat_pred = start_model_prediction(**(self.info_dict))
            x_corr, y_corr, z_corr = self.corr_of_acc(acc_mat, acc_mat_pred)
            if self.check_corr_ind(thres_x = 0.0121, thres_y=0.0134 , thres_z=0.022 , x=x_corr ,y=y_corr ,z= z_corr):
                bench_mean = 'BENCH_RSME'

            rmse = self.rmse_between_numpy_arrays(acc_mat, acc_mat_pred)

            if rmse > 6:
                rmse_check = 'too high'
            
            for value in [x_corr, y_corr, z_corr]:
                if value < -0.2:
                        neg_value = 'too neg'

            m, s = divmod(int((self.ulog.last_timestamp - self.ulog.start_timestamp) / 1e6), 60)
            mean = np.mean([np.abs(x_corr), np.abs(y_corr), np.abs(z_corr)])
            self.results = {'Filename': self.file_name, 'Type': self.drone_type, 'Duration-min': m, 'Duration-sec': s,
                                'Corr_x': x_corr, 'Corr_y': y_corr, 'Corr_z': z_corr, 'Mean_corr': mean,
                                'RMSE': rmse, 'Bench_mean': bench_mean,
                                'Rmse_check': rmse_check, 'neg_value': neg_value}
        except:
            print('======== System Identification doesnt work', self.file_name)
            
        return self.results

# Analysis metrics
    def corr_of_acc(self, acc_mat, acc_mat_pred):
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

    def check_corr_ind(self, thres_x, thres_y, thres_z, x,y,z):
        if np.abs(x) < thres_x and  np.abs(y) < thres_y and np.abs(z) < thres_z:
            return True
        return False

    def rmse_between_numpy_arrays(self, np_array1, np_array2):
        difference_array = np.subtract(np_array1.flatten(), np_array2.flatten())
        squared_array = np.square(difference_array)
        mse = squared_array.mean()
        return math.sqrt(mse)


# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================


path_to_folder = '/home/anna/Documents/logs_ulg/flight_log_usb_stick/SysID/Quadrotors/good/Quadrotors_dronetypes/1230010'
valid_vehicle_type = [2,13,14]

def show_nothing():
    pass
# doesnt show plot
#plt.show = show_nothing
#logging.getLogger().setLevel(logging.INFO)

list_csv = []

with os.scandir(path_to_folder) as entries:
    for entry in entries:
        print()
        print(entry.name)
        file_name = os.path.join(path_to_folder, entry.name)

        try:
            ulog = ULog(file_name)
            px4_ulog = PX4ULog(ulog)
            px4_ulog.add_roll_pitch_yaw()
        except:
            raise Exception("ULog has the wrong format and won't be analyzed")

        if not check_analysis_possible(ulog, px4_ulog, valid_vehicle_type):
            raise Exception("ULog doesn't meet processing conditions and won't be analyzed")

        sys_id_processor = DynamicsModel_Processor(file_name, ulog)
        sys_id_processor.process_files()


        list_csv.append(sys_id_processor.results_list())

# Specify the CSV file path
csv_file_path = '/home/anna/Documents/logs_ulg/flight_log_usb_stick/SysID/Quadrotors/Statistics/good/1230010/1230010_measured_params.csv'
save_to_csv(list_csv, csv_file_path)