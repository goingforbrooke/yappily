"""Twitter API interactions."""
from pathlib import Path

from tweepy import Client


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

    # Tweet the user's provided text.
    api_client.create_tweet(text=tweet_text)

    print(f'Tweeted on X/Twitter: {tweet_text}')
    return True


"""Consumer key is known as "API Key" in "Projects and Apps."""
def get_consumer_key():
    file_path = Path('twitter_creds/api_key.txt')
    with open(file_path, 'r') as infile:
        consumer_key = infile.read()
    return consumer_key


"""Consumer secret is known as "API Key" in "Projects and Apps."""
def get_consumer_secret():
    file_path = Path('twitter_creds/api_key_secret.txt')
    with open(file_path, 'r') as infile:
        consumer_secret = infile.read()
    return consumer_secret


"""Get the access token from a file."""
def get_access_token():
    file_path = Path('twitter_creds/access_token.txt')
    with open(file_path, 'r') as infile:
        access_token = infile.read()
    return access_token


"""Get the access token secret from a file."""
def get_access_token_secret():
    file_path = Path('twitter_creds/access_token_secret.txt')
    with open(file_path, 'r') as infile:
        access_token_secret = infile.read()
    return access_token_secret
