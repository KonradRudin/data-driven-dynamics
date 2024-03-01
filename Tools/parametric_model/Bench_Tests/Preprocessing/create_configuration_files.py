from pyulog import *
import os

import yaml
from yaml import Loader


def update_rotor_position(input_yaml_file, output_yaml_file, ca_rotor):

    try:
        
        # Get the yanl file for the specific airframe
        with open(input_yaml_file) as f:
            data = yaml.load(f.read(), Loader=Loader)

        # Change the position parameters
        for id, rotor_key in enumerate(ca_rotor.keys()):
            rotor = data['model_config']['actuators']['rotors']['vertical_'][id]
            rotor['position'] = ca_rotor[rotor_key]

        # save the configuration file with the new parameters
        with open(output_yaml_file, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)

    except FileNotFoundError:
        print(f"The file at '{input_yaml_file}' was not found.")

# if CA_ROTOR parameters are available - get position values
def get_rotor_params_data(ulog, numbers_rotors):

    ca_rotor = {}
    for i in range(numbers_rotors):
        pos_x  = ulog.initial_parameters['CA_ROTOR' + str(i) +'_PX']
        pos_y = ulog.initial_parameters['CA_ROTOR' + str(i) +'_PY']
        pos_z = ulog.initial_parameters['CA_ROTOR' + str(i) +'_PZ']

        ca_rotor['rotor' + str(i)] = [pos_x, pos_y, pos_z]
    print(ca_rotor)
    return ca_rotor

# Get number of rotors and path to default configuration file for specific airframe
def data_for_specific_airframe(ulog, path_to_config):
    mav_type = ulog.initial_parameters['MAV_TYPE']
    
    # QUADrotor
    if mav_type == 2: 
        numbers_rotors = 4
        config = path_to_config + 'quadrotor_model.yaml'

    # HEXArotor
    if mav_type == 13: 
        numbers_rotors = 6 
        config = path_to_config + 'hexarotor_model.yaml'
    
    # OCTOrotor
    if mav_type == 14: 
        numbers_rotors = 8
        config = path_to_config + 'octorotor_model.yaml'

    return config, numbers_rotors


output_yaml_path = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/quadrotor_model_1230010.yaml'

path_to_folder = "/home/anna/Documents/logs_ulg/flight_log_usb_stick/Parameters/Quadrotors/1230010"


with os.scandir(path_to_folder) as entries:
    for entry in entries:
        print()
        print(entry.name)

        # file name of log file
        file_name = os.path.join(path_to_folder, entry.name)

        try:
            ulog = ULog(file_name)

        except:
            raise Exception("ULog has wrong format and won't be analyzed")

        # default configuration file for specific airframe
        path_to_config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/'
        config_path, numbers_rotors = data_for_specific_airframe(ulog, path_to_config)

        if any("CA_ROTOR" in params for params in ulog.initial_parameters):
            ca_rotor = get_rotor_params_data(ulog, numbers_rotors)
            update_rotor_position(config_path, output_yaml_path, ca_rotor)
            
            # take yaml file with adapted parameters for further processing
            config_path = output_yaml_path
        
   