"""
 *
 * Copyright (c) 2021 Manuel Yves Galliker
 *               2021 Autonomous Systems Lab ETH Zurich
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 3. Neither the name Data Driven Dynamics nor the names of its contributors may be
 *    used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
"""

__author__ = "Manuel Yves Galliker"
__maintainer__ = "Manuel Yves Galliker"
__license__ = "BSD 3"

import matplotlib.pyplot as plt
import numpy as np
import math

from src.tools.dataframe_tools import sav_gol_filter

plt.rcParams["mathtext.fontset"] = "cm"

"""The functions in this file can be used to plot data of any kind of model"""


def plot_force_predictions(stacked_force_vec, stacked_force_vec_pred, timestamp_array):
    """
    Input:
    stacked_force_vec: numpy array of shape (3*n,1) containing stacked accelerations [a_x_1, a_y_1, a_z_1, a_x_2, ...]^T in body frame
    stacked_force_vec_pred: numpy array of shape (3*n,1) containing stacked predicted accelerations [a_x_1, a_y_1, a_z_1, a_x_2, ...]^T in body frame
    timestamp_array: numpy array with n entries of corresponding timestamps.
    """

    stacked_force_vec = np.array(stacked_force_vec)
    stacked_force_vec_pred = np.array(stacked_force_vec_pred)
    timestamp_array = np.array(timestamp_array) / 1000000

    acc_mat = stacked_force_vec.reshape((-1, 3))
    acc_mat_pred = stacked_force_vec_pred.reshape((-1, 3))

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    fig.suptitle("Predictions of Forces in Body Frame [N]")
    ax1.plot(timestamp_array, acc_mat[:, 0], label="measurement")
    ax1.plot(timestamp_array, acc_mat_pred[:, 0], label="prediction")
    ax2.plot(timestamp_array, acc_mat[:, 1], label="measurement")
    ax2.plot(timestamp_array, acc_mat_pred[:, 1], label="prediction")
    ax3.plot(timestamp_array, acc_mat[:, 2], label="measurement")
    ax3.plot(timestamp_array, acc_mat_pred[:, 2], label="prediction")

    ax1.set_ylabel("$x$")
    ax2.set_ylabel("$y$")
    ax3.set_ylabel("$z$")
    ax3.set_xlabel("time [s]")
    plt.legend()
    return


def plot_moment_predictions(
    stacked_moment_vec, stacked_moment_vec_pred, timestamp_array, roll_rate, V_T, air_density, aileron_input
):
    """
    Input:
    stacked_moment_vec: numpy array of shape (3*n,1) containing stacked angular accelerations [w_x_1, w_y_1, w_z_1, w_x_2, ...]^T in body frame
    stacked_moment_vec_pred: numpy array of shape (3*n,1) containing stacked predicted angular accelerations [w_x_1, w_y_1, w_z_1, w_x_2, ...]^T in body frame
    timestamp_array: numpy array with n entries of corresponding timestamps.
    """

    stacked_moment_vec = np.array(stacked_moment_vec)
    stacked_moment_vec_pred = np.array(stacked_moment_vec_pred)
    timestamp_array = np.array(timestamp_array) / 1000000

    acc_mat = stacked_moment_vec.reshape((-1, 3))
    acc_mat_pred = stacked_moment_vec_pred.reshape((-1, 3))

    roll_rate_dot_pred = acc_mat_pred[:, 0]

    # apply filter to output data
    roll_rate_dot_pred_filtered = sav_gol_filter(roll_rate_dot_pred)

    #plot_roll_prediciton(timestamp_array, rr_dot_meas = acc_mat[:, 0], rr_dot_pred=roll_rate_dot_pred, rr_meas = roll_rate, title = 'Roll model identifier')
    plot_roll_prediciton(timestamp_array, rr_dot_meas = acc_mat[:, 0], rr_dot_pred=roll_rate_dot_pred_filtered, rr_meas = roll_rate, title = 'Roll model identifier')

    plt.show()
    return


def plot_airspeed_and_AoA(airspeed_mat, timestamp_array):
    """
    Input:
    airspeed_mat: numpy array Matrix of shape (n,4) containing
    the columns [V_a_x, V_a_y, V_a_z, AoA].
    timestamp_array: numpy array with n entries of corresponding timestamps.
    """

    airspeed_mat = np.array(airspeed_mat)
    timestamp_array = np.array(timestamp_array)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4)
    fig.suptitle("Airspeed and Angle of Attack")
    ax1.plot(timestamp_array, airspeed_mat[:, 0], label="measurement")
    ax2.plot(timestamp_array, airspeed_mat[:, 1], label="measurement")
    ax3.plot(timestamp_array, airspeed_mat[:, 2], label="measurement")
    ax4.plot(timestamp_array, airspeed_mat[:, 3], label="measurement")
    ax1.set_title(r"Airspeed in body-$x$ [m/s^2]")
    ax2.set_title(r"Airspeed in body-$y$ [m/s^2]")
    ax3.set_title(r"Airspeed in body-$z$ [m/s^2]")
    ax4.set_title("AoA in body frame [radians]")
    plt.legend()

    return


