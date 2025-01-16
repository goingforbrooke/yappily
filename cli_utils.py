"""Command line utilities."""
from sys import argv


"""Get the text for the tweet/post from the arguments passed to this script."""
def get_post_text():
    if len(argv) < 2:
        print("Usage: yappily <command>\nExample: yappily Hello, world!")
        exit(1)
    
    found_arguments = argv[1:]

    post_text = ' '.join(found_arguments)

    return post_text
