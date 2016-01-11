import enum


class ContentState(enum.Enum):
    AVAILABLE = 'AVAILABLE'
    SYNCING = 'SYNCING'
    DESELECTED = 'DESELECTED'
    INSUFFICIENT_STORAGE = 'INSUFFICIENT_STORAGE'


class Permission(enum.IntEnum):
    WRITE = 1
    MANAGE = 2


# TODO: use permission enum throughout, then update this method
def get_role(permissions=0):
    return {
        0: 'VIEWER',
        1: 'EDITOR',
        2: 'MANAGER',
        3: 'OWNER',
    }[permissions]
