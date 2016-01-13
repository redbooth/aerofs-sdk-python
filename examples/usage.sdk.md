# SDK Usage

This SDK also provides a higher-level abstraction of the AeroFS API. This
implementation is located under `aerofs.sdk`.

All resources must be initialized with a valid instance of an APIClient. For
details, see [API Usage](usage.api.md).

The following resources are implemented:

* Device
* File
* Folder
* Group
* GroupMember
* Invitation
* Invitee
* SFGroupMember
* SFMember
* SFPendingMember
* SharedFolder
* User

Each of these objects syncs with the AeroFS backend on change and lazy-loads
attributes as they are requested. For example:

```python
import aerofs

# No network request
me = aerofs.sdk.User(client, 'my-email@company.com')

# Calls GET /users/{email} to load data
print 'My name is', me.first_name, me.last_name

# Calls PUT /users/{email} with the new first_name; user is updated in backend
me.first_name = 'Foo'
```

The SDK uses [ETags](https://developers.aerofs.com/api/en/1.3/#overview_etags)
wherever possible to ensure consistency; to do this manually, we can call the
`.load()` method on any resource to ensure the local copy is up-to-date with
the API.

```python
old_first_name = me.first_name
me.load()
if me.first_name != old_first_name:
    print 'User has changed their first name since last read.'
```

Resource objects may also be completely created or destroyed: for example:

```python
root = aerofs.sdk.Folder(client, 'root')

new_file = aerofs.sdk.File(client)
new_file.create(root.id, 'filename.txt') # Creates a new file
new_file.content = open('~/test-file.txt', 'r') # Updates the file's contents
new_file.move(root.id, 'new-filename.txt') # Renames or moves file
new_file.delete() # Deletes that file
```
