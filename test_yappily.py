"""Offline tests: every network boundary is mocked."""
import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
import buffer_client as b
from cli_utils import parse_args
import main


class CliTests(unittest.TestCase):
    def test_original_text(self):
        self.assertEqual(parse_args(['Hello', 'world']).text, ['Hello', 'world'])

    def test_only(self):
        self.assertEqual(parse_args(['--only', 'x,bluesky', 'Hello']).only, ['x', 'bluesky'])

    def test_invalid_args(self):
        for args in ([], ['--only', 'wrong', 'Hi'], ['--only', '', 'Hi'], ['--check-buffer', 'Hi'], ['--setup-buffer', '--only', 'x']):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parse_args(args)

    def test_literal_option(self):
        self.assertEqual(parse_args(['--', '--check-buffer']).text, ['--check-buffer'])


class BufferTests(unittest.TestCase):
    def test_request(self):
        response = Mock(status_code=200)
        response.json.return_value = {'data': {'ok': True}}
        with patch.object(b.requests, 'post', return_value=response) as post:
            self.assertEqual(b.request('test-key', 'query {}'), {'ok': True})
            self.assertEqual(post.call_args.kwargs['headers'], {'Authorization': 'Bearer test-key'})
            self.assertFalse(post.call_args.kwargs['allow_redirects'])
            self.assertEqual(post.call_args.kwargs['timeout'], (10, 30))

    def test_http_and_graphql_errors(self):
        for status, payload in ((401, {}), (429, {}), (500, {}), (200, {'errors': [{'message': 'secret'}]}), (200, []), (200, {})):
            response = Mock(status_code=status)
            response.json.return_value = payload
            with self.subTest(status=status, payload=payload), patch.object(b.requests, 'post', return_value=response), self.assertRaises(b.BufferError) as error:
                b.request('secret', 'query {}')
            self.assertNotIn('secret', str(error.exception))

    def test_timeout_not_retried(self):
        with patch.object(b.requests, 'post', side_effect=requests.Timeout('secret')) as post, self.assertRaises(b.BufferError):
            b.request('secret', 'mutation {}')
        post.assert_called_once()

    def test_wrong_channel(self):
        with patch.object(b, 'request', return_value={'channel': {'id': 'c', 'service': 'bluesky'}}), self.assertRaises(b.BufferError):
            b.validate_channel('key', 'c')

    def test_post_statuses_and_payload(self):
        for status in ('sent', 'scheduled', 'error', 'draft', 'notSent'):
            with self.subTest(status=status), patch.object(b, 'get_config', return_value=('key', 'c')), patch.object(b, 'validate_channel'), patch.object(b, 'request', return_value={'createPost': {'__typename': 'PostActionSuccess', 'post': {'id': 'p', 'status': status}}}) as request, contextlib.redirect_stdout(io.StringIO()) as output:
                if status in ('error', 'draft', 'notSent'):
                    with self.assertRaises(b.BufferError):
                        b.send_tweet('Hello', Path('.'))
                else:
                    self.assertTrue(b.send_tweet('Hello', Path('.')))
                    if status == 'scheduled':
                        self.assertIn('not confirmed', output.getvalue())
                payload = request.call_args.args[2]['input']
                self.assertEqual(payload['mode'], 'shareNow')
                self.assertEqual(payload['text'], 'Hello')
                self.assertEqual(payload['channelId'], 'c')
                self.assertFalse(payload['needsApproval'])
                request.assert_called_once()

    def test_typed_rejection(self):
        with patch.object(b, 'get_config', return_value=('secret', 'c')), patch.object(b, 'validate_channel'), patch.object(b, 'request', return_value={'createPost': {'__typename': 'SomeError', 'message': 'bad secret'}}), self.assertRaises(b.BufferError) as error:
            b.send_tweet('Hi', Path('.'))
        self.assertNotIn('secret', str(error.exception))

    def test_check_is_read_only(self):
        with patch.object(b, 'get_config', return_value=('key', 'c')), patch.object(b, 'request', return_value={'channel': {'id': 'c', 'service': 'twitter', 'name': 'test'}}) as request, contextlib.redirect_stdout(io.StringIO()):
            b.check_buffer(Path('.'))
        self.assertEqual(request.call_args.args[1], b.CHANNEL_QUERY)

    def test_config_and_setup(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            root = Path(directory)
            with self.assertRaises(b.BufferError):
                b.get_config(root)
            with patch.object(b.getpass, 'getpass', return_value=' test-key\n'), patch('builtins.input', return_value='1'), patch.object(b, 'request', side_effect=[{'account': {'organizations': [{'id': 'o', 'name': 'Org'}]}}, {'channels': [{'id': 'c', 'name': 'X', 'service': 'twitter'}]}]), patch.object(b, 'validate_channel'), contextlib.redirect_stdout(io.StringIO()):
                b.setup_buffer(root)
            self.assertEqual(b.get_config(root), ('test-key', 'c'))
            self.assertEqual((root / 'buffer_creds/api_key.txt').stat().st_mode & 0o777, 0o600)
            self.assertEqual((root / 'buffer_creds').stat().st_mode & 0o777, 0o700)
            with patch.dict(os.environ, {'BUFFER_API_KEY': 'env-key'}):
                self.assertEqual(b.get_config(root)[0], 'env-key')


class MainTests(unittest.TestCase):
    def test_failure_does_not_stop_others(self):
        with patch.object(main, 'send_tweet', side_effect=b.BufferError('test failure')), patch('hachyderm.post_to_hachyderm') as h, patch('bluesky.post_to_bluesky') as sky, contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main.main(['Hello']), 1)
            h.assert_called_once()
            sky.assert_called_once()
            self.assertIn('--only x', out.getvalue())

    def test_only_x(self):
        with patch.object(main, 'send_tweet') as x, patch('hachyderm.post_to_hachyderm') as h, patch('bluesky.post_to_bluesky') as sky, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--only', 'x,x', 'Hello']), 0)
            x.assert_called_once()
            h.assert_not_called()
            sky.assert_not_called()

    def test_unselected_broken_sdk_does_not_block_x(self):
        with patch.dict('sys.modules', {'bluesky': None, 'hachyderm': None}), patch.object(main, 'send_tweet') as tweet, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['--only', 'x', 'Hello']), 0)
            tweet.assert_called_once()

    def test_broken_sdk_does_not_block_other_platforms(self):
        with patch.dict('sys.modules', {'hachyderm': None}), patch.object(main, 'send_tweet') as tweet, patch('bluesky.post_to_bluesky') as sky, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(['Hello']), 1)
            tweet.assert_called_once()
            sky.assert_called_once()

    def test_check_routes_without_post(self):
        with patch.object(main, 'check_buffer') as check, patch.object(main, 'send_tweet') as tweet:
            self.assertEqual(main.main(['--check-buffer']), 0)
            check.assert_called_once()
            tweet.assert_not_called()


if __name__ == '__main__':
    unittest.main()
