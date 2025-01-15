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
from tweepy import Client, OAuth2UserHandler


def main():
    client_id = get_client_id()
    redirect_uri = 'https://goingforbrooke.com'
    scopes = ['tweet.read', 'tweet.write', 'offline.access']
    client_secret = get_client_secret()

    oauth2_user_handler = OAuth2UserHandler(client_id=client_id,
                                            redirect_uri=redirect_uri,
                                            scope=scopes,
                                            # Client Secret is only necessary if using a confidential client
                                            client_secret=client_secret)
    auth_url = oauth2_user_handler.get_authorization_url()
    print(auth_url)

    # todo: Use PIN authentication b/c it's CLI friendly.
    redirected_url = input("paste the full redirect url here: ")

    fetch_response = oauth2_user_handler.fetch_token(redirected_url)
    print(fetch_response)

    access_token = fetch_response['access_token']
    print(access_token)

    api_client = Client(bearer_token=get_bearer_token(),
                        consumer_key=get_consumer_key(),
                        consumer_secret=get_consumer_secret(),
                        access_token=access_token,
                        access_token_secret=get_access_token_secret())

    api_client.create_tweet(text="Hello, world!")

    print("Done")

"""GOAL

client = tweepy.Client(consumer_key='REPLACE_ME',
                       consumer_secret='REPLACE_ME',
                       access_token='REPLACE_ME',
                       access_token_secret='REPLACE_ME')

# Replace the text with whatever you want to Tweet about
response = client.create_tweet(text='hello world')

print(response)

"""

def get_bearer_token():
    with open('bearer_token.txt', 'r') as infile:
        bearer_token = infile.read()
    return bearer_token

def get_access_token_secret():
    with open('access_token_secret.txt', 'r') as infile:
        access_token_secret = infile.read()
    return access_token_secret

def get_consumer_secret():
    with open('api_key_secret.txt', 'r') as infile:
        consumer_secret = infile.read()
    return consumer_secret

def get_consumer_key():
    with open('api_key.txt', 'r') as infile:
        consumer_key = infile.read()
    return consumer_key

"""Load the client secret from a file."""
def get_client_secret():
    with open('client_secret.txt', 'r') as infile:
        client_secret = infile.read()
    return client_secret


"""Load the client ID from a file."""
def get_client_id():
    with open('client_id.txt', 'r') as infile:
        client_id = infile.read()
    return client_id


if __name__ == "__main__":
    main()
