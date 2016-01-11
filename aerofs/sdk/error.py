class APIException(Exception):
    pass


class NoRouteException(APIException):
    pass


class ReadOnlyException(APIException):
    pass


class WriteOnlyException(APIException):
    pass
