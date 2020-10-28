"""
Statistic and graph generator for track dataset.

This module provides functions for calculating statistics for the track dataset received from the Spotify API.

"""

import statistics
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import style
from typing import List, Dict, Optional, Union, Any, Tuple
style.use('fivethirtyeight')


def convert_dataset_to_panda_dataframe(tracks_data: List[Dict[str, Union[float, str]]]) -> pd.DataFrame:
    """Convert dataset into panda dataframe.

    Parameters
    ----------
    tracks_data: list(dict(str))
        dataset that need to be converted into panda dataframe

    Returns
    -------
    tracks_dataframe
        dataset converted into pd.dataframe
    """

    tracks_dataframe = pd.DataFrame(tracks_data)
    return tracks_dataframe


def extract_track_by_parameter_and_value(tracks_data: List[Dict[str, Union[float, str]]], parameter: str, value: float, tolerance: float) \
        -> List[Dict[str, Union[float, str]]]:
    """Extract the tracks data fitting the parameter and requested value & tolerance.

    Parameters
    ----------
    tracks_data : list(dict(string))
        list dataset. Each item contain a track data in a dict format.

    parameter : str
        the track data parameter on which to apply the value±tolerance extraction

    value : float
        targeted extraction value

    tolerance : float
        targeted extraction tolerance (value ± tolerance)

    Returns
    -------
    output_tracks: list(dict(string))
        list dataset with only the items inside the value ± tolerance

    """
    tracks_data = list(tracks_data)
    lower_spec = value - value*tolerance
    upper_spec = value + value*tolerance
    output_tracks = list()

    for item in tracks_data:
        if lower_spec <= item[parameter] <= upper_spec:
            output_tracks.append(item)

    return output_tracks


def extract_tracks_URI_IDs(tracks_data: List[Dict[str, Union[float, str]]]) -> List[str]:
    output_URI_IDs = list()
    for track in tracks_data:
        output_URI_IDs.append(track['uri'])

    return output_URI_IDs


def extract_stats_from_tracks(tracks_data: List[Dict[str, Union[float, str]]]) \
        -> Tuple[Dict[Any, Union[Optional[float], Any]], Dict[Any, Union[Union[float, None], Any]]]:

    tracks_data = tracks_data
    tracks_data[:] = [convert_values_to_float(item) for item in tracks_data]
    mean_dict_value = mean_dict(tracks_data)
    std_dict_value = std_dict(tracks_data)

    return mean_dict_value, std_dict_value


def generate_histogram_for_stat(tracks_dataframe: pd.DataFrame, parameter: str):
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


def generate_boxplot_for_specific_stat(tracks_dataframe: pd.DataFrame, parameter: str):

    if str(parameter) in tracks_dataframe.columns:
        plt.boxplot(tracks_dataframe[str(parameter)])
        plt.xlabel('Unit from 0 to 1 (0: no ' + parameter + ' )')
        plt.ylabel(parameter)
        plt.title('Box plot for' + str(parameter) + ' parameter')
        plt.show()
    else:
        print("Paramter" f"{str(parameter)}" "does not exist in the dataframe")


def extract_parameter_list(tracks_data: List[Dict[str, Union[float, str]]]) -> List[str]:
    parameter_list = list()

    for item in tracks_data[0].items():
        if isinstance(item[1], float):
            parameter_list.append(item[0])

    return parameter_list


def std_dict(dict_list: List[Dict[str, Union[float, str]]]) -> Dict[str, Union[float, None]]:
    std_dict_value = {}
    for key in dict_list[0].keys():
        if isinstance(dict_list[0][key], float):
            std_dict_value[key] = round(statistics.stdev(d[key] for d in dict_list), 2)
        else:
            std_dict_value[key] = None
    return std_dict_value


def mean_dict(dict_list: List[Dict[str, Union[float, str]]]) -> Dict[str, Union[float, None]]:
    mean_dict_values = {}
    for key in dict_list[0].keys():
        if isinstance(dict_list[0][key], float):
            mean_dict_values[key] = round(sum(d[key] for d in dict_list) / len(dict_list), 2)
        else:
            mean_dict_values[key] = None
    return mean_dict_values


def convert_values_to_float(dict_data: Dict[str, Union[float, str]]) -> Dict[str, Union[float, str]]:
    for key, value in dict_data.items():
        try:
            dict_data[key] = float(value)
        except ValueError:
            continue
    return dict_data