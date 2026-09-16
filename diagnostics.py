"""Private, bounded, per-run JSONL diagnostics; no SDK wire logging.

Only deliberately selected metadata is persisted. Exception messages, response
bodies, request headers, argv, source lines, and frame locals are never serialized.
"""
from contextvars import ContextVar
from datetime import datetime, timezone
from importlib.metadata import version, PackageNotFoundError
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import uuid

_ACTIVE = ContextVar('yappily_diagnostics', default=None)
MAX_RUNS = 50
MAX_BYTES = 256 * 1024


def log_directory():
    override = os.environ.get('YAPPILY_LOG_DIR')
    if override:
        return Path(override).expanduser()
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Logs' / 'Yappily'
    return Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state')) / 'yappily' / 'logs'


def identifier(value):
    """Bounded service IDs/codes, never arbitrary error messages or URLs."""
    if isinstance(value, (str, int)):
        text = str(value)
        if re.fullmatch(r'[A-Za-z0-9_.-]{1,200}', text):
            return text
        if re.fullmatch(r'at://did:plc:[a-z0-9]+/app\.bsky\.feed\.post/[a-z0-9]+', text):
            return text
    return None


def error_details(error):
    """Stack locations without source/locals/exception text; numeric HTTP status."""
    frames = []
    tb = error.__traceback__
    while tb is not None:
        frames.append({'file': Path(tb.tb_frame.f_code.co_filename).name,
                       'function': tb.tb_frame.f_code.co_name, 'line': tb.tb_lineno})
        tb = tb.tb_next
    details = {'error_type': type(error).__name__, 'frames': frames[-20:]}
    # Requests / atproto response status; Mastodon.py may put status in args.
    response = getattr(error, 'response', None)
    status = getattr(response, 'status_code', None)
    if not isinstance(status, int):
        status = getattr(error, 'status_code', None)
    if not isinstance(status, int):
        status = next((arg for arg in error.args if type(arg) is int and 100 <= arg <= 599), None)
    if type(status) is int and 100 <= status <= 599:
        details['http_status'] = status
    if isinstance(error, OSError) and isinstance(error.errno, int):
        details['errno'] = error.errno
    return details


def classify_error(message):
    """Extract known categories without retaining potentially sensitive prose."""
    text = str(message).lower()
    for needles, category in (
        (('credits depleted', 'insufficient credits', 'payment required'), 'billing'),
        (('rate limit', 'too many requests'), 'rate_limit'),
        (('unauthorized', 'invalid token', 'expired', 'invalid api key'), 'authentication'),
        (('permission', 'forbidden', 'scope'), 'permission'),
        (('too long', 'character limit'), 'text_length'),
        (('duplicate',), 'duplicate'),
        (('not configured', 'no api key'), 'configuration'),
    ):
        if any(needle in text for needle in needles):
            return category
    return 'unclassified'


def event(name, **fields):
    run = _ACTIVE.get()
    if run is not None:
        run.event(name, **fields)


def runtime_details(root):
    packages = {}
    for name in ('requests', 'atproto', 'Mastodon.py', 'standard-imghdr'):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = 'not-installed'
        except Exception:
            # Broken/unreadable metadata is not a reason to block publishing.
            packages[name] = 'unavailable'
    details = {'python': platform.python_version(), 'os': platform.system(), 'packages': packages}
    try:
        revision = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=root,
                                  capture_output=True, text=True, timeout=2)
        if revision.returncode == 0:
            details['revision'] = revision.stdout.strip()
        status = subprocess.run(['git', 'status', '--porcelain'], cwd=root,
                                capture_output=True, text=True, timeout=2)
        if status.returncode == 0:
            details['worktree_dirty'] = bool(status.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return details


class RunLog:
    def __init__(self):
        self.run_id = uuid.uuid4().hex
        self.started = time.monotonic()
        self.file = None
        self.path = None
        self.bytes_written = 0
        self.warned = False
        self.token = None

    def warn(self):
        if not self.warned:
            self.warned = True
            try:
                print('⚠️ Diagnostic logging unavailable or full; posting will continue. Check yappily --logs.', file=sys.stderr)
            except (OSError, ValueError):
                pass

    def __enter__(self):
        self.token = _ACTIVE.set(self)
        try:
            directory = log_directory()
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            directory.chmod(0o700)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            self.path = directory / f'run-{stamp}-{self.run_id}.jsonl'
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            self.file = os.fdopen(fd, 'w', encoding='utf-8')
            # Each invocation has its own file: overlapping CLIs never rotate an
            # active shared handle. Only matching Yappily filenames are pruned.
            for old in run_files(directory)[MAX_RUNS:]:
                try:
                    old.unlink()
                except FileNotFoundError:
                    pass
        except OSError:
            self.warn()
        return self

    def event(self, name, **fields):
        if self.file is None:
            return
        try:
            row = {'schema': 1, 'timestamp': datetime.now(timezone.utc).isoformat(),
                   'run_id': self.run_id, 'event': name, **fields}
            line = json.dumps(row, ensure_ascii=True) + '\n'
            size = len(line.encode('utf-8'))
            if self.bytes_written + size > MAX_BYTES:
                self.warn()
                return
            self.file.write(line)
            self.file.flush()
            self.bytes_written += size
        except (OSError, TypeError, ValueError):
            self.warn()

    def __exit__(self, exc_type, error, tb):
        try:
            if error is not None:
                self.event('run_crashed', **error_details(error))
            if self.file:
                self.file.close()
        except OSError:
            self.warn()
        finally:
            _ACTIVE.reset(self.token)


def run_files(directory):
    return sorted((p for p in directory.glob('run-*.jsonl')
                   if re.fullmatch(r'run-\d{8}T\d{12}Z-[0-9a-f]{32}\.jsonl', p.name)
                   and not p.is_symlink()), reverse=True)


def show_logs(failures_only=False):
    """Print the latest five matching runs, without making any network requests."""
    directory = log_directory()
    print(f'Diagnostic logs: {directory}')
    shown = 0
    try:
        for path in run_files(directory):
            rows = []
            with path.open(encoding='utf-8') as file:
                for line in file:
                    try:
                        row = json.loads(line)
                        if isinstance(row, dict):
                            rows.append(row)
                    except ValueError:
                        continue
            ended = any(row.get('event') == 'run_finished' for row in rows)
            failed = any(row.get('event') in ('platform_failed', 'run_crashed', 'operation_failed')
                         or row.get('exit_code', 0) != 0 for row in rows)
            if failures_only and ended and not failed:
                continue
            print(f'\n{path.name}' + (' (incomplete or still running)' if not ended else ''))
            for row in rows:
                print(json.dumps(row, ensure_ascii=True))
            shown += 1
            if shown == 5:
                break
    except OSError as error:
        print(f'Cannot read diagnostics ({type(error).__name__}).', file=sys.stderr)
        return 1
    if not shown:
        print('No matching runs recorded yet.')
    return 0
