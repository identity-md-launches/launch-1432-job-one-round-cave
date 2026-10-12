#!/usr/bin/env python3
"""Offline regression observations from gathering 01, updated for the round-22
line interfaces in gathering 02; no network calls.

Prints JSON; exit 1 means known producer defects remain, 0 means all checks pass.
Run from workspace root: python3 -B gathering/review_checks.py
"""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    snapshot = load("snapshot", "line-1/tools/rpc-snapshot/rpc_snapshot.py")
    decoder = load("decoder", "line-3/tools/zto-eip1559-decoder/tx_decode.py")
    window = load("window", "line-4/tools/erc20-transfer-window/transfer_window.py")
    checks = []
    # Patch the opener in memory; nothing here can issue a request.
    class Reply:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, *limit): return b"null"
    original_open = snapshot.urllib.request.urlopen
    original_argv = sys.argv
    snapshot.urllib.request.urlopen = lambda *args, **kwargs: Reply()
    sys.argv = ["rpc_snapshot.py"]
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                code = snapshot.main()
                checks.append({"check": "line-1 null JSON response is a controlled error", "passed": code == 1})
            except Exception as error:
                checks.append({"check": "line-1 null JSON response is a controlled error", "passed": False,
                               "observed": type(error).__name__ + ": " + str(error)})
    finally:
        snapshot.urllib.request.urlopen = original_open
        sys.argv = original_argv

    raw = bytes.fromhex(decoder.demo_transaction()[2:])
    fields, _ = decoder.rlp_item(raw, 1)
    fields[1] = b"\x00"
    try:
        result = decoder.decode("02" + decoder.rlp_encode(fields).hex())
        checks.append({"check": "line-3 reject zero encoded as 0x00", "passed": False,
                       "observed_nonce": result["nonce"]})
    except ValueError:
        checks.append({"check": "line-3 reject zero encoded as 0x00", "passed": True})

    source = json.loads(Path("shared/evidence-handoff/examples/transfers.json").read_text())
    event = source["transfers"][0]
    original = {"address": window.TOKENS["zto"],
                "topics": [window.TRANSFER_TOPIC, "0x" + "0"*24 + event["from"][2:],
                           "0x" + "0"*24 + event["to"][2:]],
                "data": "0x" + format(int(event["raw_value"]), "064x"),
                "blockNumber": hex(event["block"]), "logIndex": hex(event["log_index"]),
                "transactionHash": event["transaction_hash"], "removed": False,
                # Round-22 decoder also requires these identity fields.
                "blockHash": "0x" + "ab"*32, "transactionIndex": "0x0"}
    cases = {
        "wrong emitter": {"address": window.TOKENS["imd"]},
        "wrong topic": {"topics": ["0x" + "ff"*32] + original["topics"][1:]},
        "out of range": {"blockNumber": hex(source["from_block"]-1)},
        "removed log": {"removed": True},
        "short uint256": {"data": "0x1"},
        "nonhex address topic": {"topics": original["topics"][:1] + ["0x"+"g"*64] + original["topics"][2:]},
        "duplicate log": {},
    }
    for name, changes in cases.items():
        log = copy.deepcopy(original)
        log.update(changes)
        logs = [log, copy.deepcopy(log)] if name == "duplicate log" else [log]
        def fake_rpc(endpoint, method, params):
            if method == "eth_chainId": return "0x1"
            if method == "eth_blockNumber": return hex(source["head_at_capture"])
            if method == "eth_getBlockByNumber": return {"number": params[0], "hash": original["blockHash"]}
            if method == "eth_call": return "0x" + format(18, "064x")
            if method == "eth_getLogs": return logs
            raise AssertionError("Unexpected method: " + method)
        window.rpc = fake_rpc
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                window.main(["--from-block", str(source["from_block"]), "--to-block", str(source["to_block"])])
            result = json.loads(out.getvalue())
            expected = 1 if name == "duplicate log" else 0
            checks.append({"check": "line-4 handle " + name, "passed": result["transfer_count"] == expected,
                           "observed_count": result["transfer_count"]})
        except window.RpcError:
            checks.append({"check": "line-4 handle " + name, "passed": True})
        except Exception as error:
            checks.append({"check": "line-4 handle " + name, "passed": False,
                           "observed": "uncontrolled " + type(error).__name__})
    return {"network": "disabled by in-memory replacements", "checks": checks,
            "failed": sum(not item["passed"] for item in checks)}


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report["failed"]))
