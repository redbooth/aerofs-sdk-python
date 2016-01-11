from .interface import APIObject
from .interface import readonly
from .interface import synced


@readonly('shared_folder', sync=False)
@readonly('email', sync=False)
@readonly('first_name')
@readonly('last_name')
@synced('permissions')
@readonly('etags', sync=False)
class SFMember(APIObject):
    def __init__(self, api, sid, email=None):
        super(SFMember, self).__init__(api)

        from .shared_folder import SharedFolder
        self._shared_folder = SharedFolder(self.api, sid)

        self._email = email
        self._first_name = None
        self._last_name = None
        self._permissions = None

        self._etags = None

    def from_json(self, json):
        self._email = json['email']
        self._first_name = json['first_name']
        self._last_name = json['last_name']
        self._permissions = json['permissions']
        return self

    def load(self):
        data = self.api.get_sf_member(self.shared_folder.id, self.email)
        self.from_json(data)

        self._etags = [self.api.response_headers['ETag']]

    def save_permissions(self, matching=False):
        if not matching:
            self._etags = None

        self.api.update_sf_member(self.shared_folder.id, self.email,
                                  self._permissions, ifmatch=self._etags)

        self._etags = [self.api.response_headers['ETag']]

    def create(self, email, permissions):
        data = self.api.add_sf_member(self.shared_folder.id, email,
                                      permissions)
        self.from_json(data)

    def delete(self, matching=False):
        if not matching:
            self._etags = None

        self.api.remove_sf_member(self.shared_folder.id, self.email,
                                  ifmatch=self._etags)

        self._etags = [self.api.response_headers['ETag']]
