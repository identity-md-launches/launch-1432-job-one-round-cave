#!/usr/bin/env python3
"""Read a portable RPC snapshot from stdin and summarize it without networking."""
import datetime
import importlib.util
import json
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / 'rpc-snapshot' / 'rpc_snapshot.py'
spec = importlib.util.spec_from_file_location('rpc_snapshot', SOURCE)
rpc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rpc)


def summarize(snapshot):
    if not isinstance(snapshot, dict):
        raise ValueError('snapshot must be an object')
    fields = {'captured_at', 'endpoint', 'method', 'params', 'result'}
    if set(snapshot) != fields:
        raise ValueError('snapshot must have the five capture fields')
    rpc.validate_request(snapshot['method'], snapshot['params'])
    if not isinstance(snapshot['endpoint'], str) or not snapshot['endpoint'].startswith('https://'):
        raise ValueError('expected an HTTPS endpoint')
    captured = snapshot['captured_at']
    if not isinstance(captured, str) or not captured.endswith('Z'):
        raise ValueError('capture time must be UTC with a Z suffix')
    datetime.datetime.fromisoformat(captured[:-1] + '+00:00')
    summary = dict(snapshot)
    summary['evidence_limits'] = 'Provider observation; not proof of authenticity, finality or current state.'
    method = snapshot['method']
    result = snapshot['result']
    if method in {'eth_blockNumber', 'eth_chainId', 'eth_gasPrice', 'eth_getBalance', 'eth_getTransactionCount'}:
        if not rpc.block_tag(result) or not result.startswith('0x'):
            raise ValueError('expected a canonical hex quantity result')
        summary['decimal_result'] = str(int(result, 16))
    return summary


def main():
    try:
        raw = sys.stdin.buffer.read(rpc.MAX_RESPONSE_BYTES + 1)
        if len(raw) > rpc.MAX_RESPONSE_BYTES:
            raise ValueError('snapshot exceeds 4 MiB limit')
        result = summarize(json.loads(raw))
    except (ValueError, UnicodeError) as exc:
        print('snapshot-check: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
