# Authentication

There are two methods of authentication supported by the AeroFS API: individual
access tokens and app tokens generated through OAuth.

For the former, each user may find their token in the AeroFS web client. This
token should automatically have full API access, with permissions for every
[scope](https://developers.aerofs.com/api/en/1.3/#oauth_scopes) except for
`organization.admin`. Note that the `organization.admin` scope should be
treated with caution; many destructive actions may be taken by users with this
scope.

The latter is slightly more complex. The following code block illustrates the
OAuth flow for this SDK.

```python
import aerofs

config = aerofs.api.InstanceConfiguration('share.my-private-cloud.com')
# Generated on a per-app basis in AeroFS WebUI.
creds = aerofs.api.AppCredentials('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                                  'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                                  'http://my-web-app.com')

auth = aerofs.api.APIAuthClient(config, creds)
# For the full list of potential scopes, see [AeroFS scopes](https://developers.aerofs.com/api/en/1.3/#oauth_scopes).
url = auth.get_authorization_url(['organization.admin', 'user.password',
                                  'user.read', 'user.write'])

# The user should be provided with `url` to allow OAuth access to your app.
# They will be redirected to `http://my-web-app.com?code=XXXXXXXXXX
# This route should use the below function to generate an access token for that
# request.
token = auth.get_access_token_with_code(url_params['code'])
```

In either case, once we have a token for a given user, we can use this to make
API requests as that user (and with the requested scopes).

```python
client = aerofs.api.APIClient(config, token)
print client.get_folder_children('root')
```
