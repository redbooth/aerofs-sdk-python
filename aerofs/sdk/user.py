from .error import NoRouteException
from .interface import APIObject
from .interface import readonly
from .interface import synced
from .interface import writeonly


@readonly('email', sync=False)
@synced('first_name')
@synced('last_name')
@readonly('shares')
@readonly('invitations')
@writeonly('password')
@synced('two_factor')
@readonly('devices')
class User(APIObject):
    def __init__(self, api, email):
        super(User, self).__init__(api)

        self._email = email
        self._first_name = None
        self._last_name = None
        self._shares = None
        self._invitations = None
        self._password = None
        self._two_factor = None
        self._devices = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.email == other.email
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.email != other.email
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def from_json(self, json):
        self._first_name = json['first_name']
        self._last_name = json['last_name']
        if 'shares' in json:  # requires extra scopes
            from .shared_folder import SharedFolder
            self._shares = frozenset([SharedFolder(self.api).from_json(f)
                                      for f in json['shares']])
        if 'invitations' in json:  # requires extra scopes
            from .invitation import Invitation
            self._invitations = frozenset(
                [Invitation(self.api, self.email).from_json(f)
                 for f in json['invitations']])
        return self

    def load(self):
        data = self.api.get_user(self.email)
        self.from_json(data)

    def load_devices(self):
        data = self.api.get_devices(self.email)
        from .device import Device
        self._devices = frozenset([Device(self.api).from_json(d)
                                   for d in data])

    def load_two_factor(self):
        data = self.api.get_user_twofactor(self.email)
        self._two_factor = data['enforce']

    def save_first_name(self):
        self.api.update_user(self.email, self._first_name, self._last_name)

    def save_last_name(self):
        self.api.update_user(self.email, self._first_name, self._last_name)

    def save_password(self):
        password = self._password
        self._password = None

        if not password:
            self.api.delete_user_password(self.email)
            return

        self.api.update_user_password(self.email, password)

    def save_two_factor(self):
        if not self._two_factor:
            self.api.disable_user_twofactor(self.email)
            return

        self._two_factor = True
        raise NoRouteException(
            'Can not enable two-factor authentication from API.')

    def create(self, first_name, last_name):
        data = self.api.create_user(self.email, first_name, last_name)
        self.from_json(data)

    def delete(self):
        self.api.delete_user(self.email)
