"""Offline integration contracts for the LIVE single-owner support services."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tests import _harness  # noqa: F401 - deterministic test-only signing keys
from services.common import envelope
from services.common.sharia_attestation import RESULT_PURPOSE, attach
from services.sharia_screener.manual_registry import load_manual_registry
from services.sharia_screener.manual_registry_service import ManualRegistryProjector
from services.telegram_broker import bot
from services.universe_service.snapshot_store import load_current, store


ROOT = Path(__file__).resolve().parents[1]


class LiveOwnerServiceParity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry_path = self.root / 'halal_coins.json'
        self.commands = self.root / 'commands'
        self.inbox = self.commands / 'inbox'
        self.results = self.root / 'research/results'
        self.reports = self.root / 'research/reports'
        self.results.mkdir(parents=True)
        self.reports.mkdir(parents=True)
        self.patch = mock.patch.dict('os.environ', {
            'SHARED_ROOT': str(self.root),
            'SHARIA_REGISTRY_COMMAND_ROOT': str(self.commands),
            'SHARIA_RESEARCH_ROOT': str(self.root / 'research'),
            'AUDIT_LOG': str(self.root / 'audit/events.jsonl'),
        })
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.network = mock.patch('requests.sessions.Session.request',
                                  side_effect=AssertionError('network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.write_registry(['ETHUSDT', 'SOLUSDT'])
        self.projector = ManualRegistryProjector(
            registry_path=self.registry_path,
            status_path=self.root / 'status.json',
            reports_dir=self.root / 'projection_reports',
            runtime_dir=self.root / 'runtime',
            alert_outbox=self.root / 'alerts',
        )

    def write_registry(self, symbols):
        now = datetime.now(timezone.utc).date()
        self.registry_path.write_text(json.dumps({
            'schema_version': 1, 'version': 'offline-fixture-1',
            'last_reviewed': now.isoformat(),
            'next_review': (now + timedelta(days=30)).isoformat(),
            'symbols': sorted(symbols),
        }), encoding='utf-8')

    def queue(self, action='REGISTRY_REMOVE', **args):
        self.assertTrue(callable(getattr(bot, 'registry_owner_command', None)),
                        'LIVE broker lacks signed registry-command producer')
        registry = load_manual_registry(self.registry_path)
        gate = SimpleNamespace(registry_sha256=registry.sha256)
        with mock.patch.object(bot, 'SHARIA_REGISTRY_COMMAND_INBOX', self.inbox), \
                mock.patch.object(bot, 'load_sharia_gate', return_value=gate):
            return bot.registry_owner_command(action, {'base': 'ETH', **args})

    def process(self):
        self.assertTrue(callable(getattr(self.projector, 'process_owner_commands', None)),
                        'LIVE projector lacks signed registry-command consumer')
        return self.projector.process_owner_commands()

    def test_signed_remove_is_consumed_once_and_never_calls_network(self):
        command = self.queue()
        self.assertEqual(self.process(), 1)
        self.assertEqual(load_manual_registry(self.registry_path).symbols, ('SOLUSDT',))
        self.assertTrue((self.commands / 'processed' /
                         f'registry_{command["command_id"]}.json').is_file())
        self.assertEqual(self.process(), 0)

    def test_tampered_signature_cannot_mutate_the_registry(self):
        command = self.queue()
        path = self.inbox / f'registry_{command["command_id"]}.json'
        payload = json.loads(path.read_text())
        payload['payload']['base'] = 'SOL'
        path.write_text(json.dumps(payload))
        before = self.registry_path.read_bytes()
        self.assertEqual(self.process(), 0)
        self.assertEqual(self.registry_path.read_bytes(), before)
        self.assertTrue((self.commands / 'rejected' / path.name).exists())

    def test_stale_confirmed_registry_hash_cannot_override_newer_owner_list(self):
        command = self.queue()
        self.write_registry(['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])
        before = self.registry_path.read_bytes()
        self.assertEqual(self.process(), 0)
        self.assertEqual(self.registry_path.read_bytes(), before)
        self.assertTrue((self.commands / 'rejected' /
                         f'registry_{command["command_id"]}.json').exists())

    def test_add_without_verified_research_is_rejected(self):
        self.queue('REGISTRY_ADD', base='BTC', research_request_id='missing',
                   report_sha256='a' * 64)
        before = self.registry_path.read_bytes()
        self.assertEqual(self.process(), 0)
        self.assertEqual(self.registry_path.read_bytes(), before)

    def test_add_requires_signed_result_matching_report_base_and_owner_approval(self):
        report = {'final_code': 'GREEN', 'owner_approval': {'decision': 'APPROVE'}}
        report_path = self.reports / 'report-research-1.json'
        report_path.write_text(json.dumps(report), encoding='utf-8')
        digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
        result = attach({
            'base': 'BTC', 'pair': 'BTC/USDT', 'validated': True,
            'final_code': 'GREEN', 'report_sha256': digest,
            'report_file': report_path.name,
        }, purpose=RESULT_PURPOSE)
        signed = envelope.sign_envelope(producer='sharia-screener',
                                       purpose=envelope.BUS_SHARIA_RESULT,
                                       payload=result, ttl_seconds=600)
        (self.results / 'result_research-1.json').write_text(json.dumps(signed))
        self.queue('REGISTRY_ADD', base='BTC', research_request_id='research-1',
                   report_sha256=digest)
        self.assertEqual(self.process(), 1)
        self.assertEqual(load_manual_registry(self.registry_path).symbols,
                         ('BTCUSDT', 'ETHUSDT', 'SOLUSDT'))

    def test_unknown_action_is_rejected_before_queue_creation(self):
        with self.assertRaises(ValueError):
            self.queue('FORCE_APPROVE')
        self.assertFalse(self.inbox.exists())

    def test_old_root_compose_wires_all_required_projector_bus_keys(self):
        import yaml
        compose = yaml.safe_load((ROOT / 'docker-compose.yml').read_text())
        wired = compose['services']['sharia-screener']['environment']
        with mock.patch.dict('os.environ', {name: 't' * 48 for name in wired}, clear=True):
            for purpose in (envelope.BUS_SHARIA_DECISION, envelope.BUS_SHARIA_RESULT):
                self.assertEqual(len(envelope.load_key(purpose)), 48)

    def test_read_only_fallback_never_hides_mutating_command_outcomes(self):
        self.assertTrue(callable(getattr(bot, '_sidecar_read', None)))
        with mock.patch.object(bot, 'sidecar_command', side_effect=TimeoutError('unavailable')) as bus:
            result = bot._sidecar_read('orders')
            self.assertFalse(result['ok'])
            self.assertTrue(result['no_trading_action_performed'])
            with self.assertRaises(ValueError):
                bot._sidecar_read('resume')
            self.assertEqual(bus.call_count, 1)

    def test_explicit_all_eligible_snapshot_roundtrips_all_members_and_empty_state(self):
        for count in (0, 120, 376):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as raw:
                path = Path(raw)
                rows = [{'pair': f'COIN{i}/USDT', 'rank': i+1} for i in range(count)]
                store(path, rows, {'limit': count, 'limit_mode': 'all_eligible'}, 300)
                loaded = load_current(path / 'current_pairlist.json', require_nonempty=False)
                self.assertEqual(loaded['pairs'], [row['pair'] for row in rows])
                self.assertEqual(loaded['selection']['ready'], count > 0)

    def test_legacy_limit_and_inconsistent_all_eligible_count_stay_rejected(self):
        rows = [{'pair': 'ETH/USDT', 'rank': 1}]
        for config in ({'limit': 120}, {'limit': 2, 'limit_mode': 'all_eligible'},
                       {'limit': 1, 'limit_mode': 'unknown'}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                store(self.root / 'universe', rows, config, 300)


if __name__ == '__main__':
    unittest.main()
