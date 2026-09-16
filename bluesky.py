"""Bluesky API interactions.

# Prerequisites

You *can* use your personal password to login, but we recommend creatng an app password to use instead.

Settings -> Privacy and Security -> App Passwords
"""
from pathlib import Path

from atproto import Client
from diagnostics import event, identifier


"""Post on [Bluesky](https://bsky.app)."""
def post_to_bluesky(post_text, root_directory):
    bluesky_username = get_bluesky_username(root_directory)
    bluesky_password = get_bluesky_password(root_directory)

    bluesky_client = Client()

    # Login to Bluesky.
    # todo: Strip username and password characters in file load functions.
    event('authentication_started', platform='bluesky')
    bluesky_client.login(bluesky_username.strip(), bluesky_password.strip())
    event('authentication_completed', platform='bluesky')

    event('delivery_started', platform='bluesky')
    result = bluesky_client.send_post(text=post_text)
    event('delivery_result', platform='bluesky', post_id=identifier(getattr(result, 'uri', None)),
          status='sent', confirmed=True)

    print(f'🌤️ Posted to Bluesky: {post_text}')
    return True


"""Get the Bluesky username from a file.

This should be in the format `your.username.bsky.social`.

"""
def get_bluesky_username(root_directory):
    file_path = Path(root_directory, 'bluesky_creds', 'bluesky_username.txt')
    return file_path.read_text()


"""Get the Bluesky user password or app password."""
def get_bluesky_password(root_directory):
    file_path = Path(root_directory, 'bluesky_creds', 'bluesky_password.txt')
    return file_path.read_text()
