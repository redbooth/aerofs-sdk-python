from .interface import APIObject
from .interface import readonly


@readonly('id', sync=False)
@readonly('name')
@readonly('members')
class Group(APIObject):
    def __init__(self, api, gid=None):
        super(Group, self).__init__(api)

        self._id = gid
        self._name = None
        self._members = None

    def from_json(self, json):
        self._id = json['id']
        self._name = json['name']
        from .group_member import GroupMember
        self._members = set([GroupMember(self.api, self.id).from_json(f)
                             for f in json['members']])
        return self

    def load(self):
        data = self.api.get_group(self.id)
        self.from_json(data)

    def create(self, name):
        data = self.api.create_group(name)
        self.from_json(data)

    def delete(self):
        self.api.delete_group(self.id)
