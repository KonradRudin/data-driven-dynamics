

import math
import numpy as np

from scipy.spatial.transform import Rotation
from progress.bar import Bar


class NonLinearWingRollModel:
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

        const = 0.5 * density_air * (v_airspeed**2)

        deflection_al = aileron_input
        deflection_ar = - deflection_al

        features = np.array([const * deflection_ar,
                         const * deflection_al,
                         const * (angular_velocity[0]) / (2 * v_airspeed),
                         1])

        return features 


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
            "t_d": {"rot": {"x": "t_d_x"}},
        }
        col_names = [
            "c_L_al_x",
            "c_L_ar_x",
            "c_L_pv_x",
            "t_d_x",
        ]

        return X_aero, coef_dict, col_names
