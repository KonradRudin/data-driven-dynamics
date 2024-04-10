

import math
import numpy as np

from scipy.spatial.transform import Rotation
from progress.bar import Bar


class RollAngularVelocityModel:
    def __init__(self, config_dict):
        pass

    def compute_wing_moment_features(
        self,
        v_airspeed,
        aileron_input,
        angular_velocity,
        density_air
    ):
        """
        Model description:

        Compute Rolling acceleration

        Rolling moment is modeled as a linear function
        v_Roll_dot = 0.5 * density * V_air_y^2  * (c_L*(ail_left - ail_right) - static + c_L_pv* damping_feature) - inert*ang_vel(1)*ang_vel(2)

        Coefficients for optimization:
        c_L, c_p, ail_static, inert

        :param v_airspeed: airspeed in m/s
        :param ailerons_input: ailerons input
        :param angular_velocity: angular velocity in rad/s

        :return: regression matrix X for the estimation of rolling moment for a single feature
        """

        const = 0.5 * density_air * (v_airspeed**2)

        deflection_al = aileron_input
        

        features = np.array([const * (aileron_input[1] - aileron_input[0]),
                         const * (angular_velocity[0]) / (2 * v_airspeed),
                         -const,
                         +angular_velocity[1]*angular_velocity[2]])

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
            aileron_input_vec[0, :],
            angular_vel_mat[0, :],
            density_air_vec[0]
            )
        aero_features_bar = Bar("Feature Computation", max=v_airspeed_vec.shape[0])
        for i in range(1, len(v_airspeed_vec)):
            X_curr = self.compute_wing_moment_features(
                v_airspeed_vec[i],
                aileron_input_vec[i, :],
                angular_vel_mat[i, :],
                density_air_vec[i]
                )
            X_aero = np.vstack((X_aero, X_curr))
            aero_features_bar.next()
        aero_features_bar.finish()

        coef_dict = {
            "c_L": {"rot": {"x": "c_L"}},
            "c_p": {"rot": {"x": "c_p"}},
            "ail_static": {"rot": {"x": "ail_static"}},
            "inert": {"rot": {"x": "inert"}},
        }
        col_names = [
            "c_L",
            "c_p",
            "ail_static",
            "inert",
        ]

        return X_aero, coef_dict, col_names
