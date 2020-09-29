

class SongAnalyser(object):

    # Variables.
    tracks_data = None

    # Constructor.
    def __init__(self, tracks_data):
        self.tracks_data = tracks_data

    # Methods.
    def extract_track_URIs_by_parameter(self, parameter, value, tolerance):
        track_data = self.tracks_data
        output_URI_IDs = list()
        parameter = parameter
        value = value
        tolerance = tolerance
        lower_spec = value - value*tolerance
        upper_spec = value + value*tolerance
        for track in track_data:
            if lower_spec <= track[parameter] <= upper_spec:
                output_URI_IDs.append(track['uri'])
        return output_URI_IDs
