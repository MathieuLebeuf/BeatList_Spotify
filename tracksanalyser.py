import statistics
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')

"""
Tracks data manipulation module.

This module provides functions for extracting informations and statistic analysis from the list of tracks (list of dicts).

This module include:
==================                             =============================================
Function                                       Description
==================                             =============================================
convert_dataset_to_panda_dataframe             Convert the dataset received from the SpotifyAPI into a panda dataframe.
extract_track_URIs_by_parameter_and_value      Extracts the tracks data fitting the parameters and requested value & tolerance.
extract_tracks_URI_IDs                         Extacts the track URIs included in the tracks data list provided.
extract_stats_from_tracks                      Gives the mean (average) and standard deviation for each tracks parameters that can be converted to float number.
generate_boxplot_for_specific_stat             Display the boxplot for a specific parameter based on a panda dataframe.
==================                             =============================================
"""


def convert_dataset_to_panda_dataframe(tracks_data):
    tracks_dataframe = pd.DataFrame(tracks_data)
    return tracks_dataframe


def extract_track_by_parameter_and_value(tracks_data, parameter, value, tolerance):
    tracks_data = list(tracks_data)
    lower_spec = value - value*tolerance
    upper_spec = value + value*tolerance
    tracks_len = len(tracks_data)
    output_tracks = list()

    for i in range(tracks_len):
        if lower_spec <= tracks_data[i][parameter] <= upper_spec:
            output_tracks.append(tracks_data[i])

    return output_tracks


def extract_tracks_URI_IDs(tracks_data):
    output_URI_IDs = list()
    for track in tracks_data:
        output_URI_IDs.append(track['uri'])

    return output_URI_IDs


def extract_stats_from_tracks(tracks_data):
    tracks_data = tracks_data
    for i in range(len(tracks_data)):
        tracks_data[i] = convert_values_to_float(tracks_data[i])

    mean_dict_value = mean_dict(tracks_data)
    std_dict_value = std_dict(tracks_data)

    return mean_dict_value, std_dict_value


def generate_histogram_for_stat(tracks_dataframe, parameter):
    if str(parameter) in tracks_dataframe.columns:

        # the histogram of the data
        plt.hist(tracks_dataframe[str(parameter)], facecolor='blue')

        # add a 'best fit' line

        plt.xlabel(parameter)
        plt.ylabel('Number of occurence')
        plt.title('Histogram for ' + str(parameter) + ' parameter')
        plt.grid(True)

        plt.show()
    else:
        print("Paramter" f"{str(parameter)}" "does not exist in the dataframe")

def generate_boxplot_for_specific_stat(tracks_dataframe, parameter):

    if str(parameter) in tracks_dataframe.columns:
        plt.boxplot(tracks_dataframe[str(parameter)])
        plt.xlabel('Unit from 0 to 1 (0: no ' + parameter + ' )')
        plt.ylabel(parameter)
        plt.title('Box plot for' + str(parameter) + ' parameter')
        plt.show()
    else:
        print("Paramter" f"{str(parameter)}" "does not exist in the dataframe")


def extract_parameter_list(tracks_data):
    parameter_list = list()

    for key in tracks_data[0].keys():
        if is_float(tracks_data[0][key]):
            parameter_list.append(key)

    return parameter_list


def std_dict(dict_list):
    std_dict_value = {}
    for key in dict_list[0].keys():
        if is_float(dict_list[0][key]):
            std_dict_value[key] = statistics.stdev(d[key] for d in dict_list)
        else:
            std_dict_value[key] = None
    return std_dict_value


def mean_dict(dict_list):
    mean_dict_values = {}
    for key in dict_list[0].keys():
        if is_float(dict_list[0][key]):
            mean_dict_values[key] = sum(d[key] for d in dict_list) / len(dict_list)
        else:
            mean_dict_values[key] = None
    return mean_dict_values


def is_float(to_test):
    try:
        float(to_test)
        return True
    except ValueError:
        return False


def convert_values_to_float(dict_data):
    for key, value in dict_data.items():
        try:
            dict_data[key] = float(value)
        except ValueError:
            continue
    return dict_data