import requests
from future.utils import iteritems


class APIAuthClient(object):
    def __init__(self, instance_configuration, app_credentials):
        self.instance_configuration = instance_configuration
        self.app_credentials = app_credentials

        self.url_prefix = 'https://{}'.format(instance_configuration.hostname)

        self.session = requests.Session()

    def get_authorization_url(self, scopes):
        scopes = ','.join(scopes)
        return ('{}/authorize?response_type=code'
                '&redirect_uri={}'
                '&scope={}'
                '&client_id={}'
               ).format(self.url_prefix, self.app_credentials.redirect_uri,
                        scopes, self.app_credentials.client_id)

    def get_access_token_with_code(self, code):
        route = '/auth/token'
        data = '&'.join('{}={}'.format(k, v) for k, v in iteritems({
            'client_id': self.app_credentials.client_id,
            'client_secret': self.app_credentials.client_secret,
            'redirect_uri': self.app_credentials.redirect_uri,
            'grant_type': 'authorization_code',
            'code': code,
        }))
        res = self.session.post(
            '{}{}'.format(self.url_prefix, route), data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            if res.json()['error'] == 'invalid_grant':
                return None

            raise

        return res.json()['access_token']

    def revoke_access_token(self, token):
        route = '/auth/token/{}'.format(token)
        res = self.session.delete('{}{}'.format(self.url_prefix, route))
        res.raise_for_status()
        return 'ok'

    def get_access_token_info(self, token):
        route = '/auth/tokeninfo'
        data = {'access_token': token}
        # AeroFS does not create a resource server for 3rd party apps, so we
        # cannot actually use our own client id/secret here.
        res = self.session.get(
            '{}{}'.format(self.url_prefix, route), params=data,
            auth=('oauth-havre', 'i-am-not-a-restful-secret'))
        res.raise_for_status()
        return res.json()
