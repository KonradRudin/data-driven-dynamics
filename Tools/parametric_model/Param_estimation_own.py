
import numpy as np
import pandas as pd

from pyulog import *
from pyulog.px4 import *
from pyulog.core import *

from scipy import fft, signal
import matplotlib.pyplot as plt
import math

from generate_parametric_model import *
from src.models.aerodynamic_models.roll_angular_velocity_model import *
from sklearn.linear_model import LinearRegression
from src.tools.dataframe_tools import *
from src.tools import math_tools

import logging
# Set the logging level 
logging.basicConfig(level=logging.INFO)

# ==============================================================================================================================================
# Pipeline Arguments
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
info_dict['data_selection']  = 'interactive'

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
info_dict['config'] = 'Tools/parametric_model/configs/fixedwing_model_roll_velocity.yaml'
# CONFIG: NL, old
# config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll _nonlinear_old_topic.yaml'

""" 
The Log file contains all data needed for the system identification of the specified model as defined in its config file
"""

info_dict['log_path'] = 'data/b0ab77e2-d4d6-48ea-b1fe-23b8fb6a3def.ulg'

# ==============================================================================================================================================

# Load data
logging.info("Loading data")
data_df = start_model_load_data(**(info_dict))


logging.info("Prepare regression matrix")

# time
time = data_df["timestamp"].to_numpy()/1000000

# true airspeed in m/s
true_airspeed = data_df['true_airspeed_m_s'].to_numpy()

# air density 
density_air = data_df['rho'].to_numpy()

angular_vel_mat = data_df[
    ["ang_vel_x", "ang_vel_y", "ang_vel_z"]
].to_numpy()

angular_acc_x_onboard = data_df['ang_acc_x'].to_numpy()

aileron_inputs = data_df[
    ["c0", "c1"]
].to_numpy()

fig, ax = plt.subplots(4, sharex=True)
ax[0].plot(time, true_airspeed)
ax[0].set_xlabel("time [s]")
ax[0].set_ylabel("airspeed [m/s]")
ax[0].grid()
ax[1].plot(time, density_air)
ax[1].set_xlabel("time [s]")
ax[1].set_ylabel("air density [kg/m**3]")
ax[1].grid()
ax[2].plot(time, angular_vel_mat[:,0], label="x")
ax[2].plot(time, angular_vel_mat[:,1], label="y")
ax[2].plot(time, angular_vel_mat[:,2], label="z")
ax[2].set_xlabel("time [s]")
ax[2].set_ylabel("angular velocity [rad/s]")
ax[2].grid()
ax[2].legend()
ax[3].plot(time, aileron_inputs[:,0], label="first")
ax[3].plot(time, aileron_inputs[:,1], label="second")
ax[3].set_xlabel("time [s]")
ax[3].set_ylabel("aileron deflection in [-1, 1] [-]")
ax[3].grid()
ax[3].legend()

plt.show()

logging.info("Analyze the angular velocity")

delta_t = np.average(np.diff(time)[1:-1])
logging.info("The frequency of this dataset is " + str(delta_t))

# make an fft 
ang_vel_fft = fft.fft(angular_vel_mat[:,0])

