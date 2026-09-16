# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "atproto",
#     "mastodon-py",
#     "requests",
#     "standard-imghdr",
# ]
# ///
"""Cross-post to X via Buffer, Hachyderm, and Bluesky."""
from pathlib import Path
import time

from diagnostics import RunLog, event, error_details, classify_error, runtime_details, show_logs

from buffer_client import BufferError, check_buffer, send_tweet, setup_buffer
from cli_utils import parse_args


def main(argv=None):
    root_directory = Path(__file__).parent
    args = parse_args(argv)
    if args.logs or args.failures:
        return show_logs(failures_only=args.failures)
    with RunLog() as run:
        operation = 'setup_buffer' if args.setup_buffer else 'check_buffer' if args.check_buffer else 'post'
        try:
            runtime = runtime_details(root_directory)
        except Exception:
            runtime = {'runtime_metadata': 'unavailable'}
        event('run_started', operation=operation, **runtime)
        code = execute(args, root_directory)
        event('run_finished', exit_code=code, elapsed_ms=round((time.monotonic() - run.started) * 1000))
        if code and run.file is not None:
            print(f'🧾 Diagnostics: {run.path} (or yappily --failures)')
        return code


def execute(args, root_directory):
    if args.setup_buffer or args.check_buffer:
        try:
            (setup_buffer if args.setup_buffer else check_buffer)(root_directory)
        except (BufferError, OSError, EOFError) as error:
            event('operation_failed', category=classify_error(error), **error_details(error))
            print(f"❌ {error}")
            return 1
        return 0

    post_text = " ".join(args.text)
    print(f'👅 Yapping "{post_text}"')
    selected = list(dict.fromkeys(args.only or ("x", "hachyderm", "bluesky")))
    event('post_started', platforms=selected, text_characters=len(post_text), text_bytes=len(post_text.encode('utf-8')))
    failed = []
    completed = []
    for name in selected:
        started = time.monotonic()
        event('platform_started', platform=name)
        try:
            # Resolve only this platform's SDK, inside its failure boundary.
            if name == "x":
                send_tweet(post_text, root_directory)
            elif name == "hachyderm":
                from hachyderm import post_to_hachyderm
                post_to_hachyderm(post_text, root_directory)
            elif name == "bluesky":
                from bluesky import post_to_bluesky
                post_to_bluesky(post_text, root_directory)
        except Exception as error:
            # One service must not prevent delivery to the others. Do not echo
            # arbitrary SDK exceptions, which can include credentials or bodies.
            detail = str(error) if isinstance(error, BufferError) else type(error).__name__
            print(f"❌ {name}: {detail}")
            event('platform_failed', platform=name, category=classify_error(error),
                  elapsed_ms=round((time.monotonic() - started) * 1000), **error_details(error))
            failed.append(name)
        else:
            event('platform_accepted', platform=name, elapsed_ms=round((time.monotonic() - started) * 1000))
            completed.append(name)
    event('post_finished', accepted=completed, failed=failed)
    if completed:
        print(f"✅ Accepted by: {', '.join(completed)}")
    if failed:
        print(f"❌ Failed or unconfirmed: {', '.join(failed)}")
        print("Check the affected platforms before retrying: a lost response can still mean a published post.")
        print(f"Retry only those platforms with: yappily --only {','.join(failed)} -- \"your post text\"")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
