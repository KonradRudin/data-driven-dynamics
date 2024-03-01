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




def check_corr(threshold, x,y,z):
    if np.abs(x) < threshold and  np.abs(y) < threshold and np.abs(z) < threshold:
        return True
    return False

def slide_window_data_overlapping(timestamps, acc_mat, acc_mat_pred):

    acc_x = acc_mat[:, 0]
    acc_y = acc_mat[:, 1]
    acc_z = acc_mat[:, 2]

    acc_x_pred = acc_mat_pred[:, 0]
    acc_y_pred = acc_mat_pred[:, 1]
    acc_z_pred = acc_mat_pred[:, 2]

    timestamps_array = pd.to_timedelta(timestamps*1000000, unit='us')

    df = pd.DataFrame({
    'x_actual': acc_x, 'y_actual' : acc_y, 'z_actual' : acc_z, 
    'x_pred': acc_x_pred, 'y_pred' : acc_y_pred, 'z_pred' : acc_z_pred, 
    }, index=timestamps_array)

    window_size = '10s'
    correlation_series_x = df['x_actual'].rolling(window=window_size).corr(df['x_pred'])
    correlation_series_y = df['y_actual'].rolling(window=window_size).corr(df['y_pred'])
    correlation_series_z = df['z_actual'].rolling(window=window_size).corr(df['z_pred'])

    return correlation_series_x, correlation_series_y, correlation_series_z

def slide_window_data(timestamps, acc_mat, acc_mat_pred):

    acc_x = acc_mat[:, 0]
    acc_y = acc_mat[:, 1]
    acc_z = acc_mat[:, 2]

    acc_x_pred = acc_mat_pred[:, 0]
    acc_y_pred = acc_mat_pred[:, 1]
    acc_z_pred = acc_mat_pred[:, 2]

    timestamps_array = pd.to_timedelta(timestamps*1000000, unit='us')

    df = pd.DataFrame({
    'x_actual': acc_x, 'y_actual' : acc_y, 'z_actual' : acc_z, 
    'x_pred': acc_x_pred, 'y_pred' : acc_y_pred, 'z_pred' : acc_z_pred, 
    }, index=timestamps_array)

    window_size = '20s'

    # Calculate correlation for each 20-second interval
    correlation_results = []
    for i in range(0, len(df), pd.to_timedelta(window_size).seconds):
        start_time = df.index[i]
        end_time = df.index[min(i + pd.to_timedelta(window_size).seconds, len(df) - 1)]
        
        window_data = df.loc[start_time:end_time]
        correlation_x = window_data['x_actual'].corr(window_data['x_pred'])
        correlation_y = window_data['y_actual'].corr(window_data['y_pred'])
        correlation_z = window_data['z_actual'].corr(window_data['z_pred'])
    
        correlation_results.append((start_time, end_time, correlation_x, correlation_y, correlation_z))
    #print(correlation_results)
    # Create a DataFrame from the correlation results
    correlation_df = pd.DataFrame(correlation_results, columns=['Corr_x', 'Corr_y', 'Corr_z'])


    return correlation_df['Corr_x'], correlation_df['Corr_y'], correlation_df['Corr_z']

def corr_of_acc(acc_mat, acc_mat_pred):
    acc_x = acc_mat[:, 0]
    acc_y = acc_mat[:, 1]
    acc_z = acc_mat[:, 2]

    acc_x_pred = acc_mat_pred[:, 0]
    acc_y_pred = acc_mat_pred[:, 1]
    acc_z_pred = acc_mat_pred[:, 2]

    df_actual = pd.DataFrame({'x': acc_x, 'y': acc_y, 'z': acc_z})
    df_pred = pd.DataFrame({'x': acc_x_pred, 'y': acc_y_pred, 'z': acc_z_pred})

    #df_actual_smoothed = df_actual.rolling(window=3).mean()  # Adjust the window size as needed

    # Calculate the correlation coefficients
    correlation_matrix = df_actual.corrwith(df_pred)
    #correlation_matrix_smoothed = df_actual_smoothed.corrwith(df_pred)

    # # # Create subplots
    # fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # # Plot each array in a separate subplot
    # axs[0].plot(df_pred['x'], label='X-direction', color='blue')
    # axs[0].plot(df_actual['x'], label='X-direction', color='red')

    # from sklearn.preprocessing import MinMaxScaler

    # # Create a sample DataFrame

    # # Initialize the MinMaxScaler
    # scaler = MinMaxScaler()

    # # Apply Min-Max normalization to the DataFrame
    # df_normalized = pd.DataFrame(scaler.fit_transform(df_pred), columns=df_pred.columns)

    #     # Plot each array in a separate subplot
    # axs[1].plot(df_normalized['x'], label='X-direction', color='blue')
    # axs[1].plot(df_actual['x'], label='X-direction', color='red')


    # axs[1].plot(df_pred['y'], label='Y-direction', color='blue')
    # axs[1].plot(df_actual_smoothed['y'], label='Y-direction', color='red')

    # axs[2].plot(df_pred['z'], label='Z-direction', color='blue')
    # axs[2].plot(df_actual_smoothed['z'], label='Z-direction', color='red')

    # # Add labels and legend to each subplot
    # axs[0].set_xlabel('X-axis Label')
    # axs[0].set_ylabel('Y-axis Label')
    # axs[0].legend()

    # axs[1].set_xlabel('X-axis Label')
    # axs[1].set_ylabel('Y-axis Label')
    # axs[1].legend()

    # axs[2].set_xlabel('X-axis Label')
    # axs[2].set_ylabel('Y-axis Label')
    # axs[2].legend()

    # # Adjust layout to prevent clipping of labels
    # plt.tight_layout()

    # # Show the plot
    #plt.show()
    #return correlation_matrix_smoothed['x'], correlation_matrix_smoothed['y'], correlation_matrix_smoothed['z']
    return correlation_matrix['x'], correlation_matrix['y'], correlation_matrix['z']#, correlation_matrix_smoothed['x'], correlation_matrix_smoothed['y'], correlation_matrix_smoothed['z']


