# 👅 Yappily 😁

Post the same message to Twitter 🦜, Hachyderm 🐘, and 🌤️Bluesky.

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

You need to get API keys from Twitter, Hachyderm, and Bluesky.

Paste each one into their corresponding text files at the paths noted below.

The `*_creds` already exist for your convenience.

Each site needs a different set of credentials:

- **Twitter/X**
  - requires a ["Developer Portal"](https://developer.twitter.com/en/portal) account
    - (different from your main account)
    - setup
      - set up for "User Authentication"
      - Type of App: "Web App, Automated App, or Bot"
      - callback uri: up to you, but we won't be using it
      - website url: your website's URL
  - required keys
    - consumer key
      - sometimes known as "API Key" in "Projects and Apps"
      - create `yappily/twitter_creds/api_key.txt`
    - consumer secret
      - sometimes known as "API Key" in "Projects and Apps."
      - create `yappily/twitter_creds/api_key_secret.txt`
    - access token
      - create `yappily/twitter_creds/access_token.txt`
    - access token secret
      - create `yappily/twitter_creds/access_token_secret.txt`
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

[!CAUTION]
Twitter/X's free tier has very low limits. As of 25-1-26, you get 100 posts each month, which may be insufficient for profific posters.

3. Install Dependencies

[!TIP]
[Avoid manually installing dependencies](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) and skip to [`uv run`](#run-as-uv-script).

[!TIP]
[Zsh](https://www.zsh.org.) users can run Yappily from anywhere by adding this file as `yapply` to `~/bin`:
```zsh
#!/bin/zsh
uv run ~/path/to/where/you/clone/repos/yappily/main.py "$@"
```

### Install with [`uv`](https://docs.astral.sh/uv/)

This isn't necessary for `uv run`, but is included here for those who would like to set up a virtual environment.

### Install with [`pip`](https://pip.pypa.io/en/stable/installation/)

```console
pip install -r requirements.txt
```

## Usage

You can run Yappily with any `requirements.txt`-friendly project manager, but we recommend[`uv`](https://docs.astral.sh/uv/)

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
🦜 Tweeted on X/Twitter: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
🐘 Posted to Hachyderm: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
🌤️ Posted to Bluesky: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
✅ Done
```

### Run with `python`

This works the same as the [`uv run`](#run-as-uv-script), but replace `uv run` with `python`.

[!IMPORTANT]
Install dependencies and/or activate a virtual environment first.

```console
python main.py
```

```console
python main.py "using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy"
```

```console
👅 Yapping "using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy"
🦜 Tweeted on X/Twitter: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
🐘 Posted to Hachyderm: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
🌤️ Posted to Bluesky: using QR codes to sign into Slack workspaces on mobile brings me such unbridled joy
✅ Done
```

## Future

- allow posting to fewer than all sites 🔧
  - right now, it fails if you don't provide credentials for each one
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

Be sure to update `requirements.txt` with the latest from `uv`:

```console
uv export --format requirements-txt > requirements.txt
```

## License

[MIT](https://choosealicense.com/licenses/mit/)