def plot_actuator_inputs(actuator_mat, actuator_name_list, timestamp_array):
    """
    Input:
    input_mat
    actuator_name_list
    timestamp_array: numpy array with n entries of corresponding timestamps.
    """

    airspeed_mat = np.array(actuator_mat)
    timestamp_array = np.array(timestamp_array) / 1000000

    n_actuator = actuator_mat.shape[1]
    fig, (ax1) = plt.subplots(1)
    fig.suptitle("Normalized Actuator Inputs")
    for i in range(n_actuator):
        ax1.plot(timestamp_array, actuator_mat[:, i], label=actuator_name_list[0])

    ax1.set_ylabel("normalized actuator output")
    ax1.set_xlabel("time [s]")
    plt.legend()
    return


def plot_accel_and_airspeed_in_y_direction(
    stacked_acc_vec, stacked_acc_vec_pred, v_a_y, timestamp_array
):
    """
    Input:
    acc_vec: numpy array of shape (3*n,1) containing stacked accelerations [a_x_1, a_y_1, a_z_1, a_x_2, ...]^T in body frame
    acc_vec_pred: numpy array of shape (3*n,1) containing stacked predicted accelerations [a_x_1, a_y_1, a_z_1, a_x_2, ...]^T in body frame
    v_a_y: numpy array of shape (n,1) containing the airspeed in y direction
    timestamp_array: numpy array with n entries of corresponding timestamps.
    """

    stacked_acc_vec = np.array(stacked_acc_vec)
    stacked_acc_vec_pred = np.array(stacked_acc_vec_pred)
    v_a_y = np.array(v_a_y)
    x_drag_y = np.zeros(v_a_y.shape[0])
    for i in range(x_drag_y.shape[0]):
        x_drag_y[i] = -math.copysign(1, v_a_y[i]) * v_a_y[i] ** 2
    timestamp_array = np.array(timestamp_array)

    acc_mat = stacked_acc_vec.reshape((-1, 3))
    acc_mat_pred = stacked_acc_vec_pred.reshape((-1, 3))

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.suptitle("Acceleration and Airspeed in y direction")
    ax1.plot(timestamp_array, v_a_y, label="measurement")
    ax2.plot(timestamp_array, x_drag_y, label="measurement")
    ax3.plot(timestamp_array, acc_mat[:, 1], label="measurement")
    ax3.plot(timestamp_array, acc_mat_pred[:, 1], label="prediction")
    ax1.set_title("airspeed in y direction of body frame [m/s^2]")
    ax2.set_title("features corresponding to drag in y direction")
    ax3.set_title("acceleration y direction of body frame [m/s^2]")
    plt.legend()
    return


def plot_accel_and_airspeed_in_z_direction(
    stacked_acc_vec, stacked_acc_vec_pred, v_a_z, timestamp_array
):
    """
    Input:
    acc_vec: numpy array of shape (3*n,1) containing stacked accelerations [a_x_1, a_y_1, a_z_1, a_x_2, ...]^T in body frame
    acc_vec_pred: numpy array of shape (3*n,1) containing stacked predicted accelerations [a_x_1, a_y_1, a_z_1, a_x_2, ...]^T in body frame
    v_a_z: numpy array of shape (n,1) containing the airspeed in y direction
    timestamp_array: numpy array with n entries of corresponding timestamps.
    """

    stacked_acc_vec = np.array(stacked_acc_vec)
    stacked_acc_vec_pred = np.array(stacked_acc_vec_pred)
    v_a_z = np.array(v_a_z)
    x_drag_z = np.zeros(v_a_z.shape[0])
    for i in range(x_drag_z.shape[0]):
        x_drag_z[i] = -math.copysign(1, v_a_z[i]) * v_a_z[i] ** 2
    timestamp_array = np.array(timestamp_array)

    acc_mat = stacked_acc_vec.reshape((-1, 3))
    acc_mat_pred = stacked_acc_vec_pred.reshape((-1, 3))

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    fig.suptitle("Acceleration and Airspeed in z direction")
    ax1.plot(timestamp_array, v_a_z, label="measurement")
    ax2.plot(timestamp_array, x_drag_z, label="measurement")
    ax3.plot(timestamp_array, acc_mat[:, 2], label="measurement")
    ax3.plot(timestamp_array, acc_mat_pred[:, 2], label="prediction")
    ax1.set_title("airspeed in z direction of body frame [m/s^2]")
    ax2.set_title("- sign(v_a)*v_a^2 in body frame [m/s^2]")
    ax3.set_title("acceleration z direction of body frame [m/s^2]")
    plt.legend()
    return


