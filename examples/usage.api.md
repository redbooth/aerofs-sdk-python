# API Usage

The API client implemented in this SDK (eg. `aerofs.api.APIClient`) should be
used as follows:

To initialize the instance, we must provide a valid
`aerofs.api.InstanceConfiguration` as well as an [access token](authentication.md)
for the user for which we wish to make requests. We can then initialize the
client with:

```python
import aerofs

config = aerofs.api.InstanceConfiguration('share.my-private-cloud.com')
client = aerofs.api.APIClient(config, ACCESS_TOKEN)
```

The APIClient instance implements all routes in the [AeroFS API](https://developers.aerofs.com/api/en/1.3/)
in a one-to-one mapping. For example, to [get all users](https://developers.aerofs.com/api/en/1.3/#user_list)
we can run:

```python
client.get_users(limit=0)
```