N = len(angular_vel_mat[:,0])
chosen_freq = [0.05, 8]
freqsplot = fft.fftfreq(N, delta_t)
plt.figure()
plt.semilogx(freqsplot[:N//2], np.log10(np.abs(ang_vel_fft[:N//2])/N))
plt.xlabel("Freq [Hz]")
plt.ylabel("Mag")
plt.grid(True)
plt.axvline(chosen_freq[0])
plt.axvline(chosen_freq[1])
plt.show()

# create a butterworth bandpass filter
sys_nom, sys_den = signal.butter(2, chosen_freq, 'bandpass', analog=True)
sys = signal.TransferFunction(sys_nom,sys_den)
logging.info("Continuous butterworth bandpass filter parameters")
print(sys)
print(signal.tf2ss(sys_nom,sys_den))

sos_bp = signal.butter(2, chosen_freq, 'bandpass', fs=1/delta_t, output='sos')
ang_vel_bp = signal.sosfilt(sos_bp, angular_vel_mat[:,0])

# Get the angular acceleration
ang_acc_x_bp_gradient = np.gradient(ang_vel_bp, time)
ang_acc_x_gradient = np.gradient(angular_vel_mat[:,0], time)
ang_vel_x_filtered = sav_gol_filter(angular_vel_mat[:,0], window_length = 20, polyorder=2)
ang_acc_x_filtered_gradient = np.gradient(ang_vel_x_filtered, time)

fix, ax = plt.subplots(2, sharex=True)
ax[0].plot(time, angular_vel_mat[:,0], label='measured')
ax[0].plot(time, ang_vel_x_filtered, label='filtered')
ax[0].plot(time, ang_vel_bp, label='bandpass')
ax[0].set_xlabel("time [s]")
ax[0].set_ylabel("angular velocity [rad/s]")
ax[0].grid()
ax[0].legend()
#ax[1].plot(time, angular_acc_x_onboard, label='onboard')
ax[1].plot(time, ang_acc_x_gradient, label='gradient')
ax[1].plot(time, ang_acc_x_filtered_gradient, label='filtered gradient')
ax[1].plot(time, ang_acc_x_bp_gradient, label='bp gradient')
ax[1].set_xlabel("time [s]")
ax[1].set_ylabel("angular acceleration [rad/s**2]")
ax[1].grid()
ax[1].legend()

plt.show()

# estimate the parameters
model = RollAngularVelocityModel({})
ang_vel_mat = angular_vel_mat
ang_vel_mat[:,0] = ang_vel_x_filtered
X_regr, _ , coef_names = model.compute_aero_moment_features(true_airspeed, aileron_inputs, angular_vel_mat, density_air)

logging.info("Make linear regression")
max_time_shift = 0.3
best_shift = 0
best_rmse = 100000000
ang_acc_to_use = ang_acc_x_filtered_gradient
best_acc_pred = np.zeros(np.shape(ang_acc_to_use))
best_coef = [0,0,0,0]
for shift in range(1, int(max_time_shift/delta_t)):
    regression = LinearRegression(fit_intercept=True)
    regression.fit(X_regr[:-shift,], ang_acc_to_use[shift:], np.absolute(ang_acc_to_use[shift:]))

    y_acc_pred = regression.predict(X_regr[:-shift,])

    current_rmse = math_tools.rmse_between_numpy_arrays(y_acc_pred, ang_acc_to_use[shift:])

    if current_rmse < best_rmse:
        best_shift = shift
        best_rmse = current_rmse
        best_acc_pred = y_acc_pred
        best_coef = regression.coef_

logging.info(" RMSE: " + str(best_rmse) + " on time shift " + str(best_shift*delta_t))
logging.info("Estimated params: " + str(coef_names) + " = " + str(best_coef))
best_coef[2] = best_coef[2]/best_coef[0]
# plot the best match
y_vel_pred = np.zeros((2,len(ang_vel_x_filtered)))
y_vel_pred[0,0] = ang_vel_x_filtered[0]
y_vel_pred[1,0] = aileron_inputs[0,1] - aileron_inputs[0,0]

for i in range(1, len(ang_vel_x_filtered)):
    y_vel_pred[1,i] = y_vel_pred[1,i-1] + delta_t/(best_shift*delta_t) * (aileron_inputs[i-1,1] - aileron_inputs[i-1,0] - y_vel_pred[1,i-1])
    #y_vel_pred[1,i] = y_vel_pred[1,i-1] + 1. * (aileron_inputs[i-1,0] - aileron_inputs[i-1,1] - y_vel_pred[1,i-1])
    y_vel_pred[0,i] = y_vel_pred[0,i-1] + delta_t*(0.5*density_air[i-1]*(true_airspeed[i-1]**2)*(best_coef[0]*(y_vel_pred[1,i-1] - best_coef[2]) + best_coef[1]*y_vel_pred[0,i-1]/(2*true_airspeed[i-1])) + best_coef[3]*ang_vel_mat[i-1,1]*ang_vel_mat[i-1,2])


fig, ax = plt.subplots(3, sharex=True)

ax[0].plot(time[best_shift:], ang_acc_to_use[best_shift:], label='measured')
ax[0].plot(time[best_shift:], best_acc_pred, label='predicted')
ax[0].set_xlabel('time [s]')
ax[0].set_ylabel('Angular acceleration [rad/s**2]')
ax[0].grid()
ax[0].legend()

ax[1].plot(time, ang_vel_x_filtered, label='measured')
ax[1].plot(time, y_vel_pred[0,:], label='predicted')
ax[1].set_xlabel('time [s]')
ax[1].set_ylabel('Angular velocity [rad/s]')
ax[1].grid()
ax[1].legend()

ax[2].plot(time, signal.sosfilt(sos_bp, ang_vel_x_filtered), label='measured')
ax[2].plot(time, signal.sosfilt(sos_bp, y_vel_pred[0,:]), label='predicted')
ax[2].set_xlabel('time [s]')
ax[2].set_ylabel('Angular velocity [rad/s]')
ax[2].grid()
ax[2].legend()

plt.show()
