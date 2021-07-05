__author__ = "Manuel Galliker"
__maintainer__ = "Manuel Galliker"
__license__ = "BSD 3"

""" The model class contains properties shared between all models and shgall simplyfy automated checks and the later
export to a sitl gazebo model by providing a unified interface for all models. """

from progress.bar import Bar
import pandas as pd
import math
import time
import yaml
import numpy as np
from src.models.model_config import ModelConfig

from src.tools.ulog_tools import load_ulog, pandas_from_topic
from src.tools.dataframe_tools import compute_flight_time, resample_dataframe_list
from src.tools.quat_utils import quaternion_to_rotation_matrix


class DataHandler():
    def __init__(self, config_file="qpm_gazebo_standard_vtol_config.yaml"):
        self.config = ModelConfig(config_file)
        config_dict=self.config.dynamics_model_config

        assert type(
            config_dict) is dict, 'req_topics_dict input must be a dict'
        assert bool(config_dict), 'req_topics_dict can not be empty'
        self.config_dict = config_dict
        self.resample_freq = config_dict["resample_freq"]
        print("Resample frequency: ", self.resample_freq, "Hz")
        self.req_topics_dict = config_dict["data"]["required_ulog_topics"]
        self.req_dataframe_topic_list = config_dict["data"]["req_dataframe_topic_list"]

        self.visual_dataframe_selector_config_dict = {
            "x_axis_col": "timestamp",
            "sub_plt1_data": ["q0", "q1", "q2", "q3"],
            "sub_plt2_data": ["u0", "u1", "u2", "u3"]}

        self.estimate_forces = config_dict["estimate_forces"]
        self.estimate_moments = config_dict["estimate_moments"]

        # used to generate a dict with the resulting coefficients later on.
        self.coef_name_list = []
        self.result_dict = {}
    
    def loadLog(self, rel_data_path):
        self.rel_data_path = rel_data_path

        if (rel_data_path[-4:] == ".csv"):
            self.data_df = pd.read_csv(rel_data_path, index_col=0)
            for req_topic in self.req_dataframe_topic_list:
                assert(
                    req_topic in self.data_df), ("missing topic in loaded csv: " + str(req_topic))

        elif (rel_data_path[-4:] == ".ulg"):

            self.ulog = load_ulog(rel_data_path)
            self.check_ulog_for_req_topics()

            self.compute_resampled_dataframe()

        else:
            print("ERROR: file extension needs to be either csv or ulg:")
            print(rel_data_path)
            exit(1)

    def check_ulog_for_req_topics(self):
        for topic_type in self.req_topics_dict.keys():
            try:
                topic_type_data = self.ulog.get_dataset(topic_type)

            except:
                print("Missing topic type: ", topic_type)
                exit(1)

            topic_type_data = topic_type_data.data
            ulog_topic_list = self.req_topics_dict[topic_type]["ulog_name"]
            for topic_index in range(len(ulog_topic_list)):
                try:
                    topic = ulog_topic_list[topic_index]
                    topic_data = (topic_type_data[topic])
                except:
                    print("Missing topic: ", topic_type,
                          ulog_topic_list[topic_index])
                    exit(1)

        return

    def compute_resampled_dataframe(self):
        print("Starting data resampling of topic types: ",
              self.req_topics_dict.keys())
        # setup object to crop dataframes for flight data
        fts = compute_flight_time(self.ulog)
        df_list = []
        topic_type_bar = Bar('Resampling', max=len(
            self.req_topics_dict.keys()))

        # getting data
        for topic_type in self.req_topics_dict.keys():
            topic_dict = self.req_topics_dict[topic_type]
            curr_df = pandas_from_topic(self.ulog, [topic_type])
            curr_df = curr_df[topic_dict["ulog_name"]]
            if "dataframe_name" in topic_dict.keys():
                assert (len(topic_dict["dataframe_name"]) == len(topic_dict["ulog_name"])), (
                    'could not rename topics of type', topic_type, "due to rename list not having an entry for every topic.")
                curr_df.columns = topic_dict["dataframe_name"]
            df_list.append(curr_df)
            topic_type_bar.next()
        topic_type_bar.finish()
        resampled_df = resample_dataframe_list(
            df_list, fts, self.resample_freq)
        self.data_df = resampled_df.dropna()

    def visually_select_data(self, plot_config_dict=None):
        from visual_dataframe_selector.data_selector import select_visual_data
        print("Number of data samples before cropping: ",
              self.data_df.shape[0])
        self.data_df = select_visual_data(
            self.data_df, self.visual_dataframe_selector_config_dict)

    def get_dataframes(self):
        return self.data_df