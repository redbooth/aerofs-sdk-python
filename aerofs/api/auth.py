#import requests

class APIAuthClient(object):
    def __init__(self, instance_configuration, app_credentials):
        self.instance_configuration = instance_configuration
        self.app_credentials = app_credentials

    def get_access_token_with_code(self, code):
        # TODO finish this...
        return