import io
import requests

VERSION_PREFIX = '/api/v1.2'
MAX_CHUNK_SIZE = 1024 * 1024 # 1 MB chunks.

class APIClient(object):
    def __init__(self, instance_configuration, access_token):
        self.instance_configuration = instance_configuration
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers = self._auth_headers()

    def _url_prefix(self):
        return 'https://{}{}'.format(self.instance_configuration.hostname,
                                     VERSION_PREFIX)

    def _auth_headers(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Endpoint-Consistency': 'strict',
            'Content-Type': 'application/json',
        }
        return headers

    # user object

    def get_user(self, email):
        url = '{}/users/{}'.format(self._url_prefix(), email)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def create_user(self, email, first_name, last_name):
        data = {'email': email, 'first_name': first_name,
                'last_name': last_name}

        url = '{}/users'.format(self._url_prefix())
        res = self.session.post(url, json=data)
        res.raise_for_status()
        return res.json()

    def update_user(self, email, first_name, last_name):
        data = {'email': email, 'first_name': first_name,
                'last_name': last_name}

        url = '{}/users/{}'.format(self._url_prefix(), email)
        res = self.session.put(url, json=data)
        res.raise_for_status()
        return res.json()

    def update_user_password(self, email, password):
        data = '"{}"'.format(password)

        url = '{}/users/{}/password'.format(self._url_prefix(), email)
        res = self.session.put(url, data=data)
        res.raise_for_status()
        return 'OK'

    def delete_user(self, email):
        url = '{}/users/{}'.format(self._url_prefix(), email)
        res = self.session.delete(url)
        res.raise_for_status()
        return 'OK'

    def delete_user_password(self, email):
        url = '{}/users/{}/password'.format(self._url_prefix(), email)
        res = self.session.delete(url)
        res.raise_for_status()
        return 'OK'

    # folder object

    def get_folder(self, uuid):
        url = '{}/folders/{}'.format(self._url_prefix(), uuid)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def get_folder_path(self, uuid):
        url = '{}/folders/{}/path'.format(self._url_prefix(), uuid)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def get_folder_children(self, uuid):
        url = '{}/folders/{}/children'.format(self._url_prefix(), uuid)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def create_folder(self, parent_folder, foldername):
        data = {'parent': parent_folder, 'name': foldername}

        url = '{}/folders'.format(self._url_prefix())
        res = self.session.post(url, json=data)
        res.raise_for_status()
        return res.json()

    def move_folder(self, uuid, parent_folder, foldername):
        data = {'parent': parent_folder, 'name': foldername}

        url = '{}/folders/{}'.format(self._url_prefix(), uuid)
        res = self.session.put(url, json=data)
        res.raise_for_status()
        return res.json()

    def delete_folder(self, uuid):
        url = '{}/folders/{}'.format(self._url_prefix(), uuid)
        res = self.session.delete(url)
        res.raise_for_status()
        return 'OK'

    # file object

    def get_file(self, uuid):
        url = '{}/files/{}'.format(self._url_prefix(), uuid)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def get_file_path(self, uuid):
        url = '{}/files/{}/path'.format(self._url_prefix(), uuid)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def get_file_content(self, uuid):
        url = '{}/files/{}/content'.format(self._url_prefix(), uuid)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def create_file(self, parent_folder, filename):
        data = {'parent': parent_folder, 'name': filename}

        url = '{}/files'.format(self._url_prefix())
        res = self.session.post(url, json=data)
        res.raise_for_status()
        return res.json()

    def upload_file_content(self, uuid, stream):
        url = '{}/files/{}/content'.format(self._url_prefix(), uuid)

        # Create upload identifier.
        initial_headers = {
            'Content-Range': 'bytes */*',
            'Content-Length': '0',
        }

        res = self.session.put(url, headers=initial_headers)
        res.raise_for_status()

        upload_id = res.headers['Upload-ID']
        etag = res.headers.get('ETag')
        current_chunk = stream.read(MAX_CHUNK_SIZE)
        total_bytes_sent = 0

        # Upload content, one chunk at a time.
        headers = None
        while len(current_chunk) != 0:
            headers = {
                'Upload-ID': upload_id,
                'Endpoint-Consistency': 'strict',
                'Content-Range': 'bytes {}-{}/*'.format(
                    total_bytes_sent,
                    total_bytes_sent + len(current_chunk) - 1),
            }

            if etag:
                headers['If-Match'] = etag

            res = self.session.put(url, headers=headers,
                                   data=io.BytesIO(current_chunk))
            res.raise_for_status()

            total_bytes_sent += len(current_chunk)
            current_chunk = stream.read(MAX_CHUNK_SIZE)

        # Commit upload.
        commit_headers = {
            'Upload-ID': upload_id,
            'Endpoint-Consistency': 'strict',
            'Content-Range': 'bytes */{}'.format(total_bytes_sent),
            'Content-Length': '0',
        }

        if etag:
            headers['If-Match'] = etag

        res = self.session.put(url, headers=commit_headers)
        res.raise_for_status()
        return 'OK'

    def move_file(self, uuid, parent_folder, filename):
        data = {'parent': parent_folder, 'name': filename}

        url = '{}/files/{}'.format(self._url_prefix(), uuid)
        res = self.session.put(url, json=data)
        res.raise_for_status()
        return res.json()

    def delete_file(self, uuid):
        url = '{}/files/{}'.format(self._url_prefix(), uuid)
        res = self.session.delete(url)
        res.raise_for_status()
        return 'OK'

    # shared folder object

    def list_invitations(self, email):
        url = '{}/users/{}/invitations'.format(self._url_prefix(), email)
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def accept_invitation(self, email, sid):
        url = '{}/users/{}/invitations/{}'.format(self._url_prefix(), email,
                                                  sid)
        res = self.session.post(url)
        res.raise_for_status()
        return res.json()
