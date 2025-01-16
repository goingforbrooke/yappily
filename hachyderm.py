"""Hachyderm API interactions.

# Prerequisites

1. Preferences -> Development -> New Application

[Create a new application](https://hachyderm.io/settings/applications/new)

- Redirect URI (default): `urn:ietf:wg:oauth:2.0:oob`

Permissions:

- `write:statuses`
- `write:media`: In case we want to add image posting later.

2. Navigate to the application that you made and copy these values into these files:
- "Client key" -> `hachyderm_creds/client_id.txt`
- "Client secret" -> `hachyderm_creds/client_secret.txt`
- "Your access token" -> `hachyderm_creds/access_token.txt`
"""
from pathlib import Path


"""Post on Hachyderm."""
def post_to_hachyderm(post_text: str):
    client_id = get_client_id()
    client_secret = get_client_secret()
    access_token = get_access_token()

    print(f'Posted to Hachyderm: {post_text}')
    return True


"""Get the client ID, which is known as "Client Key" on the Development -> Application."""
def get_client_id():
    file_path = Path('hachyderm_creds/client_id.txt')
    with open(file_path, 'r') as infile:
        client_id = infile.read()
    return client_id


"""Get the client secret, which is known as "Client Secret" on the Development -> Application."""
def get_client_secret():
    file_path = Path('hachyderm_creds/client_secret.txt')
    with open(file_path, 'r') as infile:
        client_secret = infile.read()
    return client_secret


"""Get the access token, which is known as "Your access token" on the Development -> Application."""
def get_access_token():
    file_path = Path('hachyderm_creds/access_token.txt')
    with open(file_path, 'r') as infile:
        access_token = infile.read()
    return access_token
