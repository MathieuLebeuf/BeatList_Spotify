import pathlib
import sqlite3


class DataManager(object):

    # Variables.
    directory_path = None
    directory_name = None
    file_path = None
    conn = None
    c = None

    # Constructor.
    def __init__(self):
        self.directory_name = 'InitFiles'
        self.directory_path = pathlib.Path.cwd() / self.directory_name
        self.file_path = self.directory_path / 'credentials.txt'

        self.directory_path.mkdir(parents=True, exist_ok=True)  # Create path and file for credentials saving.

        if not self.file_path.is_file():
            self.create_credentials_file()

        self.connect_to_database()  # Connect to SQL database and create it if necessary.
        self.close_database()

    # Methods.
    def connect_to_database(self):
        self.conn = sqlite3.connect('data.db')
        self.c = self.conn.cursor()

    def close_database(self):
        self.c.close()
        self.conn.close()

    def extract_all_table_name(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")

        data = self.c.fetchall()
        col = 0
        column = [element[col] for element in data]
        return column

    def create_tracks_data_table(self, table):
        sql_query = 'CREATE TABLE IF NOT EXISTS ' + table + ' (danceability REAL, energy REAL, key REAL, loudness REAL, mode REAL, speechiness REAL, ' \
                                                            'acousticness REAL, instrumentalness REAL, liveness REAL, valence REAL, tempo REAL, type TEXT, ' \
                                                            'id TEXT, uri TEXT, track_href TEXT, analysis_url TEXT, duration_ms REAL, time_signature REAL)'

        self.c.execute(sql_query)

    def read_all_tracks_data_table(self, table):
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self.c.execute('SELECT * FROM ' + table)
        data = self.c.fetchall()
        data = [dict(row) for row in data]
        return data

    def read_specific_tracks_data_table(self, param, value, tolerance):
        param = param
        value = value
        lower_value = value - value * tolerance
        upper_value = value + value * tolerance
        sql_select = 'SELECT * FROM songData WHERE ' + param + ' >= ' + str(lower_value) + ' AND ' + param + ' <= ' + str(upper_value)
        self.c.execute(sql_select)

        data = self.c.fetchall()
        return data

    def write_tracks_data_to_table(self, table, data):
        self.create_tracks_data_table(table)
        for item in data:
            self.c.execute(
                'INSERT INTO ' + table + ' (danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo,'
                ' type, id, uri, track_href, analysis_url, duration_ms, time_signature) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (item['danceability'], item['energy'], item['key'], item['loudness'], item['mode'], item['speechiness'], item['acousticness'],
                 item['instrumentalness'], item['liveness'], item['valence'], item['tempo'], item['type'], item['id'], item['uri'], item['track_href'],
                 item['analysis_url'], item['duration_ms'], item['time_signature'])
            )
            self.conn.commit()

    def clear_all_data_from_table(self, table):
        self.create_tracks_data_table(table)
        sql = 'DELETE FROM ' + table
        self.c.execute(sql)
        self.conn.commit()

    def is_table_exist(self, table):
        self.c.execute(f''' SELECT count(*) FROM sqlite_master WHERE type='table' AND name=' f'{table}' ''')

        # if the count is 1, then table exists
        if self.c.fetchone()[0] == 1:
            return True
        else:
            return False

    def create_credentials_file(self):  # Create the creds file with defaults values.
        file_object = open(self.file_path, mode='w')
        file_object.writelines('CLIENT_ID_ACQUIRED\n')
        file_object.writelines('CLIENT_ID\n')
        file_object.writelines('CLIENT_SECRET\n')
        file_object.writelines('AUTH_GRANT\n')
        file_object.writelines('ACCESS_TOKEN\n')
        file_object.writelines('REFRESH_TOKEN\n')
        file_object.close()

    def save_line_info(self, line_data, line_number):  # Save info in one particuliar line in the creds file.
        file_path = self.file_path

        if file_path.is_file():
            with open(file_path, 'r') as f:
                try:
                    fline = f.readlines()
                    fline[line_number] = line_data + "\n"
                    f.close()
                except IndexError:
                    print("No data found")
            with open(file_path, 'w') as f:
                try:
                    for line in fline:
                        f.write(line)
                    f.close()
                    return True
                except IndexError:
                    print("No data found")
            return False
        else:
            return False

    def extract_line_info(self, line_number):  # Extract one particuliar line in the creds files.
        file_path = self.file_path

        if file_path.is_file():
            with open(file_path, 'r') as f:
                try:
                    return f.readlines()[line_number].rstrip()
                except IndexError:
                    print("No data found")
            return False
        else:
            return "file don't exist"

    def save_authentification_to_file(self, authentification):
        self.save_line_info(authentification, 3)

    def save_tokens_to_file(self, access_token, refresh_token):
        self.save_line_info(access_token, 4)
        self.save_line_info(refresh_token, 5)

    def save_client_info_to_file(self, client_id, client_secret):
        self.save_line_info(client_id, 1)
        self.save_line_info(client_secret, 2)

    def extract_token_from_file(self):
        access_token = self.extract_line_info(4)
        refresh_token = self.extract_line_info(5)
        return [access_token, refresh_token]

    def extract_client_info_from_file(self):
        client_id = self.extract_line_info(1)
        client_secret = self.extract_line_info(2)
        return [client_id, client_secret]

    def is_client_info_exist(self):
        if self.extract_line_info(0) == '1':
            return True
        else:
            return False

    def is_auth_granted(self):
        if self.extract_line_info(3) == '1':
            return True
        else:
            return False