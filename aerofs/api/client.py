import io
import requests
import urllib

VERSION_PREFIX = '/api/v1.2'
MAX_CHUNK_SIZE = 1024 * 1024 # 1 MB chunks.

class APIClient(object):
    def __init__(self, instance_configuration, access_token):
        self.instance_configuration = instance_configuration
        self.access_token = access_token

        self.auth_headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json',
            'Endpoint-Consistency': 'strict',
        }
        self.url_prefix = 'https://{}{}'.format(
            instance_configuration.hostname, VERSION_PREFIX)

        self.session = requests.Session()

        self.response_headers = None

    # requests

    def _handle_response(self, response):
        response.raise_for_status()
        self.response_headers = response.headers
        try:
            return response.json()
        except ValueError:
            return response.text or 'ok'

    def _do_delete(self, route, headers=None):
        if not headers:
            headers = self.auth_headers

        res = self.session.delete('{}{}'.format(self.url_prefix, route),
                                  headers=headers)
        return self._handle_response(res)

    def _do_get(self, route, headers=None):
        if not headers:
            headers = self.auth_headers

        res = self.session.get('{}{}'.format(self.url_prefix, route),
                               headers=headers)
        return self._handle_response(res)

    def _do_post(self, route, data, headers=None):
        if not headers:
            headers = self.auth_headers

        res = self.session.post('{}{}'.format(self.url_prefix, route),
                                json=data, headers=headers)
        return self._handle_response(res)

    def _do_put(self, route, data, serialize=True, headers=None):
        if not headers:
            headers = self.auth_headers

        url = '{}{}'.format(self.url_prefix, route)
        if serialize and data:
            res = self.session.put(url, json=data, headers=headers)
        else:
            del headers['Content-Type']
            res = self.session.put(url, data=data, headers=headers)
        return self._handle_response(res)

    # user object

    def get_user(self, email):
        route = '/users/{}'.format(email)
        return self._do_get(route)

    def create_user(self, email, first_name, last_name):
        route = '/users'
        data = {'email': email, 'first_name': first_name,
                'last_name': last_name}
        return self._do_post(route, data)

    def update_user(self, email, first_name, last_name):
        route = '/users/{}'.format(email)
        data = {'email': email, 'first_name': first_name,
                'last_name': last_name}
        return self._do_put(route, data)

    def delete_user(self, email):
        route = '/users/{}'.format(email)
        return self._do_delete(route)

    def update_user_password(self, email, password):
        route = '/users/{}/password'.format(email)
        data = '"{}"'.format(password)
        return self._do_put(route, data)

    def delete_user_password(self, email):
        route = '/users/{}/password'.format(email)
        return self._do_delete(route)

    # folder object

    def get_folder(self, uuid, fields=None):
        route = '/folders/{}'.format(uuid)
        if fields:
            route += '?fields={}'.format(','.join(fields))
        return self._do_get(route)

    def get_folder_path(self, uuid):
        route = '/folders/{}/path'.format(uuid)
        return self._do_get(route)

    def get_folder_children(self, uuid):
        route = '/folders/{}/children'.format(uuid)
        return self._do_get(route)

    def create_folder(self, parent_folder, foldername):
        route = '/folders'
        data = {'parent': parent_folder, 'name': foldername}
        return self._do_post(route, data)

    def move_folder(self, uuid, parent_folder, foldername, ifmatch=None):
        headers = self.auth_headers
        if ifmatch:
            headers['If-Match'] = ifmatch

        route = '/folders/{}'.format(uuid)
        data = {'parent': parent_folder, 'name': foldername}
        return self._do_put(route, data, headers=headers)

    def delete_folder(self, uuid, ifmatch=None):
        headers = self.auth_headers
        if ifmatch:
            headers['If-Match'] = ifmatch

        route = '/folders/{}'.format(uuid)
        return self._do_delete(route, headers=headers)

    # file object

    def get_file(self, uuid, fields=None):
        route = '/files/{}'.format(uuid)
        if fields:
            route += '?fields={}'.format(','.join(fields))
        return self._do_get(route)

    def get_file_path(self, uuid):
        route = '/files/{}/path'.format(uuid)
        return self._do_get(route)

    def get_file_content(self, uuid, ranges=None, ifrange=None,
                         ifnonematch=None):
        headers = self.auth_headers
        if ranges:
            headers['Range'] = ','.join(ranges)
        if ifrange:
            headers['If-Range'] = ifrange
        if ifnonematch:
            headers['If-None-Match'] = ','.join(ifnonematch)

        route = '/files/{}/content'.format(uuid)
        return self._do_get(route, headers=headers)

    def create_file(self, parent_folder, filename):
        route = '/files'
        data = {'parent': parent_folder, 'name': filename}
        return self._do_post(route, data)

    def upload_file_content(self, uuid, stream, ifmatch=None):
        route = '/files/{}/content'.format(uuid)

        # Create upload identifier.
        headers = dict(self.auth_headers, **{
            'Content-Range': 'bytes */*',
            'Content-Length': '0',
        })
        if ifmatch:
            headers['If-Match'] = ','.join(ifmatch)

        self._do_put(route, None, headers=headers)
        upload_id = self.response_headers['Upload-ID']
        etag = self.response_headers.get('ETag')

        # Upload content, one chunk at a time.
        current_chunk = stream.read(MAX_CHUNK_SIZE)
        total_bytes_sent = 0
        while len(current_chunk) != 0:
            headers = dict(self.auth_headers, **{
                'Upload-ID': upload_id,
                'Content-Range': 'bytes {}-{}/*'.format(
                    total_bytes_sent,
                    total_bytes_sent + len(current_chunk) - 1),
            })
            if etag:
                headers['If-Match'] = etag

            self._do_put(route, io.BytesIO(current_chunk), serialize=False,
                         headers=headers)

            total_bytes_sent += len(current_chunk)
            current_chunk = stream.read(MAX_CHUNK_SIZE)

        # Commit upload.
        headers = dict(self.auth_headers, **{
            'Upload-ID': upload_id,
            'Content-Range': 'bytes */{}'.format(total_bytes_sent),
            'Content-Length': '0',
        })
        if etag:
            headers['If-Match'] = etag

        return self._do_put(route, None, headers=headers)

    def move_file(self, uuid, parent_folder, filename, ifmatch=None):
        headers = self.auth_headers
        if ifmatch:
            headers['If-Match'] = ','.join(ifmatch)

        route = '/files/{}'.format(uuid)
        data = {'parent': parent_folder, 'name': filename}
        return self._do_put(route, data, headers=headers)

    def delete_file(self, uuid, ifmatch=None):
        headers = self.auth_headers
        if ifmatch:
            headers['If-Match'] = ','.join(ifmatch)

        route = '/files/{}'.format(uuid)
        return self._do_delete(route, headers=headers)

    # shared folder object

    def get_shared_folders(self, email, ifnonematch=None):
        headers = self.auth_headers
        if ifnonematch:
            headers['If-None-Match'] = ','.join(ifnonematch)

        route = '/users/{}/shares'.format(email)
        return self._do_get(route, headers=headers)

    def get_shared_folder_metadata(self, uuid, ifnonematch=None):
        headers = self.auth_headers
        if ifnonematch:
            headers['If-None-Match'] = ','.join(ifnonematch)

        route = '/shares/{}'.format(uuid)
        return self._do_get(route, headers=headers)

    def create_shared_folder(self, foldername):
        route = '/shares'
        data = {'name': foldername}
        return self._do_post(route, data)

    # member object

    def get_members(self, uuid, ifnonematch=None):
        headers = self.auth_headers
        if ifnonematch:
            headers['If-None-Match'] = ','.join(ifnonematch)

        route = '/shares/{}/members'.format(uuid)
        return self._do_get(route, headers=headers)

    def get_member(self, uuid, email, ifnonematch=None):
        headers = self.auth_headers
        if ifnonematch:
            headers['If-None-Match'] = ','.join(ifnonematch)

        route = '/shares/{}/members/{}'.format(uuid, email)
        return self._do_get(route, headers=headers)

    def add_member(self, uuid, email, permissions):
        route = '/shares/{}/members'.format(uuid)
        data = {'email': email, 'permissions': permissions}
        return self._do_post(route, data)

    def update_member_permissions(self, uuid, email, permissions,
                                  ifmatch=None):
        headers = self.auth_headers
        if ifmatch:
            headers['If-Match'] = ','.join(ifmatch)

        route = '/shares/{}/members/{}'.format(uuid, email)
        data = {'permissions': permissions}
        return self._do_put(route, data, headers=headers)

    def remove_member(self, uuid, email, ifmatch=None):
        headers = self.auth_headers
        if ifmatch:
            headers['If-Match'] = ','.join(ifmatch)

        route = '/shares/{}/members/{}'.format(uuid, email)
        return self._do_delete(route, headers=headers)

    # pending member object

    def get_pending_members(self, uuid, ifnonematch=None):
        headers = self.auth_headers
        if ifnonematch:
            headers['If-None-Match'] = ','.join(ifnonematch)

        route = '/shares/{}/pending'.format(uuid)
        return self._do_get(route, headers=headers)

    def get_pending_member(self, uuid, email):
        route = '/shares/{}/pending/{}'.format(uuid, email)
        return self._do_get(route)

    def add_pending_member(self, uuid, email, permissions, note):
        route = '/shares/{}/pending'.format(uuid)
        data = {'email': email, 'permissions': permissions, 'note': note}
        return self._do_post(route, data)

    def remove_pending_member(self, uuid, email):
        route = '/shares/{}/pending/{}'.format(uuid, email)
        return self._do_delete(route)

    # invitation object

    def get_invitations(self, email):
        route = '/users/{}/invitations'.format(urllib.quote_plus(email))
        return self._do_get(route)

    def get_invitation(self, email, uuid):
        route = '/users/{}/invitations/{}'.format(urllib.quote_plus(email),
                                                  uuid)
        return self._do_get(route)

    def accept_invitation(self, email, uuid, external=False):
        route = '/users/{}/invitations/{}'.format(urllib.quote_plus(email),
                                                  uuid)
        if external:
            route += '?external=1'
        return self._do_post(route, dict())

    def ignore_invitation(self, email, uuid):
        route = '/users/{}/invitations/{}'.format(urllib.quote_plus(email),
                                                  uuid)
        return self._do_delete(route)
