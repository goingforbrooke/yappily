# 👅 Yappily 😁

Post the same message to Twitter 🦜, Hachyderm 🐘, and Bluesky🌤️.

## Installation

Compatibility:
- MacOS: ✅
- *nix: 🤷🏼‍♀️ (probably works)
- Windows: ❌

1. Clone this repo over HTTPS or SSH.

Clone over HTTPS:

```console
git clone https://github.com/goingforbrooke/yappily.git
```

Clone with SSH:

```console
git clone git@github.com:goingforbrooke/yappily.git
```

2. Get credentials.

X posting uses Buffer; Hachyderm and Bluesky use their own APIs.
Create credential directories as needed. Keep secrets out of Git and chat.

- **Twitter/X via Buffer**
  - Connect your X profile to Buffer.
  - Create a personal key in [Buffer Settings → API](https://publish.buffer.com/settings/api).
  - Use `account:read` for channel discovery and `posts:write` for publishing.
    `posts:read` can additionally be enabled for inspecting posts; account-write,
    ideas, insights, and engagement permissions are not needed.
  - Run `yappily --setup-buffer` (or `uv run main.py --setup-buffer`).
    Paste the key at the hidden terminal prompt and select your X channel.
  - Setup saves `buffer_creds/api_key.txt` and `buffer_creds/channel_id.txt`,
    with directory mode `0700` and file mode `0600`. Both are Git-ignored.
  - Alternatively, set `BUFFER_API_KEY` and `BUFFER_X_CHANNEL_ID`; environment
    settings override credential files.
  - Verify without publishing: `yappily --check-buffer`.
  - No direct X API keys or X API credit balance are used. Existing
    `twitter_creds/` files are left untouched but are no longer read.
  - Renew the key in Buffer before its selected expiration and rerun setup.
- **Hachyderm**
  - [hachyderm.io/home](https://hachyderm.io/home)
  - [Development Tab](https://hachyderm.io/settings/applications)
  - "New Application"
  - permissions
    - ☑️ `write:statuses`: publish posts
  - required keys
    - client ID 
      - also known as "Client Key" on the "Development ➡️ Application" page
      - create `yappily/hachyderm_creds/client_id.txt`
    - client secret
      - create `yappily/hachyderm_creds/client_secret.txt`
    - access token
      - also known as "Your access token" on the "Development ➡️ Application" page
      - create `yappily/hachyderm_creds/access_token.txt`
- **Bluesky**
  - "Settings"
  - ["Privacy and Security"](https://bsky.app/settings/privacy-and-security)
  - "App passwords"
  - "Add App Password"
    - don't check "Allow access to your direct messages"
  - necessary keys
    - username
      - should be in the format `your.username.bsky.social`
      - create `yappily/bluesky_creds/bluesky_username.txt`
    - password
      - create `yappily/bluesky_creds/bluesky_password.txt`

> [!NOTE]
> X posts are submitted through Buffer using `shareNow`, not added to your regular
> queue. Buffer acceptance is not proof of publication: Yappily prints the returned
> post ID and status and explicitly notes when publication is unconfirmed.
> See [Buffer's API guide](https://developers.buffer.com/guides/rest-migration.html).
>
> Historical limit note (original label `25-1-26`, apparently January 26, 2025):
> this README recorded a direct-X free-tier allowance of 100 posts/month. That is
> not a current limit and is unrelated to the Buffer integration.

3. Install Dependencies

> [!TIP]
> [Avoid manually installing dependencies](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) and skip to [`uv run`](#run-as-uv-script).

> [!TIP]
> [Zsh](https://www.zsh.org.) users can run Yappily from anywhere by adding this file as `yapply` to `~/bin`:
> ```zsh
> #!/bin/zsh
> uv run ~/path/to/where/you/clone/repos/yappily/main.py "$@"
> ```

### Install with [`uv`](https://docs.astral.sh/uv/)

This isn't necessary for `uv run`, but is included here for those who would like to set up a virtual environment.

### Install with [`pip`](https://pip.pypa.io/en/stable/installation/)

```console
pip install -r requirements.txt
```

## Usage

You can run Yappily with any `requirements.txt`-friendly project manager, but we recommend[`uv`](https://docs.astral.sh/uv/)

### Select platforms and retry safely

```console
yappily --only x "Post only to X via Buffer"
yappily --only hachyderm,bluesky "Post to the other two"
yappily --check-buffer
```

By default all three platforms are attempted independently. A failure returns exit
status 1 after the remaining platforms are attempted; the summary lists accepted
and failed/unconfirmed destinations. There are no automatic retries. If a response
is lost, check the affected service before retrying to avoid duplicates. Use
`--only` so a retry does not repeat posts on successful platforms.

Use `--` before literal post text starting with a dash, e.g.
`yappily -- "--not-an-option"`.

### Run as `uv` Script

Use `uv run`:

```console
uv run main.py "<some_awesome_text>"`
```

Surrounding the post text is optional, but recommended. It prevents your shell from interpreting special characters. For example, the `'` in `uv run main.py Yappily's awesome` will cause issues in [zsh](https://www.zsh.org.). Using `uv run main.py "Yappily's awesome"` instead.

Example:

```console
uv run main.py "using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy"
```

```console
👅 Yapping "using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy"
🦜 Submitted to Buffer for immediate X posting (post <id>, status: scheduled).
   Publication is not confirmed yet; check Buffer before retrying.
🐘 Posted to Hachyderm: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
🌤️ Posted to Bluesky: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
✅ Accepted by: x, hachyderm, bluesky
```

### Run with `python`

This works the same as the [`uv run`](#run-as-uv-script), but replace `uv run` with `python`.

> [!IMPORTANT]
> Install dependencies and/or activate a virtual environment first.

```console
python main.py
```

```console
python main.py "using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy"
```

```console
👅 Yapping "using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy"
🦜 Submitted to Buffer for immediate X posting (post <id>, status: scheduled).
   Publication is not confirmed yet; check Buffer before retrying.
🐘 Posted to Hachyderm: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
🌤️ Posted to Bluesky: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
✅ Accepted by: x, hachyderm, bluesky
```

## Future

- check for Bluesky's 300 grapheme limit
- post to Insta Threads 🧵
- RIIW (Rewrite in Rust) 🦀
- make mobile app 🤳🏻
- use oAuth for credentials? 🔐
- add image uploads 📸
    - aspect ratio cropping would be nice
- parallel posting 🏎️
- post to YouTube communities 📽️
- allow threads? 🧵
- add logging 🪵
- slick packaging 📦
- collect stats 📈
    - 30 day averages in terminal
    - matplotlib graphs in webpage 

## Contributing

### Updating Dependencies

Dependencies are tracked in three locations:

1. `uv`'s`pyproject.toml`
  - source of truth
  - created by [`uv init`](https://docs.astral.sh/uv/guides/projects/)

2. [inline script metadata](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata) dependencies (at the top of `main.py`)
  - fuels our preferred way to execute Yappily (with `uv run `main.py`)

3. `requirements.txt`
  - for compatibility

> [!IMPORTANT]
> Update `requirements.txt` with the latest from `uv`:

```console
uv export --format requirements-txt > requirements.txt
```

## License

[MIT](https://choosealicense.com/licenses/mit/)