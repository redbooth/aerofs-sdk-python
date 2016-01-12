from .error import APIException
from .error import ReadOnlyException
from .error import WriteOnlyException


def get_sync(o, field):
    NoneType = type(None)
    if isinstance(o.__dict__['_' + field], NoneType):
        try:
            getattr(o, 'load_{}'.format(field))()
        except AttributeError:
            o.load()

    if isinstance(o.__dict__['_' + field], NoneType):
        raise APIException('Could not retrieve {}.'.format(field))

    return o.__dict__['_' + field]


def set_sync(o, field, v):
    o.__dict__['_' + field] = v
    try:
        getattr(o, 'save_{}'.format(field))()
    except AttributeError:
        raise APIException('No method for syncing {}'.format(field))


def raise_(ex):
    raise ex


def readonly(field, sync=True):
    def readonly_decorator(c):
        setattr(c, field, property(
            lambda o: get_sync(o, field) if sync else o.__dict__['_' + field],
            lambda _, __: raise_(ReadOnlyException(
                '{} is a read-only field.'.format(field))),
            lambda _: raise_(ReadOnlyException(
                '{} is a read-only field.'.format(field)))))
        return c

    return readonly_decorator


def synced(field):
    def synced_decorator(c):
        setattr(c, field, property(
            lambda o: get_sync(o, field),
            lambda o, v: set_sync(o, field, v),
            lambda _: raise_(APIException(
                'Could not delete {}: undefined behaviour.'.format(field)))))
        return c

    return synced_decorator


def writeonly(field):
    def writeonly_decorator(c):
        setattr(c, field, property(
            lambda _: raise_(WriteOnlyException(
                '{} is a write-only field.'.format(field))),
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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