def plot_az_and_collective_input(
    stacked_acc_vec, stacked_acc_vec_pred, u_mat, timestamp_array
):
    u_mat = np.array(u_mat)
    u_collective = np.zeros(u_mat.shape[0])
    for i in range(u_mat.shape[1]):
        u_collective = u_collective + u_mat[:, i]

    stacked_acc_vec = np.array(stacked_acc_vec)
    stacked_acc_vec_pred = np.array(stacked_acc_vec_pred)
    acc_mat = stacked_acc_vec.reshape((-1, 3))
    acc_mat_pred = stacked_acc_vec_pred.reshape((-1, 3))

    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle("Acceleration and Collective Input in z direction")
    ax1.plot(timestamp_array, u_collective, label="measurement")
    ax2.plot(timestamp_array, acc_mat[:, 2], label="measurement")
    ax2.plot(timestamp_array, acc_mat_pred[:, 2], label="prediction")
    ax1.set_title("collective input")
    ax2.set_title("acceleration in z direction of body frame [m/s^2]")
    plt.legend()


def plot(data, timestamp, plt_title="No title"):
    plt.plot(timestamp, data)
    plt.title(plt_title)


def plot_roll_prediciton(timestamp_array, rr_dot_meas, rr_dot_pred, rr_meas, title):
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    fig.suptitle(title)
    # Roll Acceleration: Measurement vs Prediciton
    ax1.plot(timestamp_array, rr_dot_meas, label="Measurement: Vehicle_angular_velocity_xyz[0]_derivative")
    ax1.plot(timestamp_array, rr_dot_pred, label="Prediction: Roll Rate Derivative", alpha=0.7)
    ax1.legend()

    # Roll Rate: Measurement vs Integrated Predicition
    integrated_result = integrate_cum_trap(rr_dot_pred, timestamp_array, rr_meas)
    t_values, y_values = integration_RK45(rr_dot_pred, timestamp_array, rr_meas)

    # Cum_trap
    ax2.plot(timestamp_array, rr_meas, label="Measurement: Roll Rate (vehicle_angular_velocity_xyz[0])")
    ax2.plot(timestamp_array[:len(integrated_result)], integrated_result, label="Integrated prediction, Cum_Trap", alpha=0.7)
    ax2.legend()
    # RK45
    ax3.plot(timestamp_array, rr_meas, label="Measurement: Roll Rate (vehicle_angular_velocity_xyz[0])")
    ax3.plot(t_values, y_values, label="Integrated prediction, RK45", alpha=0.7)
    ax3.legend()

    ax1.set_ylabel("$p_{dot} [rad/s^2]$")
    ax1.set_xlabel("time [s]")
    ax2.set_ylabel("$p [rad/s]$")
    ax2.set_xlabel("time [s]")
    ax3.set_ylabel("$p [rad/s]$")
    ax3.set_xlabel("time [s]")
    
    plt.legend()



# ====================== INTEGRATION METHODS =========================================================================================
from scipy.integrate import cumtrapz
def integrate_cum_trap(data, time, roll_rate):
    # Ensure both data and time are numpy arrays
    data = np.array(data)
    time = np.array(time)

    # Calculate time intervals from the timestamp array
    time_intervals = np.diff(time, prepend=0)

    # Perform cumulative trapezoidal integration
    integrated_result = cumtrapz(data, x=time, dx=time_intervals, initial=roll_rate[0])

    return integrated_result

def manual_integration(roll_acc, time):
    roll_rate = [0.0]  # Initialize the roll rate with 0.0

    for id, acc in enumerate(roll_acc):
        if id == 0:
            continue
        delta_t = time[id] - time[id-1]
        delta_roll_rate = acc * delta_t
        current_roll_rate = roll_rate[-1] + delta_roll_rate
        roll_rate.append(current_roll_rate)

    return roll_rate


from scipy.integrate import RK45
def integration_RK45(roll_acc_func, time, roll_rate):
    # The right-hand side function (roll rate derivative)
    def fun(t, y):
        # Roll_acc_func, array containing roll accelerations over time
        idx = np.searchsorted(time, t) - 1  # Find the index corresponding to the current time
        return roll_acc_func[idx]

    # Set initial conditions
    t0 = time[0]
    y0 = [roll_rate[0]]

    # Create RK45 solver
    solver = RK45(fun, t0, y0, t_bound=time[-1], vectorized=True)

    # Arrays to store the results
    t_values = [solver.t]
    y_values = [solver.y[0]]

    # Integrate using RK45
    while solver.status == 'running':
        solver.step()
        t_values.append(solver.t)
        y_values.append(solver.y[0])

    return t_values, y_values


