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

import math
import numpy as np

from scipy.spatial.transform import Rotation
from progress.bar import Bar


class LinearWingRollModel:
    def __init__(self, config_dict):
        self.air_density = 1.225
        self.gravity = 9.81
        self.area = config_dict["area"]
        self.chord = config_dict["chord"]


    def compute_wing_moment_features(
        self,
        v_airspeed,
        aileron_input,
        angular_velocity,
        density_air
    ):
        """
        Model description:

        Compute Rolling moment

        Rolling moment is modeled as a linear function
        M_Roll = 0.5 * density * V_air_y^2  * (c_L_al + c_L_ar + c_L_pv* damping_feature)

        Coefficients for optimization:
        c_L_al, c_L_ar, c_L_pv

        :param v_airspeed: airspeed in m/s
        :param ailerons_input: ailerons input
        :param angular_velocity: angular velocity in rad/s

        :return: regression matrix X for the estimation of rolling moment for a single feature
        """

        #vel_y = np.sqrt(v_airspeed[0] ** 2 + v_airspeed[1]**2 + v_airspeed[2] ** 2)
        vel_y = v_airspeed
        const = 0.5 * density_air * (vel_y**2)

        # X_wing_aero_frame = np.zeros((3, 3))

        deflection_al = aileron_input
        deflection_ar = - deflection_al

        features = np.array([const * deflection_ar,
                         const * deflection_al,
                         const * (angular_velocity[0]) / (2 * vel_y)])

        return features #X_wing_aero_frame.flatten()


    def compute_aero_moment_features(
            self,
            v_airspeed_vec,
            aileron_input_vec,
            angular_vel_mat,
            density_air_vec
        ):
        """
        Inputs:

        v_airspeed_mat: airspeed in m/s with format numpy array of dimension (n,3) with columns for [v_a_x, v_a_y, v_a_z]
        aileron_input_vec: vector of size (n) with corresponding aileron deflection values
        angular_vel_mat: airspeed in m/s with format numpy array of dimension (n,3) with columns for [p, q, r]

        Returns:
        X_aero: regression matrix for the estimation of rolling moment
        coef_dict: dictionary of coefficients for optimization
        col_names: column names corresponding to the coefficients
        """

        print("Starting computation of aero moment features...")
        X_aero = self.compute_wing_moment_features(
            v_airspeed_vec[0],
            aileron_input_vec[0],
            angular_vel_mat[0, :],
            density_air_vec[0]
            )
        aero_features_bar = Bar("Feature Computation", max=v_airspeed_vec.shape[0])
        for i in range(1, len(aileron_input_vec)):
            X_curr = self.compute_wing_moment_features(
                v_airspeed_vec[i],
                aileron_input_vec[i],
                angular_vel_mat[i, :],
                density_air_vec[i]
                )
            X_aero = np.vstack((X_aero, X_curr))
            aero_features_bar.next()
        aero_features_bar.finish()

        coef_dict = {
            "c_L_al": {"rot": {"x": "c_L_al_x"}},
            "c_L_ar": {"rot": {"x": "c_L_ar_x"}},
            "c_L_pv": {"rot": {"x": "c_L_pv_x"}},
        }
        col_names = [
            "c_L_al_x",
            "c_L_ar_x",
            "c_L_pv_x",
        ]
        return X_aero, coef_dict, col_names
