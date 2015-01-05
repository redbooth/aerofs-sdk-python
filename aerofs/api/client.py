import requests

VERSION_PREFIX = "/api/v1.2"

class APIClient(object):
    def __init__(self, instance_configuration, access_token):
        self.instance_configuration = instance_configuration
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers = self.auth_headers()

    def auth_headers(self):
        headers = {"Authorization": "Bearer {}".format(self.access_token),
                   "Endpoint-Consistency": "strict"}
        return headers

    # TODO allow other interesting interactions wiht the API backend.

    def get_user_info(self, email):
        url = "https://{}{}/users/{}".format(
            self.instance_configuration.hostname,
            VERSION_PREFIX,
            email)
        print url
        res = self.session.get(url)
        res.raise_for_status()
        return res.json()

    def create_folder(self, parent_folder, foldername):
        url = "https://{}{}/folders".format(self.instance_configuration.hostname, VERSION_PREFIX)
        data = {"parent": parent_folder, "name": foldername}
        res = self.session.post(url, json=data)
        res.raise_for_status()
        return res.json()

    def create_file(self, parent_folder, filename):
        url = "https://{}{}/files".format( self.instance_configuration.hostname, VERSION_PREFIX)
        data = {"parent": parent_folder, "name": filename}
        print data
        res = self.session.post(url, json=data)
        res.raise_for_status()
        return res.json()

    def set_file_contents(self, oid, stream):
        url = "https://{}{}/files/{}/content".format(self.instance_configuration.hostname,
                                                     VERSION_PREFIX, oid)
        res = self.session.put(url, data=stream)
        res.raise_for_status()
        # Not res.json() because this PUT replies with no content
        return res