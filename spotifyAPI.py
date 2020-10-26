"""
Module for Spotify API GET and POST request.

This module handle all the GET and POST request associated with the Spotify API.
- It will fletch all the client information, access token, tracks URI, tracks data, etc.
- It will request the creation of playlist and the request to add tracks to a playlist.

"""

import base64
import datetime
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse

"""
class BearerAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['authorization'] = 'Bearer ' + self.token
        return r
"""

class BasicAuth(requests.auth.AuthBase):

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def __call__(self, r):
        r.headers['Authorization'] = 'basic ' + self.get_client_cred_b64()
        return r

    def get_client_cred_b64(self):  # API request to have client creds in a base64 encoded format.
        client_id = self.client_id
        client_secret = self.client_secret

        if client_id is None or client_secret is None:
            raise Exception("Need client id and client secret")
        client_cred = f'{client_id}:{client_secret}'
        client_cred_b64 = base64.b64encode(client_cred.encode())
        return client_cred_b64.decode()


class SpotifyAPI(object):

    # Variables.
    access_token = None
    refresh_token = None
    access_token_expires = datetime.datetime.now()
    client_id = None
    user_id = None
    client_secret = None
    auth_code = None
    expires = datetime.datetime.now()
    now = datetime.datetime.now()
    redirect_uri = 'https://github.com/'
    auth_url = 'https://accounts.spotify.com/authorize'
    token_url = 'https://accounts.spotify.com/api/token'
    api_url = 'https://api.spotify.com/v1'
    bearer_auth = None
    basic_auth = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.basic_auth = BasicAuth(self.client_id, self.client_secret)

    # Methods.

    def get_redirect_uri_encoded(self):
        redirect_uri = self.redirect_uri
        return urllib.parse.quote(redirect_uri)

    def get_token_data(self):
        grant_type = 'authorization_code'
        code = self.auth_code
        redirect_uri = self.redirect_uri
        token_data = {
            'grant_type': grant_type,
            'code': code,
            'redirect_uri': redirect_uri
        }
        return token_data

    def get_refresh_token_data(self):
        grant_type = 'refresh_token'
        refresh_token = self.refresh_token
        token_data = {
            'grant_type': grant_type,
            'refresh_token': refresh_token,
        }
        return token_data

    def get_GET_session(self):
        sess = requests.Session()
        sess.headers['Authorization'] = 'Bearer ' f'{self.access_token}'

        return sess

    def get_POST_session(self):

        sess = requests.Session()
        sess.headers['Authorization'] = 'Bearer ' f'{self.access_token}'
        sess.headers['Content-Type'] = 'application/json'

        return sess

    def extract_access_token(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        response = requests.post(token_url, auth=self.basic_auth, data=token_data)

        if response.status_code in range(200, 299):
            token_response_data = response.json()
            self.now = datetime.datetime.now()
            self.access_token = token_response_data['access_token']
            self.refresh_token = token_response_data['refresh_token']
            expires_in = token_response_data['expires_in']
            self.expires = self.now + datetime.timedelta(seconds=expires_in)
            print("\nToken expires at: " + self.expires.strftime("%H:%M:%S"))
            return [True, self.access_token, self.refresh_token]
        return [False, None, None]

    def extract_current_user_id(self):
        query = self.api_url + '/me'

        sess = self.get_GET_session()

        response = sess.get(query)
        response_json = response.json()

        self.user_id = response_json['id']

        return self.user_id

    def get_user_id(self):
        return self.user_id

    def get_access_token(self):
        return self.access_token

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_refresh_token(self):
        return self.refresh_token

    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token

    def get_expires(self):
        return self.expires

    def request_auth(self):
        client_id = self.client_id
        auth_url = self.auth_url
        redirect_uri_encoded = self.get_redirect_uri_encoded()
        full_auth_url = f'{auth_url}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri_encoded}&' \
                        f'scope=playlist-modify-public%20playlist-modify-private%20user-library-read%20playlist-read-private'

        print("Go to the following url on the browser and enter the code from the returned url: ")  # The request auth is the string after the code= in the URL.
        print("---  " + full_auth_url + "  ---")
        self.auth_code = input("code: ")

    def refresh(self):
        token_url = self.token_url
        refresh_token_data = self.get_refresh_token_data()
        response = requests.post(token_url, auth=self.basic_auth, data=refresh_token_data)
        if response.status_code in range(200, 299):
            token_response_data = response.json()
            self.now = datetime.datetime.now()
            self.access_token = token_response_data['access_token']
            expires_in = token_response_data['expires_in']
            self.expires = self.now + datetime.timedelta(seconds=expires_in)
            print("\nToken expires at: " + self.expires.strftime("%H:%M:%S"))
            return self.access_token
        else:
            return None

    def is_expire(self):
        now = self.now
        expires = self.expires
        return now > expires

    def extract_tracks_IDs_from_playlist(self, playlist_ID):

        tracks_IDs_list = list()
        playlist_ID = playlist_ID

        query = self.api_url + '/playlists/'f'{playlist_ID}''/tracks'

        sess = self.get_GET_session()

        offset = '0'

        params = {
            'limit': '100',
            'offset': offset,
        }

        response = sess.get(query, params=params)
        response_json = response.json()
        for j in response_json['items']:
            tracks_IDs_list.append(j['track']['id'])

        return tracks_IDs_list

    def extract_saved_tracks_IDs(self):
        query = self.api_url + '/me/tracks'
        tracks_IDs_list = list()

        sess = self.get_GET_session()

        params = {
            'limit': '50',
            'offset': '50',
        }

        response = sess.get(query, params=params)
        response_json = response.json()
        for j in response_json['items']:
            tracks_IDs_list.append(j['track']['id'])

        return tracks_IDs_list

    def extract_library_albums_IDs(self, offset=0):
        query = self.api_url + '/me/albums'
        album_IDs_list = list()

        sess = self.get_GET_session()

        params = {
            'limit': '50',
            'offset': offset,
        }

        response = sess.get(query, params=params)
        response_json = response.json()
        album_items = response_json['items']

        for i in album_items:
            album_IDs_list.append(i['album']['id'])

        return album_IDs_list

    def extract_tracks_IDs_from_album(self, album_IDs_list):
        album_IDs_list = album_IDs_list
        tracks_IDs_list = list()

        sess = self.get_GET_session()

        params = {
                    'limit': '50',
                }

        for i in album_IDs_list:
            response = sess.get(self.api_url + '/albums/'f'{i}''/tracks', params=params)
            response_json = response.json()
            for j in response_json['items']:
                tracks_IDs_list.append(j['id'])

        return tracks_IDs_list

    def extract_tracks_data(self, track_IDs_list):
        track_IDs_list = track_IDs_list
        query = self.api_url + '/audio-features/'
        tracks_data = list()

        sess = self.get_GET_session()

        for item in track_IDs_list:
            response = sess.get(query + f'{item}')
            response_json = response.json()
            tracks_data.append(response_json)

        return tracks_data

    def extract_list_of_user_playlist(self):
        user_id = self.user_id
        playlist_info = list()

        query = 'https://api.spotify.com/v1/users/'f'{user_id}''/playlists'

        sess = self.get_GET_session()

        response = sess.get(query)
        reponse_json = response.json()

        if response.status_code in range(200, 299):
            for item in reponse_json['items']:
                playlist_info.append([item['name'], item['id']])
            return playlist_info
        else:
            return None

    def create_a_playlist(self, playlist_name):
        playlist_name = playlist_name
        user_id = self.user_id

        query = self.api_url + '/users/'f'{user_id}''/playlists'

        data = {
            'name': f'{playlist_name}',
            'public': False
        }

        sess = self.get_POST_session()

        try:
            response = sess.post(query, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        reponse_json = response.json()
        return reponse_json['id']

    def add_tracks_to_a_playlist(self, playlist_ID, track_URIs):
        track_URIs = track_URIs
        playlist_ID = playlist_ID

        query = self.api_url + '/playlists/'f'{playlist_ID}''/tracks'

        data = {
            'uris': track_URIs,
        }

        sess = self.get_POST_session()

        try:
            response = sess.post(query, json=data)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            return False

    def is_user_playlist_name_exist(self, playlist_name):
        playlist_info = self.extract_list_of_user_playlist()

        for item in playlist_info:
            if item[0] == playlist_name:
                return True

        return False

    def is_user_playlist_ID_exist(self, playlist_ID):
        playlist_info = self.extract_list_of_user_playlist()

        for item in playlist_info:
            if item[1] == playlist_ID:
                return True

            return False

    def get_playlist_ID(self, playlist_name):
        playlist_info = self.extract_list_of_user_playlist()

        for item in playlist_info:
            if item[0] == playlist_name:
                return item[1]

        return "No_ID"