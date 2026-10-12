#!/usr/bin/env python3
"""Check an unsigned EIP-1559 transaction against live public chain state.

Glue between two lines: Line 3's offline decoder reads the envelope, and Line 1's
read-only request/response validators guard every chain read.  Each read is kept
as a Line 1 snapshot, so the evidence can be re-checked offline later with
line-1/tools/snapshot-check or replayed here with --replay.

Never signs, sends, or reads keys, wallets, environment variables or files
outside the paths given on the command line.
"""
import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
USER_AGENT = "Pepeolithic-Tx-Preflight/1.0 (read-only public data)"
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
TOKENS = {
    "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e": "ZTO",
    "0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7": "IMD",
}
POOL_MANAGER = "0x000000000004444c5dc75cb358380d2e3de08a90"
SELECTORS = {  # name, argument kinds
    "0xa9059cbb": ("transfer", ("address", "uint256")),
    "0x095ea7b3": ("approve", ("address", "uint256")),
    "0x23b872dd": ("transferFrom", ("address", "address", "uint256")),
}
UNLIMITED = 2**256 - 1


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


decoder = load("tx_decode", "line-3/tools/zto-eip1559-decoder/tx_decode.py")
snapshot = load("rpc_snapshot", "line-1/tools/rpc-snapshot/rpc_snapshot.py")


def word(value):
    return "0" * (64 - len(value)) + value


def address_arg(address):
    return word(address[2:].lower())


def decode_call(data):
    """Strictly decode a known ERC-20 call; return None for anything else."""
    item = SELECTORS.get(data[:10])
    if item is None:
        return None
    name, kinds = item
    body = data[10:]
    if len(body) != 64 * len(kinds):
        raise ValueError(name + " calldata must be exactly %d ABI words" % len(kinds))
    args = []
    for index, kind in enumerate(kinds):
        chunk = body[64 * index:64 * (index + 1)]
        if kind == "address":
            if chunk[:24] != "0" * 24:
                raise ValueError(name + " address argument has nonzero padding")
            args.append("0x" + chunk[24:].lower())
        else:
            args.append(int(chunk, 16))
    return {"function": name, "args": args}


