import os
import yaml

from pyulog import *
from pyulog.px4 import *
from pyulog.core import *

import matplotlib.pyplot as plt


def params_histogram(folder_path):

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
            # Store coefficients by type
            #if coefficients:
                for coefficient_type, value in coefficients.items():
                    coefficients_by_type.setdefault(coefficient_type, []).append(value)

    # Create subplots for each type of coefficient with two columns
    num_types = len(coefficients_by_type)
    num_rows = (num_types + 1) // 2  # Ensure at least 1 row
    fig, axes = plt.subplots(nrows=num_rows, ncols=2, figsize=(12, 5 * num_rows))

    # Flatten the axes array to iterate over it easily
    axes_flat = axes.flatten()

    for i, (coefficient_type, values) in enumerate(coefficients_by_type.items()):
        ax = axes_flat[i]
        ax.hist(values, bins=50, color='blue', edgecolor='black')
        ax.set_title(f'{coefficient_type}')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.grid(True)

    # Hide any unused subplots
    for j in range(i + 1, len(axes_flat)):
        axes_flat[j].axis('off')

    plt.tight_layout()
    plt.show()


# Path to the folder containing YAML files with estimated parameters
folder_path = "model_results_estimation_RollModel/check_rover"

# checking how far the spreading is of the estimation of the parameters of a specific dronetype
params_histogram(folder_path)
