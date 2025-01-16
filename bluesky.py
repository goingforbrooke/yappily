"""Bluesky API interactions.

# Prerequisites

You *can* use your personal password to login, but we recommend creatng an app password to use instead.

"""
from pathlib import Path

from atproto import Client


"""Post on [Bluesky](https://bsky.app)."""
def post_to_bluesky(post_text):
    bluesky_username = get_bluesky_username()
    bluesky_password = get_bluesky_password()

    bluesky_client = Client()

    # Login to Bluesky.
    bluesky_client.login(bluesky_username, bluesky_password)

    bluesky_client.send_post(text=post_text)

    print(f'Posted to Bluesky: {post_text}')
    return True


"""Get the Bluesky username from a file.

This should be in the format `your.username.bsky.social`.

"""
def get_bluesky_username():
    file_path = Path('bluesky_creds/bluesky_username.txt')
    with open(file_path, 'r') as infile:
        username = infile.read()
    return username


"""Get the Bluesky user password or app password."""
def get_bluesky_password():
    file_path = Path('bluesky_creds/bluesky_password.txt')
    with open(file_path, 'r') as infile:
        password = infile.read()
    return password
