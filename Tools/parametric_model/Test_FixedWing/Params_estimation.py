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
sys.path.append('/home/konrad/Src/data-driven-dynamics/data-driven-dynamics/Tools/parametric_model')

from generate_parametric_model import *

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
info_dict['config'] = '/home/konrad/Src/data-driven-dynamics/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll_velocity.yaml'
# CONFIG: NL, old
# config = '/home/anna/Workspaces/ddd_ws/src/data-driven-dynamics/Tools/parametric_model/configs/fixedwing_model_roll _nonlinear_old_topic.yaml'

""" 
The Log file contains all data needed for the system identification of the specified model as defined in its config file
"""

info_dict['log_path'] = '/home/konrad/Src/data-driven-dynamics/data-driven-dynamics/data/b193e4e1-922d-4394-900b-fed194fccfef.ulg'

# ==============================================================================================================================================

# predict model parameters
start_model_estimation(**(info_dict))

