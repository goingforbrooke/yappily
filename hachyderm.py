"""Hachyderm API interactions.

# Prerequisites

- Redirect URI (default): `urn:ietf:wg:oauth:2.0:oob`

[Create a new application](https://hachyderm.io/settings/applications/new) with these permissions:
- `write:statuses`
- `write:media`: In case we want to add image posting later.
"""


"""Post on Hachyderm."""
def post_to_hachyderm(post_text: str):
    pass

