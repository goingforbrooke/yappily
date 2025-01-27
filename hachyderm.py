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

from mastodon import Mastodon


"""Post on [Hachyderm](https://hachyderm.io)."""
def post_to_hachyderm(post_text: str, root_directory: Path):
    client_id = get_client_id(root_directory)
    client_secret = get_client_secret(root_directory)
    access_token = get_access_token(root_directory)

    # Authenticate with the Mastodon API.
    mastodon_client = Mastodon(api_base_url='https://hachyderm.io',
                               client_id=client_id,
                               client_secret=client_secret,
                               access_token=access_token)

    # Post the text to Hachyderm.
    mastodon_client.toot(post_text)

    print(f'🐘 Posted to Hachyderm: {post_text}')
    return True


"""Get the client ID, which is known as "Client Key" on the Development -> Application."""
def get_client_id(root_directory):
    file_path = Path(root_directory, 'hachyderm_creds', 'client_id.txt')
    return file_path.read_text()


"""Get the client secret, which is known as "Client Secret" on the Development -> Application."""
def get_client_secret(root_directory):
    file_path = Path(root_directory, 'hachyderm_creds', 'client_secret.txt')
    return file_path.read_text()


"""Get the access token, which is known as "Your access token" on the Development -> Application."""
def get_access_token(root_directory):
    file_path = Path(root_directory, 'hachyderm_creds', 'access_token.txt')
    return file_path.read_text()
