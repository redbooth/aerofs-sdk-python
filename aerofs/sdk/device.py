from .interface import APIObject
from .interface import readonly
from .interface import synced


@readonly('online', sync=False)
@readonly('last_seen', sync=False)
class DeviceStatus(object):
    def __init__(self):
        self._online = None
        self._last_seen = None

    def from_json(self, json):
        self._online = json['online']
        self._last_seen = json['last_seen']


@readonly('id', sync=False)
@synced('name')
@readonly('owner')
@readonly('os_family')
@readonly('install_date')
@readonly('status')
class Device(APIObject):
    def __init__(self, api, did=None):
        super(Device, self).__init__(api)

        self._id = did
        self._name = None
        self._owner = None
        self._os_family = None
        self._install_date = None
        self._status = None

    def from_json(self, json):
        self._id = json['id']
        self._name = json['name']
        from .user import User
        self._owner = User(self.api, json['owner'])
        self._os_family = json['os_family']
        self._install_date = json['install_date']
        return self

    def load(self):
        data = self.api.get_device(self.id)
        self.from_json(data)

    def load_status(self):
        data = self.api.get_device_status(self.id)
        self._status = DeviceStatus.from_json(data)

    def save_name(self):
        self.api.update_device(self.id, self._name)
