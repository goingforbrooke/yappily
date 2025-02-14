# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "atproto",
#     "mastodon-py",
#     "requests",
#     "standard-imghdr",
#     "tweepy",
# ]
# ///
"""Yappily: An X/Twitter client that posts the same message to Twitter variants.

We use tweepy (Python, or the Rust equivalent in the future) because it's necessary for tweeting:
> Please note that only OAuth 1.0a or OAuth 2.0 Authorization Code Flow with PKCE is required to issues requests on behalf of users. The API reference page describes the authentication method required to use an API. You will need user-authentication, user-context, with an access token to perform the following:
> 
> - Post Tweets or other resources
> - Search for users
> - Use any geo endpoint
> - Access Direct Messages or account credentials
> - Retrieve user’s email addresses

[X docs on OAuth2 flow with PKCE](https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/authorization-code#oauth-2-0-authorization-code-flow-with-pkce)
- necessary for tweeting

[Confidential clients](https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/authorization-code#confidential-clients)
- gives us a client secret

[Oauth2 Glossary](https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/authorization-code#glossary)

[source](https://docs.x.com/resources/fundamentals/authentication/oauth-2-0/application-only#app-only-authentication-and-oauth-2-0-bearer-token)
 
API key and secret are also knowns as consumer key and consumer secret. source: https://docs.x.com/resources/fundamentals/authentication/oauth-1-0a/api-key-and-secret#api-key-and-secret
"""
from pathlib import Path

from bluesky import post_to_bluesky
from cli_utils import get_post_text
from hachyderm import post_to_hachyderm
from twitter import send_tweet


def main():
    # Get the directory for this project so we can build relative paths to credential files.
    root_directory = Path(__file__).parent

    # Get the text that the user wants to yap about.
    tweet_text = get_post_text()
    print(f'👅 Yapping "{tweet_text}"')

    # Tweet on X/Twitter.
    send_tweet(tweet_text, root_directory)

    # Toot on Hachyderm.
    post_to_hachyderm(tweet_text, root_directory)

    # Post on Bluesky.
    post_to_bluesky(tweet_text, root_directory)

    print("✅  Done")


if __name__ == "__main__":
    main()
