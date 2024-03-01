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
sys.path.append('Tools/parametric_model')
from generate_parametric_model import *


import csv
import math
import statistics 


""" 

The model, which is designed to predict whether a log file is a bench test or not, 
uses parameters derived from the median values. 
These medians are calculated from multiple flights of the same drone type ('SYS_AUTOSTART'), 
which should ensure robustness against outliers.

"""


def median_approach(folder_path):

    # List to store coefficients for each type
    coefficients_by_type = {}

    # Iterate over YAML files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml"):
            file_path = os.path.join(folder_path, filename)

            # Load YAML file
            with open(file_path, 'r') as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)

            # Extract coefficients (replace 'coefficients' with the actual key in your YAML file)
            coefficients = yaml_data.get("coefficients")

            has_zeros = any(value == 0 for value in coefficients.values())

            # Store coefficients by type
            if coefficients and not has_zeros:
                for coefficient_type, value in coefficients.items():
                    coefficients_by_type.setdefault(coefficient_type, []).append(value)

    medians_by_type = {}
    for coefficient_type, values in coefficients_by_type.items():
        median_value = statistics.median(values)
        medians_by_type[coefficient_type] = median_value
    
    return medians_by_type

def create_new_yaml_file(medians_by_type, output_file_path):
    
    # Create a dictionary with the key "coefficients"
    output_dict = {"coefficients": medians_by_type}

    with open(output_file_path, 'w') as output_file:
        yaml.dump(output_dict, output_file, default_flow_style=False)




#Path to the folder containing YAML files
folder_path = "model_results_airframes/model_results_quadrotors/1230010/model_results_estimation_1230010_measured_params"
# path where new yaml file should be saved
output_file_path = "model_results_airframes/model_results_quadrotors/model_results_median/median_1230010_measured_params.yaml"
medians_by_type = median_approach(folder_path)
create_new_yaml_file(medians_by_type, output_file_path)
