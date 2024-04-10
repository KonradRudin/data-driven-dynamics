"""
 *
 * Copyright (c) 2023 Julius Schlapbach
 *               2023 Autonomous Systems Lab ETH Zurich
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

__author__ = "Julius Schlapbach"
__maintainer__ = "Julius Schlapbach"
__license__ = "BSD 3"


import numpy as np

from . import aerodynamic_models
from .dynamics_model import DynamicsModel
from .model_config import ModelConfig
from matplotlib import pyplot as plt
from scipy.spatial.transform import Rotation
from scipy.integrate import odeint



class FixedWingRollAngularVelModel(DynamicsModel):
    def __init__(
        self, config_file, normalization=True, model_name="simple_fixedwing_model"
    ):
        self.config = ModelConfig(config_file)
        super(FixedWingRollAngularVelModel, self).__init__(
            config_dict=self.config.dynamics_model_config, normalization=normalization
        )

        self.model_name = model_name

        # self.rotor_config_dict = self.config.model_config["actuators"]["rotors"]
        self.aerodynamics_dict = self.config.model_config["aerodynamics"]

        try:
            self.aero_model = getattr(
                aerodynamic_models, self.aerodynamics_dict["type"]
            )(self.aerodynamics_dict)
        except AttributeError:
            error_str = (
                "Aerodynamics Model '{0}' not found, is it added to models "
                "directory and models/__init__.py?".format(self.aerodynamics_dict.type)
            )
            raise AttributeError(error_str)


    def prepare_moment_regression_matrices(self):

        # true airspeed in m/s
        true_airspeed = self.data_df['true_airspeed_m_s'].to_numpy()

        # air density 
        density_air = self.data_df['rho'].to_numpy()

        angular_vel_mat = self.data_df[
            ["ang_vel_x", "ang_vel_y", "ang_vel_z"]
        ].to_numpy()
        
        aileron_inputs = self.data_df[
            ["c0", "c1"]
        ].to_numpy()

        (
            X_aero,
            coef_dict_aero,
            col_names_aero,
        ) = self.aero_model.compute_aero_moment_features(
            true_airspeed, aileron_inputs, angular_vel_mat, density_air
        )

        self.data_df[col_names_aero] = X_aero
        self.coef_dict.update(coef_dict_aero)
        self.col_names_aero = col_names_aero
        self.X_aero = X_aero

        self.y_dict.update(
            {
                "rot": {
                    "x": "ang_acc_b_x",
                }
            }
        )

    # =========== SANITY Check=========
    def plot(self, raw_data, detrend_data, time):
        time = time/1000000 #[s]
        plt.figure(figsize=(10, 5))
        plt.plot(time[:100], raw_data[:100], label='Raw Data', linestyle='-', marker='o', markersize=1)
        plt.plot(time[:100], detrend_data[:100], label='Detrended Data', linestyle='-', marker='.', markersize=1, alpha=0.7)
        plt.xlabel('Time [s]')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()
        

    def plot_input(self):
        time = self.data_df["timestamp"].to_numpy()/1000000
        fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
        fig.suptitle('Input Data') 
        aileron_servo = self.data_df[["c0", "c1"]].to_numpy()
        ax1.plot(time, aileron_servo[:,0], label='first aileron')
        ax1.plot(time, aileron_servo[:,1], label='second aileron')
        #ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('Servo output')
        ax1.legend()
        ax1.grid(True)
        
        roll_vel = self.data_df[["ang_vel_x"]].to_numpy()
        ax2.plot(time, roll_vel, label='roll ang vel')
        #ax2.set_xlabel('Time [s]')
        ax2.set_ylabel('roll ang vel [rad/s]')
        #ax2.legend()
        ax2.grid(True)

        roll_acc = self.data_df[["ang_acc_b_x"]].to_numpy()
        ax3.plot(time, roll_acc, label='roll ang vel')
        ax3.set_xlabel('Time [s]')
        ax3.set_ylabel('roll ang acc [rad/s**2]')
        ax3.grid(True)
        plt.show()
