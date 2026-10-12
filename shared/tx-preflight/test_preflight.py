#!/usr/bin/env python3
"""Offline tests: recorded live ZTO evidence is replayed; no request leaves the machine."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight as pf

HERE = Path(__file__).resolve().parent
RECORDS = json.loads((HERE / "examples" / "zto-transfer-evidence.json").read_text())
HOLDER = "0xe6ea861295af4e0d0d7f331c7b950f7da3a9d265"
ZTO = "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e"


def tx(nonce=3056, max_fee=2_000_000_000, to=ZTO, data=None, chain=1, value=0):
    if data is None:
        data = "a9059cbb" + pf.word(HOLDER[2:]) + pf.word(format(10**18, "x"))
    fields = [chain, nonce, 1_000_000_000, max_fee, 60_000, bytes.fromhex(to[2:]), value, bytes.fromhex(data), []]
    return "0x02" + pf.decoder.rlp_encode(fields).hex()


def status(report, name):
    return [c["status"] for c in report["checks"] if c["check"] == name]


class Preflight(unittest.TestCase):
    def run_tx(self, raw, sender=HOLDER, records=RECORDS):
        return pf.preflight(raw, pf.Replay(copy.deepcopy(records)), sender)

    def test_demo_passes_on_recorded_live_state(self):
        report = self.run_tx(pf.demo_transaction())
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["call"]["function"], "transfer")
        self.assertEqual(report["token"]["symbol"], "ZTO")
        self.assertEqual(report["token"]["decimals"], 18)

    def test_stale_nonce_and_unaffordable_gas_fail(self):
        report = self.run_tx(tx(nonce=0, max_fee=30_000_000_000))
        self.assertEqual(report["verdict"], "fail")
        self.assertEqual(status(report, "nonce"), ["fail"])
        self.assertEqual(status(report, "ETH for value and gas"), ["fail"])

    def test_wrong_chain_fails(self):
        self.assertEqual(status(self.run_tx(tx(chain=11155111)), "chain"), ["fail"])

    def test_unrecoverable_recipient_fails(self):
        for recipient in (pf.POOL_MANAGER, ZTO):
            data = "a9059cbb" + pf.word(recipient[2:]) + pf.word("1")
            with self.subTest(recipient=recipient):
                self.assertEqual(status(self.run_tx(tx(data=data)), "recipient"), ["fail"])

    def test_more_than_balance_fails(self):
        data = "a9059cbb" + pf.word(HOLDER[2:]) + pf.word(format(10**30, "x"))
        self.assertEqual(status(self.run_tx(tx(data=data)), "token balance"), ["fail"])

    def test_malformed_erc20_calldata_is_refused(self):
        for data in ("a9059cbb" + "00" * 63, "a9059cbb" + "11" * 32 + "00" * 32):
            with self.subTest(data=data[:12]), self.assertRaises(ValueError):
                self.run_tx(tx(data=data))

    def test_without_sender_warns(self):
        report = self.run_tx(pf.demo_transaction(), sender=None)
        self.assertEqual(report["verdict"], "warn")

    def test_missing_evidence_is_an_error_not_a_guess(self):
        with self.assertRaises(ValueError):
            self.run_tx(pf.demo_transaction(), records=RECORDS[:3])

    def test_evidence_records_pass_line1_snapshot_check(self):
        checker = pf.load("check_snapshot", "line-1/tools/snapshot-check/check_snapshot.py")
        for record in RECORDS:
            checker.summarize(record)

    def test_live_transport_refuses_signing_methods_before_network(self):
        live = pf.Live("https://example.invalid")
        with mock.patch.object(pf.urllib.request, "urlopen") as network:
            for method in ("eth_sendRawTransaction", "eth_sign", "personal_sign"):
                with self.assertRaises(ValueError):
                    live(method, ["0x00"])
            network.assert_not_called()

    def test_cli_demo_exit_zero(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(pf.main(["demo"]), 0)
        self.assertEqual(json.loads(out.getvalue())["verdict"], "pass")


if __name__ == "__main__":
    unittest.main(verbosity=1)
