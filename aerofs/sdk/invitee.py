from .interface import APIObject
from .interface import readonly


@readonly('email', sync=False)
@readonly('inviter')
@readonly('signup_code')
class Invitee(APIObject):
    def __init__(self, api, email):
        super(Invitee, self).__init__(api)

        self._email = email
        self._inviter = None
        self._signup_code = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.email == other.email
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.email != other.email
        return NotImplemented

    def from_json(self, json):
        self._email = json['email_to']
        from .user import User
        self._inviter = User(self.api, json['email_from'])
        self._signup_code = json['signup_code']
        return self

    def load(self):
        data = self.api.get_invitee(self.email)
        self.from_json(data)

    def create(self, inviter_email):
        data = self.api.create_invitee(inviter_email, self.email)
        self.from_json(data)

    def delete(self):
        self.api.delete_invitee(self.email)
