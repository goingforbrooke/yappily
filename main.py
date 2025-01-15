#!/usr/bin/env python3
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
from tweepy import Client


def main():
    tweet_text = "Hello, world!"
    send_tweet(tweet_text)

    print("Done")


"""Send a tweet from Twitter/X."""
def send_tweet(tweet_text: str):
    consumer_key = get_consumer_key()
    consumer_secret = get_consumer_secret()
    access_token = get_access_token()
    access_token_secret = get_access_token_secret()

    api_client = Client(consumer_key=get_consumer_key(),
                        consumer_secret=get_consumer_secret(),
                        access_token=get_access_token(),
                        access_token_secret=get_access_token_secret())

    api_client.create_tweet(text=tweet_text)

    print(f'Sent tweet: {tweet_text}')
    return True


"""Consumer key is known as "API Key" in "Projects and Apps."""
def get_consumer_key():
    with open('api_key.txt', 'r') as infile:
        consumer_key = infile.read()
    return consumer_key


"""Consumer secret is known as "API Key" in "Projects and Apps."""
def get_consumer_secret():
    with open('api_key_secret.txt', 'r') as infile:
        consumer_secret = infile.read()
    return consumer_secret


"""Get the access token from a file."""
def get_access_token():
    with open('access_token.txt', 'r') as infile:
        access_token = infile.read()
    return access_token


"""Get the access token secret from a file."""
def get_access_token_secret():
    with open('access_token_secret.txt', 'r') as infile:
        access_token_secret = infile.read()
    return access_token_secret


if __name__ == "__main__":
    main()
