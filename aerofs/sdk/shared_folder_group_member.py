from .interface import APIObject
from .interface import readonly
from .interface import synced


@readonly('shared_folder', sync=False)
@readonly('id', sync=False)
@readonly('name')
@synced('permissions')
class SFGroupMember(APIObject):
    def __init__(self, api, sid, gid=None):
        super(SFGroupMember, self).__init__(api)

        from .shared_folder import SharedFolder
        self._shared_folder = SharedFolder(self.api, sid)

        self._id = gid
        self._name = None
        self._permissions = None

    def from_json(self, json):
        self._id = json['id']
        self._name = json['name']
        self._permissions = json['permissions']
        return self

    def load(self):
        data = self.api.get_sf_group_member(self.shared_folder.id, self.id)
        self.from_json(data)

    def save_permissions(self):
        self.api.update_sf_group_member(self.shared_folder.id, self.id,
                                        self._permissions)

    def create(self, gid, permissions):
        data = self.api.add_sf_group_member(self.shared_folder.id, gid,
                                            permissions)
        self.from_json(data)

    def delete(self):
        self.api.remove_sf_group_member(self.shared_folder.id, self.id)
