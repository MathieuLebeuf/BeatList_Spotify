import base64
import datetime
import requests
import urllib.parse
import json


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
    redirect_uri = 'https://github.com/'
    auth_url = 'https://accounts.spotify.com/authorize'
    token_url = 'https://accounts.spotify.com/api/token'

    # Constructor.
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    # Methods.
    def get_client_cred_b64(self):  # API request to have client creds in a base64 encoded format.
        client_id = self.client_id
        client_secret = self.client_secret

        if client_id is None or client_secret is None:
            raise Exception("Need client id and client secret")
        client_cred = f'{client_id}:{client_secret}'
        client_cred_b64 = base64.b64encode(client_cred.encode())
        return client_cred_b64.decode()

    def get_redirect_uri_encoded(self):
        redirect_uri = self.redirect_uri
        return urllib.parse.quote(redirect_uri)

    def get_token_headers(self):
        client_creds_b64 = self.get_client_cred_b64()  # <base64 encoded client_id:client_secret>
        return {
            'Authorization': f'basic {client_creds_b64}'
        }

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

    def get_request_auth_header(self):
        access_token = self.access_token
        headers = {
            'Authorization': 'Bearer ' f'{access_token}',
        }
        return headers

    def extract_access_token(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        response = requests.post(token_url, headers=token_headers, data=token_data)
        if response.status_code in range(200, 299):
            token_response_data = response.json()
            now = datetime.datetime.now()
            self.access_token = token_response_data['access_token']
            self.refresh_token = token_response_data['refresh_token']
            expires_in = token_response_data['expires_in']
            expires = now + datetime.timedelta(seconds=expires_in)
            print("\nToken expires in: " + expires)
            return [True, self.access_token, self.refresh_token]
        return None

    def extract_current_user_id(self):
        headers = self.get_request_auth_header()
        query = 'https://api.spotify.com/v1/me'

        response = requests.get(query, headers=headers)
        response_json = response.json()

        self.user_id = response_json['id']

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
        r = requests.get(full_auth_url)

        print("Go to the following url on the browser and enter the code from the returned url: ")  # The request auth is the string after the code= in the URL.
        print("---  " + full_auth_url + "  ---")
        self.auth_code = input("code: ")

    def refresh(self):
        token_url = self.token_url
        refresh_token_data = self.get_refresh_token_data()
        token_headers = self.get_token_headers()
        response = requests.post(token_url, headers=token_headers, data=refresh_token_data)
        if response.status_code in range(200, 299):
            token_response_data = response.json()
            now = datetime.datetime.now()
            self.access_token = token_response_data['access_token']
            expires_in = token_response_data['expires_in']
            self.expires = now + datetime.timedelta(seconds=expires_in)
            return self.access_token

    def extract_saved_tracks_IDs(self):
        query = 'https://api.spotify.com/v1/me/tracks'
        tracks_IDs_list = list()

        headers = self.get_request_auth_header()

        params = (
            ('limit', '50'),
        )

        response = requests.get(query, headers=headers, params=params)
        response_json = response.json()
        for j in response_json['items']:
            tracks_IDs_list.append(j['track']['id'])

        return tracks_IDs_list

    def extract_library_albums_IDs(self):
        query = 'https://api.spotify.com/v1/me/albums'
        album_IDs_list = list()

        headers = self.get_request_auth_header()

        params = (
            ('limit', '50'),
        )

        response = requests.get(query, headers=headers, params=params)
        response_json = response.json()
        album_items = response_json['items']

        for i in album_items:
            album_IDs_list.append(i['album']['id'])

        return album_IDs_list

    def extract_tracks_IDs_from_album(self, album_IDs_list):
        album_IDs_list = album_IDs_list
        tracks_IDs_list = list()

        headers = self.get_request_auth_header()

        params = (
            ('limit', '50'),
        )

        for i in album_IDs_list:
            response = requests.get('https://api.spotify.com/v1/albums/'f'{i}''/tracks', headers=headers, params=params)
            response_json = response.json()
            for j in response_json['items']:
                tracks_IDs_list.append(j['id'])

        return tracks_IDs_list

    def extract_tracks_data(self, track_IDs_list):
        track_IDs_list = track_IDs_list
        query = 'https://api.spotify.com/v1/audio-features/'
        tracks_data = list()

        headers = self.get_request_auth_header()

        for i in range(len(track_IDs_list)):
            response = requests.get(query + f'{track_IDs_list[i]}', headers=headers)
            response_json = response.json()
            tracks_data.append(response_json)

        return tracks_data

    def create_a_playlist(self, playlist_name):
        playlist_name = playlist_name
        access_token = self.access_token
        user_id = self.user_id

        query = 'https://api.spotify.com/v1/users/'f'{user_id}''/playlists'

        headers = {
            'Authorization': 'Bearer ' f'{access_token}',
            'Content-Type': 'application/json'
        }

        data = {
            'name': f'{playlist_name}',
            'public': False
        }
        request_body = json.dumps(data)

        response = requests.post(query, headers=headers, data=request_body)
        reponse_json = response.json()

        if response.status_code in range(200, 299):
            return reponse_json['id']
        else:
            return None

    def add_tracks_to_a_playlist(self, playlist_ID, track_URIs):
        track_URIs = track_URIs
        playlist_ID = playlist_ID
        access_token = self.access_token

        data = {
            'uris': track_URIs,
        }

        data_json = json.dumps(data)

        query = 'https://api.spotify.com/v1/playlists/'f'{playlist_ID}''/tracks'

        headers = {
            'Authorization': 'Bearer 'f'{access_token}',
            'Accept': 'application/json',
        }

        response = requests.post(query, data=data_json, headers=headers)

        if response.status_code in range(200, 299):
            return True
        else:
            return False
