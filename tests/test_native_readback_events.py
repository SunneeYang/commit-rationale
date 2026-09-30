"""Offline event-format regressions. No model, network, or native plugin run."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('native_readback_probe', ROOT / 'benchmarks/native_readback_probe.py')
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def event(kind, item):
    return {'type': kind, 'item': item}


class NativeEventTests(unittest.TestCase):
    def summarize(self, events, returncode=0, extra=''):
        stdout = '\n'.join(json.dumps(value) for value in events) + extra
        result = subprocess.CompletedProcess(['codex'], returncode, stdout, 'synthetic stderr')
        with tempfile.TemporaryDirectory() as directory:
            return probe.summarize(result, Path(directory) / 'absent-output.txt')

    def test_legacy_command_records_full_body_and_explicit_exit(self):
        row = self.summarize([event('item.completed', {
            'type': 'command_execution', 'id': 'c1', 'status': 'completed',
            'command': 'git show -s --format=%B HEAD', 'exit_code': 0,
            'aggregated_output': 'Subject\n\nConstraint\n\nRefs: END\n'})])
        self.assertEqual(row['tool_call_count'], 1)
        self.assertEqual(row['commands'][0]['exit_code'], 0)
        self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], 'reported_exit_zero')
        self.assertIn('Refs: END', row['tool_calls'][0]['result']['value'])
        self.assertIsNone(row['review'])

    def test_completed_mcp_transport_is_not_successful_execution(self):
        row = self.summarize([event('item.completed', {
            'type': 'mcp_tool_call', 'id': 'm1', 'server': 'exec', 'tool': 'exec_command',
            'arguments': {'cmd': 'git show -s --format=%B HEAD'}, 'status': 'completed',
            'result': {'isError': True, 'content': [{'type': 'text', 'text': 'sandbox_apply: Operation not permitted'}]}})])
        self.assertEqual(row['commands'], [])
        self.assertEqual(row['tool_call_count'], 1)
        call = row['tool_calls'][0]
        self.assertEqual(call['input']['value']['cmd'], 'git show -s --format=%B HEAD')
        self.assertTrue(call['completion_event_observed'])
        self.assertEqual(call['execution_evidence']['state'], 'reported_blocked')
        self.assertEqual(row['tool_execution_blocked_count'], 1)
        self.assertEqual(row['exit_code'], 0)
        self.assertEqual(row['unexpected_tool_item_types'], [])

    def test_started_arguments_survive_sparse_completion(self):
        row = self.summarize([
            event('item.started', {'type': 'mcp_tool_call', 'id': 'm1', 'server': 'exec',
                                  'tool': 'exec_command', 'arguments': {'cmd': 'git log'}}),
            event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1', 'status': 'completed',
                                    'result': {'content': [{'type': 'text', 'text': 'history'}]}})])
        self.assertEqual(row['tool_call_count'], 1)
        self.assertEqual(row['tool_calls'][0]['input']['value'], {'cmd': 'git log'})
        self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], 'result_returned_unverified')

    def test_started_only_is_incomplete_and_not_no_tools(self):
        row = self.summarize([event('item.started', {'type': 'mcp_tool_call', 'id': 'm1',
                             'input': {'cmd': 'git log'}, 'status': 'in_progress'})], returncode=124)
        self.assertEqual(row['tool_call_count'], 1)
        self.assertFalse(row['tool_calls'][0]['completion_event_observed'])
        self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], 'incomplete')
        self.assertIsNone(row['startup_error'])

    def test_mcp_explicit_structured_exit_code_and_error(self):
        for key in ('structuredContent', 'structured_content'):
            for code, expected in ((0, 'reported_exit_zero'), (1, 'reported_failed')):
                with self.subTest(key=key, code=code):
                    row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
                        'status': 'completed', 'result': {key: {'exit_code': code}}})])
                    self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], expected)
        for error_field in ('isError', 'is_error'):
            row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
                'status': 'completed', 'result': {error_field: True}})])
            self.assertEqual(row['tool_execution_failed_count'], 1)

    def test_input_mentions_do_not_falsely_mark_execution_blocked(self):
        row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
            'arguments': {'cmd': 'echo "sandbox_apply: Operation not permitted"'},
            'status': 'completed', 'result': {'structuredContent': {'exit_code': 0}}})])
        self.assertEqual(row['tool_execution_blocked_count'], 0)

    def test_capture_truncation_does_not_silently_drop_tail(self):
        row = self.summarize([event('item.completed', {'type': 'command_execution', 'id': 'c1',
            'command': 'git show', 'exit_code': 0, 'aggregated_output': 'x' * 20000 + 'TAIL'}),
            {'type': 'turn.completed'}])
        call = row['tool_calls'][0]
        self.assertTrue(call['capture_truncated'])
        self.assertIsNone(call['result']['value'])
        self.assertEqual(len(call['result']['preview']), probe.CAPTURE_LIMIT)
        self.assertGreater(call['result']['sanitized_chars'], probe.CAPTURE_LIMIT)
        self.assertIsNone(row['commands'][0]['aggregated_output'])
        self.assertIsNone(row['review'])
        self.assertTrue(row['event_trace_complete'])
        self.assertFalse(row['tool_capture_complete'])

    def test_tool_reported_truncation_is_separate_from_capture_truncation(self):
        row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
            'status': 'completed', 'result': {'structuredContent': {'exit_code': 0, 'truncated': True}}}),
            {'type': 'turn.completed'}])
        call = row['tool_calls'][0]
        self.assertTrue(call['execution_evidence']['tool_output_truncation_signal'])
        self.assertFalse(call['capture_truncated'])
        self.assertTrue(row['event_trace_complete'])
        self.assertFalse(row['tool_capture_complete'])

    def test_successful_read_of_historical_error_text_is_not_current_blocker(self):
        row = self.summarize([event('item.completed', {'type': 'command_execution', 'id': 'c1',
            'command': 'git show', 'exit_code': 0,
            'aggregated_output': 'Fixed old sandbox_apply: Operation not permitted failure'})])
        self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], 'reported_exit_zero')
        self.assertTrue(row['tool_calls'][0]['execution_evidence']['sandbox_blocker_signal'])
        self.assertEqual(row['tool_execution_blocked_count'], 0)

    def test_unstructured_error_text_is_only_a_signal_until_reviewed(self):
        row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
            'status': 'completed', 'result': {'content': [{'type': 'text',
                'text': 'sandbox_apply: Operation not permitted'}]}})])
        self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], 'result_returned_unverified')
        self.assertTrue(row['tool_calls'][0]['execution_evidence']['sandbox_blocker_signal'])
        self.assertEqual(row['tool_execution_blocked_count'], 0)

    def test_mcp_zero_exit_with_sandbox_text_remains_unverified(self):
        row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
            'status': 'completed', 'result': {'structuredContent': {'exit_code': 0},
                'content': [{'type': 'text', 'text': 'sandbox_apply: Operation not permitted'}]}})])
        self.assertEqual(row['tool_calls'][0]['execution_evidence']['state'], 'conflicting_signals_unverified')
        self.assertEqual(row['tool_execution_blocked_count'], 0)

    def test_nested_secret_binary_and_reasoning_are_not_saved(self):
        row = self.summarize([event('item.completed', {'type': 'mcp_tool_call', 'id': 'm1',
            'arguments': {'authorization': 'SYNTHETIC_SECRET', 'nested': {'password': 'SYNTHETIC_SECRET'}},
            'result': {'content': [{'type': 'image', 'data': 'SYNTHETIC_BINARY'},
                                   {'type': 'text', 'text': 'Bearer SYNTHETIC_SECRET'}]}}),
            event('item.completed', {'type': 'reasoning', 'text': 'SYNTHETIC_REASONING'})])
        serialized = json.dumps(row)
        for secret in ('SYNTHETIC_SECRET', 'SYNTHETIC_BINARY', 'SYNTHETIC_REASONING'):
            self.assertNotIn(secret, serialized)
        self.assertIn('[REDACTED]', serialized)

    def test_json_encoded_input_credentials_are_redacted(self):
        captured = probe.capture('{"api_key":"SYNTHETIC_SECRET","cmd":"git log"}')
        self.assertNotIn('SYNTHETIC_SECRET', json.dumps(captured))
        self.assertIn('git log', json.dumps(captured))

    def test_malformed_or_unknown_events_make_capture_incomplete(self):
        row = self.summarize([event('item.completed', {'type': 'future_tool_format', 'id': 'x'})], extra='\n{"partial":')
        self.assertEqual(row['malformed_event_lines'], 1)
        self.assertFalse(row['tool_capture_complete'])
        self.assertEqual(row['unexpected_tool_item_types'], ['future_tool_format'])

    def test_translation_with_no_tools_has_explicit_zero_count(self):
        row = self.summarize([event('item.completed', {'type': 'agent_message', 'text': 'Hello, world'}),
                              {'type': 'turn.completed'}])
        self.assertEqual(row['tool_call_count'], 0)
        self.assertEqual(row['output'], 'Hello, world')
        self.assertTrue(row['tool_capture_complete'])

    def test_empty_or_unfinished_log_cannot_certify_no_tools(self):
        for events in ([], [event('item.started', {'type': 'mcp_tool_call', 'id': 'm1'}),
                           {'type': 'turn.failed', 'error': 'interrupted'}]):
            row = self.summarize(events)
            self.assertFalse(row['tool_capture_complete'])

    def test_app_server_spelling_is_distinguished_from_cli_spelling(self):
        row = self.summarize([event('item.completed', {'type': 'mcpToolCall', 'id': 'm1',
            'server': 'exec', 'tool': 'exec_command', 'arguments': {'cmd': 'git log'},
            'status': 'failed', 'error': {'message': 'sandbox_apply: Operation not permitted'},
            'result': None})])
        call = row['tool_calls'][0]
        self.assertEqual(call['source_item_type'], 'mcpToolCall')
        self.assertEqual(call['type'], 'mcp_tool_call')
        self.assertEqual(call['execution_evidence']['state'], 'reported_blocked')
        self.assertEqual(call['error']['value']['message'], 'sandbox_apply: Operation not permitted')


if __name__ == '__main__':
    unittest.main()
