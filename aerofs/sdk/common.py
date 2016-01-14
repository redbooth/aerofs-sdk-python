import enum


class ContentState(enum.Enum):
    AVAILABLE = 'AVAILABLE'
    SYNCING = 'SYNCING'
    DESELECTED = 'DESELECTED'
    INSUFFICIENT_STORAGE = 'INSUFFICIENT_STORAGE'
    UNKNOWN = 'UNKNOWN'


class Permission(enum.Enum):
    WRITE = 'WRITE'
    MANAGE = 'MANAGE'
