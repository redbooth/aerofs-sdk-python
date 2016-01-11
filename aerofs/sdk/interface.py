from .error import PermissionException
from .error import ReadOnlyException
from .error import WriteOnlyException


REQUIRED_SCOPE = {
    'invitations': 'acl.invitations',
    'shares': 'acl.read',
}


def get_sync(o, field):
    NoneType = type(None)
    if isinstance(o.__dict__['_' + field], NoneType):
        try:
            getattr(o, 'load_{}'.format(field))()
        except AttributeError:
            o.load()

    if isinstance(o.__dict__['_' + field], NoneType):
        raise PermissionException('{} requires {} scope(s).'.format(
            field.title(), REQUIRED_SCOPE[field]))

    return o.__dict__['_' + field]


def set_sync(o, field, v):
    o.__dict__['_' + field] = v
    getattr(o, 'save_' + field)()


def raise_(ex):
    raise ex


def readonly(field, sync=True):
    def readonly_decorator(c):
        setattr(c, field, property(
            lambda o: get_sync(o, field) if sync else o.__dict__['_' + field],
            lambda _, __: raise_(ReadOnlyException(
                '{} is a read-only field.'.format(field.title())))))
        return c

    return readonly_decorator


def synced(field):
    def synced_decorator(c):
        setattr(c, field, property(
            lambda o: get_sync(o, field),
            lambda o, v: set_sync(o, field, v)))
        return c

    return synced_decorator


def writeonly(field):
    def writeonly_decorator(c):
        setattr(c, field, property(
            lambda _: raise_(WriteOnlyException(
                '{} is a write-only field.'.format(field.title()))),
            lambda o, v: set_sync(o, field, v),
            lambda o: set_sync(o, field, None)))
        return c

    return writeonly_decorator


class APIObject(object):
    def __init__(self, api):
        self.api = api

    def from_json(self, _json):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()
