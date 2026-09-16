"""Diagnostic privacy, retention, and failure-isolation regression tests."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import diagnostics as d
import buffer_client as b
import main
from cli_utils import parse_args


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        env = patch.dict(os.environ, {'YAPPILY_LOG_DIR': str(self.root)})
        env.start()
        self.addCleanup(env.stop)

    def rows(self):
        return [json.loads(line) for file in d.run_files(self.root) for line in file.read_text().splitlines()]

    def test_private_permissions_and_complete_run(self):
        with patch.object(main, 'check_buffer'), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--check-buffer']), 0)
        rows = self.rows()
        self.assertEqual(rows[0]['event'], 'run_started')
        self.assertEqual(rows[-1]['event'], 'run_finished')
        self.assertEqual(rows[-1]['exit_code'], 0)
        self.assertEqual(len({r['run_id'] for r in rows}), 1)
        self.assertIn('packages', rows[0])
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        self.assertEqual(d.run_files(self.root)[0].stat().st_mode & 0o777, 0o600)

    def test_sensitive_exception_and_post_not_recorded(self):
        secret = 'secret-token-123'
        text = 'private unposted thought'
        error = RuntimeError(f'Authorization: Bearer {secret}; body={text}')
        with patch.object(main, 'send_tweet', side_effect=error), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--only', 'x', text]), 1)
        raw = d.run_files(self.root)[0].read_text()
        self.assertNotIn(secret, raw)
        self.assertNotIn(text, raw)
        failure = next(r for r in self.rows() if r['event'] == 'platform_failed')
        self.assertEqual(failure['error_type'], 'RuntimeError')
        self.assertTrue(failure['frames'])
        self.assertNotIn('message', failure)

    def test_buffer_402_and_graphql_diagnostics(self):
        for status, payload in ((402, {}), (200, {'errors': [{'message': 'credits depleted private-text secret-token', 'extensions': {'code': 'CREDITS_DEPLETED'}}]})):
            response = Mock(status_code=status, headers={'x-request-id': 'req-123', 'Authorization': 'secret-token'})
            response.json.return_value = payload
            with d.RunLog(), patch.object(b.requests, 'post', return_value=response), self.assertRaises(b.BufferError):
                b.request('secret-token', b.CREATE_POST_MUTATION, {'input': {'text': 'private-text'}})
        raw = ''.join(p.read_text() for p in d.run_files(self.root))
        self.assertNotIn('secret-token', raw)
        self.assertNotIn('private-text', raw)
        self.assertTrue(any(r.get('http_status') == 402 for r in self.rows()))
        self.assertIn('CREDITS_DEPLETED', raw)
        self.assertIn('billing', raw)
        self.assertIn('req-123', raw)

    def test_retention_only_removes_owned_files(self):
        unrelated = self.root / 'notes.jsonl'
        unrelated.write_text('leave this alone')
        with patch.object(d, 'MAX_RUNS', 2):
            for _ in range(4):
                with d.RunLog() as log:
                    log.event('run_finished', exit_code=0)
        self.assertEqual(len(d.run_files(self.root)), 2)
        self.assertTrue(unrelated.exists())

    def test_byte_cap(self):
        with patch.object(d, 'MAX_BYTES', 250), contextlib.redirect_stderr(io.StringIO()):
            with d.RunLog() as log:
                for _ in range(100):
                    log.event('test')
        self.assertLessEqual(d.run_files(self.root)[0].stat().st_size, 250)

    def test_log_creation_failure_does_not_block_post(self):
        with patch.object(d.os, 'open', side_effect=PermissionError), patch.object(main, 'send_tweet') as send, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as out:
            self.assertEqual(main.main(['--only', 'x', 'hi']), 0)
            send.assert_called_once()
            self.assertIn('logging unavailable', out.getvalue())

    def test_write_failure_does_not_raise(self):
        with d.RunLog() as log, contextlib.redirect_stderr(io.StringIO()):
            with patch.object(log.file, 'write', side_effect=OSError):
                log.event('test')
            self.assertTrue(log.warned)

    def test_incomplete_and_failed_run_filtering(self):
        with d.RunLog() as log:
            log.event('run_finished', exit_code=0)
        with d.RunLog() as log:
            log.event('run_started')
        with d.RunLog() as log:
            log.event('run_finished', exit_code=1)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(d.show_logs(failures_only=True), 0)
        self.assertIn('incomplete', output.getvalue())
        self.assertNotIn('"exit_code": 0', output.getvalue())
        self.assertIn('"exit_code": 1', output.getvalue())

    def test_logs_command_no_run_or_network(self):
        with patch.object(main, 'send_tweet') as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--logs']), 0)
            self.assertEqual(main.main(['--failures']), 0)
        send.assert_not_called()
        self.assertEqual(d.run_files(self.root), [])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args(['--logs', 'accidental post'])

    def test_interrupt_has_stack_without_message(self):
        with self.assertRaises(KeyboardInterrupt):
            with d.RunLog():
                raise KeyboardInterrupt('secret')
        rows = self.rows()
        self.assertEqual(rows[-1]['event'], 'run_crashed')
        self.assertNotIn('secret', json.dumps(rows))
        self.assertIsNone(d._ACTIVE.get())

    def test_metadata_permission_error_does_not_block(self):
        with patch.object(d, 'version', side_effect=PermissionError), patch.object(main, 'send_tweet') as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--only', 'x', 'hi']), 0)
            send.assert_called_once()
        self.assertEqual(self.rows()[0]['packages']['requests'], 'unavailable')

    def test_runtime_enrichment_failure_does_not_block(self):
        with patch.object(main, 'runtime_details', side_effect=ValueError), patch.object(main, 'send_tweet') as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--only', 'x', 'hi']), 0)
            send.assert_called_once()

    def test_warning_stderr_failure_does_not_raise(self):
        with patch.object(d.sys, 'stderr') as stderr:
            stderr.write.side_effect = OSError
            d.RunLog().warn()

    def test_identifiers_exclude_urls(self):
        self.assertIsNone(d.identifier('https://example.com/secret'))
        self.assertEqual(d.identifier('req-123'), 'req-123')

    def test_numeric_status_extraction(self):
        error = RuntimeError('private', 403)
        self.assertEqual(d.error_details(error)['http_status'], 403)


if __name__ == '__main__':
    unittest.main()