class Live:
    """Read-only transport; every request passes Line 1's allowlist first."""

    def __init__(self, endpoint):
        if not endpoint.startswith("https://"):
            raise ValueError("RPC endpoint must use HTTPS")
        self.endpoint = endpoint
        self.evidence = []

    def __call__(self, method, params):
        snapshot.validate_request(method, params)
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
        request = urllib.request.Request(self.endpoint, data=body, headers={
            "Content-Type": "application/json", "User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise RuntimeError("response exceeds 4 MiB limit")
        result = snapshot.validate_response(json.loads(raw.decode("utf-8")))
        self.evidence.append({
            "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "endpoint": self.endpoint, "method": method, "params": params, "result": result})
        return result


class Replay:
    """Answer reads from recorded Line 1 snapshots; never touches a network."""

    def __init__(self, records):
        if not isinstance(records, list):
            raise ValueError("replay evidence must be a JSON list of snapshots")
        self.records = records
        self.evidence = []

    def __call__(self, method, params):
        snapshot.validate_request(method, params)
        for record in self.records:
            if record.get("method") == method and record.get("params") == params:
                self.evidence.append(record)
                return record["result"]
        raise ValueError("no recorded snapshot for %s %s" % (method, json.dumps(params)))


def quantity(value, name):
    if not isinstance(value, str) or not snapshot.block_tag(value) or not value.startswith("0x"):
        raise ValueError(name + " is not a hex quantity")
    return int(value, 16)


def uint_word(value, name):
    if not snapshot.hex_data(value, 32):
        raise ValueError(name + " is not one 32-byte ABI word")
    return int(value, 16)


def units(raw, decimals):
    whole, fraction = divmod(raw, 10**decimals)
    return str(whole) + ("." + str(fraction).zfill(decimals).rstrip("0") if fraction else "")


def preflight(tx_hex, rpc, sender=None):
    tx = decoder.decode(tx_hex)
    checks = []

    def check(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    chain_id = quantity(rpc("eth_chainId", []), "chain ID")
    check("chain", "pass" if chain_id == tx["chainId"] else "fail",
          "transaction chainId %d, endpoint chain %d" % (tx["chainId"], chain_id))
    head = quantity(rpc("eth_blockNumber", []), "head")
    pin = hex(head)  # every later read is pinned to this block
    block = rpc("eth_getBlockByNumber", [pin, False])
    if not isinstance(block, dict) or quantity(block.get("number"), "block number") != head:
        raise ValueError("pinned block unavailable")
    base_fee = quantity(block.get("baseFeePerGas"), "baseFeePerGas")
    if tx["maxPriorityFeePerGas"] > tx["maxFeePerGas"]:
        check("fee order", "fail", "maxPriorityFeePerGas exceeds maxFeePerGas")
    check("fee vs base fee", "pass" if tx["maxFeePerGas"] >= base_fee else "warn",
          "maxFeePerGas %d wei, base fee at block %d is %d wei" % (tx["maxFeePerGas"], head, base_fee))
    gas_limit = quantity(block.get("gasLimit"), "block gasLimit")
    check("gas limit", "pass" if 21000 <= tx["gasLimit"] <= gas_limit else "fail",
          "gasLimit %d (block limit %d)" % (tx["gasLimit"], gas_limit))
    target = tx["to"]
    call = None
    token = None
    if target is None:
        check("destination", "warn", "contract creation: no destination to inspect")
    else:
        code = rpc("eth_getCode", [target, pin])
        has_code = isinstance(code, str) and code not in ("0x", "0x0")
        if tx["data"] != "0x" and not has_code:
            check("destination", "fail", "calldata sent to an address with no code")
        else:
            check("destination", "pass", ("contract" if has_code else "account without code")
                  + (" (%s)" % TOKENS[target] if target in TOKENS else ""))
        call = decode_call(tx["data"])
        if call is not None and has_code:
            decimals = uint_word(rpc("eth_call", [{"to": target, "data": "0x313ce567"}, pin]), "decimals()")
            if decimals > 255:
                raise ValueError("decimals() exceeds uint8")
            token = {"address": target, "symbol": TOKENS.get(target), "decimals": decimals}
            amount = call["args"][-1]
            call["amount_units"] = "unlimited" if amount == UNLIMITED else units(amount, decimals)
            recipient = call["args"][-2]
            if call["function"] != "approve" and recipient in (target, POOL_MANAGER, "0x" + "0" * 40):
                check("recipient", "fail", "tokens would go to %s, where a plain transfer is not recoverable" % recipient)
            if call["function"] == "approve" and amount == UNLIMITED:
                check("allowance size", "warn", "approves an unlimited amount to " + recipient)
    if tx["value"] and call is not None:
        check("value", "warn", "ETH value attached to an ERC-20 call")
    if sender is not None:
        sender = sender.lower()
        if not snapshot.hex_data(sender, 20):
            raise ValueError("--from must be a 20-byte hex address")
        nonce = quantity(rpc("eth_getTransactionCount", [sender, pin]), "nonce")
        check("nonce", "pass" if tx["nonce"] == nonce else "fail",
              "transaction nonce %d, account's next nonce %d at block %d" % (tx["nonce"], nonce, head))
        balance = quantity(rpc("eth_getBalance", [sender, pin]), "balance")
        worst = tx["value"] + tx["gasLimit"] * tx["maxFeePerGas"]
        check("ETH for value and gas", "pass" if balance >= worst else "fail",
              "needs up to %s ETH, has %s ETH" % (units(worst, 18), units(balance, 18)))
        if token is not None:
            owner = call["args"][0] if call["function"] == "transferFrom" else sender
            held = uint_word(rpc("eth_call", [{"to": target, "data": "0x70a08231" + address_arg(owner)}, pin]),
                             "balanceOf()")
            if call["function"] in ("transfer", "transferFrom"):
                check("token balance", "pass" if held >= call["args"][-1] else "fail",
                      "%s holds %s, call moves %s" % (owner, units(held, token["decimals"]), call["amount_units"]))
            spender = call["args"][0] if call["function"] == "approve" else sender
            if call["function"] != "transfer":
                holder = sender if call["function"] == "approve" else owner
                allowed = uint_word(rpc("eth_call", [{"to": target, "data": "0xdd62ed3e"
                                                      + address_arg(holder) + address_arg(spender)}, pin]), "allowance()")
                if call["function"] == "transferFrom":
                    check("allowance", "pass" if allowed >= call["args"][-1] else "fail",
                          "allowance %s" % units(allowed, token["decimals"]))
                else:
                    check("current allowance", "pass", "replaces allowance %s" % units(allowed, token["decimals"]))
    else:
        check("sender", "warn", "no --from given: nonce and balances were not checked")
    worst = "fail" if any(c["status"] == "fail" for c in checks) else (
        "warn" if any(c["status"] == "warn" for c in checks) else "pass")
    return {"format": "tx-preflight-v1", "verdict": worst, "block": head, "transaction": tx,
            "call": call, "token": token, "checks": checks, "evidence": rpc.evidence,
            "limits": "Read-only observations at one block from one provider; not a simulation, "
                      "not proof of inclusion, and not advice that the transaction is safe to sign."}


def demo_transaction(nonce=3056, max_fee=2_000_000_000):
    """Unsigned ZTO transfer of 1 ZTO from a real ZTO holder back to itself.

    Nonce 3056 was that account's next nonce at block 26177373 (2026-10-12).
    """
    holder = bytes.fromhex("e6ea861295af4e0d0d7f331c7b950f7da3a9d265")
    data = bytes.fromhex("a9059cbb" + word(holder.hex()) + word(format(10**18, "x")))
    fields = [1, nonce, 1_000_000_000, max_fee, 60_000, bytes.fromhex("d782bdea4ef02a0bd391eb9089470c8080f0a68e"), 0, data, []]
    return "0x02" + decoder.rlp_encode(fields).hex()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="replay the recorded live ZTO evidence offline")
    run = sub.add_parser("check", help="check one unsigned 0x02 transaction")
    run.add_argument("transaction", help="unsigned EIP-1559 hex, or 'demo' for the built-in ZTO transfer")
    run.add_argument("--from", dest="sender", help="the address that would sign (read-only checks)")
    run.add_argument("--rpc", default=snapshot.DEFAULT_RPC, help="public HTTPS JSON-RPC endpoint")
    run.add_argument("--replay", help="JSON list of Line 1 snapshots to answer reads offline")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            records = json.loads((HERE / "examples" / "zto-transfer-evidence.json").read_text())
            sender = "0xe6ea861295af4e0d0d7f331c7b950f7da3a9d265"
            report = preflight(demo_transaction(), Replay(records), sender)
        else:
            tx = demo_transaction() if args.transaction == "demo" else args.transaction
            if args.replay:
                rpc = Replay(json.loads(Path(args.replay).read_text()))
            else:
                rpc = Live(args.rpc)
            report = preflight(tx, rpc, args.sender)
    except (ValueError, RuntimeError, OSError, urllib.error.URLError, RecursionError) as exc:
        print("tx-preflight: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 3 if report["verdict"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
