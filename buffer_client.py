"""Publish to X through Buffer's GraphQL API, not the paid direct X API.

API reference: https://developers.buffer.com/guides/rest-migration.html
"""
import getpass
import os
from pathlib import Path

import requests

API_URL = "https://api.buffer.com"
API_SETTINGS_URL = "https://publish.buffer.com/settings/api"

ORGANIZATIONS_QUERY = """
query YappilyOrganizations {
  account { organizations { id name } }
}
"""
CHANNELS_QUERY = """
query YappilyChannels($input: ChannelsInput!) {
  channels(input: $input) { id name service }
}
"""
CHANNEL_QUERY = """
query YappilyChannel($input: ChannelInput!) {
  channel(input: $input) { id name service }
}
"""
CREATE_POST_MUTATION = """
mutation YappilyShareNow($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id status } }
    ... on MutationError { message }
  }
}
"""


class BufferError(RuntimeError):
    """A safe-to-display Buffer configuration or request error."""


def request(api_key: str, query: str, variables: dict | None = None) -> dict:
    """Do not retry: a lost mutation response may still have published a post."""
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"query": query, "variables": variables or {}},
            timeout=(10, 30),
            allow_redirects=False,
        )
    except requests.RequestException:
        raise BufferError(
            "Buffer connection failed. If submitting a post, delivery is unknown; "
            "check Buffer before retrying."
        ) from None
    if not 200 <= response.status_code < 300:
        raise BufferError(
            f"Buffer returned HTTP {response.status_code}. Check API access, "
            "rate limits, and Buffer's queue before retrying."
        )
    try:
        payload = response.json()
    except ValueError:
        raise BufferError("Buffer returned invalid JSON; check Buffer before retrying.") from None
    if not isinstance(payload, dict):
        raise BufferError("Unexpected Buffer response; check Buffer before retrying.")
    if payload.get("errors"):
        # Avoid echoing response bodies that could contain credentials or request data.
        raise BufferError(
            "Buffer reported GraphQL errors. Check API access and Buffer's queue "
            "before retrying; delivery may be unknown."
        )
    if not isinstance(payload.get("data"), dict):
        raise BufferError("Buffer returned no data; check Buffer before retrying.")
    return payload["data"]


def get_setting(root_directory: Path, filename: str, env_name: str) -> str:
    value = os.environ.get(env_name, "").strip()
    if not value:
        try:
            value = (root_directory / "buffer_creds" / filename).read_text().strip()
        except FileNotFoundError:
            pass
    if not value:
        raise BufferError(f"Buffer is not configured ({env_name}); run yappily --setup-buffer.")
    return value


def get_config(root_directory: Path) -> tuple[str, str]:
    return (
        get_setting(root_directory, "api_key.txt", "BUFFER_API_KEY"),
        get_setting(root_directory, "channel_id.txt", "BUFFER_X_CHANNEL_ID"),
    )


def validate_channel(api_key: str, channel_id: str) -> dict:
    channel = request(api_key, CHANNEL_QUERY, {"input": {"id": channel_id}}).get("channel")
    if not isinstance(channel, dict) or channel.get("service") != "twitter":
        raise BufferError("Configured Buffer channel is missing or is not X/Twitter; run yappily --setup-buffer.")
    if channel.get("id") != channel_id:
        raise BufferError("Buffer returned a different channel than requested; refusing to post.")
    return channel


def check_buffer(root_directory: Path) -> None:
    """Read-only authentication and destination check; never creates a post."""
    api_key, channel_id = get_config(root_directory)
    channel = validate_channel(api_key, channel_id)
    print(f"✅ Buffer API access verified: X/Twitter — {channel['name']} ({channel_id}). Nothing posted.")


def send_tweet(tweet_text: str, root_directory: Path) -> bool:
    api_key, channel_id = get_config(root_directory)
    validate_channel(api_key, channel_id)
    data = request(api_key, CREATE_POST_MUTATION, {"input": {
        "text": tweet_text,
        "channelId": channel_id,
        "schedulingType": "automatic",
        "mode": "shareNow",
        "assets": [],
        "needsApproval": False,
        "saveToDraft": False,
    }})
    result = data.get("createPost")
    if not isinstance(result, dict):
        raise BufferError("Missing Buffer post result; check Buffer before retrying.")
    if result.get("__typename") != "PostActionSuccess":
        message = str(result.get("message") or "Post was rejected").replace(api_key, "[redacted]")
        raise BufferError(f"Buffer: {message}")
    post = result.get("post")
    if not isinstance(post, dict) or not post.get("id") or not post.get("status"):
        raise BufferError("Incomplete Buffer post result; check Buffer before retrying.")
    if post["status"] == "sent":
        print(f"🦜 Posted on X/Twitter via Buffer (post {post['id']}).")
    elif post["status"] == "error":
        raise BufferError(f"Buffer post {post['id']} failed to publish; check Buffer for details.")
    elif post["status"] in {"draft", "notSent"}:
        raise BufferError(f"Buffer post {post['id']} has status {post['status']}; check Buffer before retrying.")
    else:
        # shareNow is asynchronous: API acceptance is not proof of publication.
        print(f"🦜 Submitted to Buffer for immediate X posting (post {post['id']}, status: {post['status']}).")
        print("   Publication is not confirmed yet; check Buffer before retrying.")
    return True


def setup_buffer(root_directory: Path) -> None:
    """Prompt locally for a key, discover X channels, and save private credentials."""
    print(f"Create a personal API key at {API_SETTINGS_URL}")
    if any(os.environ.get(name, "").strip() for name in ("BUFFER_API_KEY", "BUFFER_X_CHANNEL_ID")):
        raise BufferError("Unset BUFFER_API_KEY and BUFFER_X_CHANNEL_ID before setup; environment values override saved settings.")
    api_key = getpass.getpass("Buffer API key (hidden): ").strip()
    if not api_key:
        raise BufferError("No API key entered; nothing saved.")
    account = request(api_key, ORGANIZATIONS_QUERY).get("account")
    if not isinstance(account, dict) or not isinstance(account.get("organizations"), list):
        raise BufferError("Buffer did not return account organizations; nothing saved.")
    channels = []
    for organization in account["organizations"]:
        result = request(api_key, CHANNELS_QUERY, {"input": {"organizationId": organization["id"]}})
        for channel in result.get("channels", []):
            if channel["service"] == "twitter":
                channels.append((organization["name"], channel))
    if not channels:
        raise BufferError("No X/Twitter channel found. Connect X in Buffer, then rerun setup.")
    for number, (organization, channel) in enumerate(channels, start=1):
        print(f"{number}. {channel['name']} — {organization} ({channel['id']})")
    choice = input("Choose your X channel [1]: ").strip() or "1"
    if not choice.isdigit() or not 1 <= int(choice) <= len(channels):
        raise BufferError("Invalid channel selection; nothing saved.")
    channel = channels[int(choice) - 1][1]
    validate_channel(api_key, channel["id"])
    directory = root_directory / "buffer_creds"
    directory.mkdir(mode=0o700, exist_ok=True)
    directory.chmod(0o700)
    for filename, value in (("api_key.txt", api_key), ("channel_id.txt", channel["id"])):
        # Set permissions before writing, including when replacing an existing key.
        fd = os.open(directory / filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as file:
            os.fchmod(file.fileno(), 0o600)
            file.write(value + "\n")
    print(f"✅ Buffer configured for X/Twitter — {channel['name']}. Nothing posted.")
