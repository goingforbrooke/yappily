"""Twitter API interactions."""

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