from .interface import APIObject
from .interface import readonly


@readonly('id', sync=False)
@readonly('name')
@readonly('is_external')
@readonly('members')
@readonly('groups')
@readonly('pending')
@readonly('caller_permissions')
class SharedFolder(APIObject):
    def __init__(self, api, sid=None):
        super(SharedFolder, self).__init__(api)

        self._id = sid
        self._name = None
        self._is_external = None
        self._members = None
        self._groups = None
        self._pending = None
        self._caller_permissions = None

    def from_json(self, json):
        self._id = json['id']
        self._name = json['name']
        self._is_external = json['is_external']
        from .shared_folder_member import SFMember
        self._members = frozenset(
            [SFMember(self.api, self.id).from_json(f)
             for f in json['members']])
        from .shared_folder_group_member import SFGroupMember
        self._groups = frozenset(
            [SFGroupMember(self.api, self.id).from_json(f)
             for f in json['groups']])
        from .shared_folder_pending_member import SFPendingMember
        self._pending = frozenset(
            [SFPendingMember(self.api, self.id).from_json(f)
             for f in json['pending']])
        self._caller_permissions = json['caller_effective_permissions']
        return self

    def load(self):
        data = self.api.get_shared_folder(self.id)
        self.from_json(data)

    def create(self, name):
        data = self.api.create_shared_folder(name)
        self.from_json(data)
