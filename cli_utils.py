"""Command line utilities."""
import argparse


PLATFORMS = ("x", "hachyderm", "bluesky")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Cross-post to X via Buffer, Hachyderm, and Bluesky.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--setup-buffer", action="store_true", help="Save a Buffer key and select your X channel; nothing posted")
    modes.add_argument("--check-buffer", action="store_true", help="Verify Buffer access without posting")
    parser.add_argument("--only", metavar="PLATFORMS", help="Comma-separated platforms: x,hachyderm,bluesky")
    parser.add_argument("text", nargs="*", help="Post text (quote it; use -- before text starting with a dash)")
    args = parser.parse_args(argv)
    if args.setup_buffer or args.check_buffer:
        if args.only is not None or args.text:
            parser.error("setup/check cannot be combined with post text or --only")
    elif not args.text or not " ".join(args.text).strip():
        parser.error('provide post text, e.g. yappily "Hello, world!"')
    if args.only is not None:
        args.only = [name.strip().lower() for name in args.only.split(",")]
        if any(name not in PLATFORMS for name in args.only):
            parser.error("--only must contain x, hachyderm, and/or bluesky (comma-separated)")
    return args


def get_post_text():
    """Compatibility helper for callers that only need the text."""
    return " ".join(parse_args().text)
