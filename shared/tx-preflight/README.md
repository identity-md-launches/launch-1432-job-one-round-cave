# Tx preflight

Before a person signs an unsigned EIP-1559 transaction, check it against the
chain as it is now. `preflight.py` decodes the envelope with Line 3's decoder,
then makes read-only reads through Line 1's allowlisted request and response
validators. Every read is pinned to one block and kept as a Line 1 snapshot.
It reports `pass`, `warn` or `fail` for each check:

- the transaction's chain ID matches the endpoint's chain
- fee order, `maxFeePerGas` against the pinned block's base fee, and gas limit
- the destination has code when calldata is sent
- known ERC-20 calls (`transfer`, `approve`, `transferFrom`) are decoded
  strictly, with amounts in token units using on-chain `decimals()`
- a transfer to the token itself, the Uniswap v4 PoolManager or the zero
  address is refused, because a plain transfer there cannot be recovered
- with `--from`: the nonce matches the account's next nonce, there is enough
  ETH for value plus worst-case gas, and the token balance/allowance covers the
  call

ZTO and IMD are named when they appear. Python 3 standard library only. It never
signs, sends, or reads keys, wallets or environment variables. Exit codes: 0
means pass or warn, 3 means at least one check failed, 1 means a controlled
error (bad input, missing evidence, network).

## See it working (offline)

```sh
python3 -B shared/tx-preflight/preflight.py demo
```

This replays `examples/zto-transfer-evidence.json`: eight real PublicNode reads
captured on 2026-10-12 at 15:45:34Z, pinned to block 26177373. The demo transaction is
an unsigned transfer of 1 ZTO from a real ZTO holder
(`0xe6ea…d265`) back to itself, using that account's real next nonce, 3056.
All seven checks pass. The holder had 200,000 ZTO and 0.0016 ETH at that block.

```sh
python3 -B shared/tx-preflight/test_preflight.py
```

There are 11 offline tests, all passing. They use the same recorded evidence and
check these cases: a stale nonce, gas the account cannot afford, the wrong chain,
transfers to the PoolManager or the token itself, an amount above the balance,
malformed ABI words, missing evidence (an error, never a guess), every record
passing Line 1's `snapshot-check`, and signing methods refused before any
network call.

## Live use

```sh
python3 -B shared/tx-preflight/preflight.py check 0x02... --from 0xSIGNER
python3 -B shared/tx-preflight/preflight.py check demo --from 0xe6ea861295af4e0d0d7f331c7b950f7da3a9d265
```

What happened when I tried it live: the first draft of the demo used nonce 0 and a
30 gwei max fee. The preflight correctly failed it twice: the account's next nonce was 3056,
and it held 0.0016 ETH against 0.0024 ETH worst-case gas. After those
two fixes it passed, and that run was recorded as the example. `--replay FILE`
answers reads from any saved list of snapshots. The `evidence` array in each
report has that same shape, so a report can be re-checked later without a
network.

## Limits

These are observations from one provider at one block. They are not a simulation:
Line 1's `eth_call` allows only `to` and `data`, so calls are not run as the
sender. It does not check token-specific transfer rules, contract behaviour or
inclusion, and it gives no assurance that the transaction is safe to sign.
`preflight.py` imports the two line tools from `line-1/` and `line-3/` by path,
so keep the repository layout.
