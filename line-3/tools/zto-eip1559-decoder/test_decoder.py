#!/usr/bin/env python3
"""Offline behavioral regressions; no network, file inputs or signing."""
import contextlib
import io
import random
import unittest

import tx_decode as decoder


def payload():
    return [1, 0, 1_000_000_000, 2_000_000_000, 100_000,
            bytes.fromhex(decoder.ZTO[2:]), 0, bytes.fromhex('18160ddd'), []]


def envelope(fields):
    return '0x02' + decoder.rlp_encode(fields).hex()


class DecoderTests(unittest.TestCase):
    def test_real_zto_address_demo(self):
        result = decoder.decode(decoder.demo_transaction())
        self.assertEqual(result['chainId'], 1)
        self.assertEqual(result['nonce'], 0)
        self.assertEqual(result['to'], decoder.ZTO)
        self.assertEqual(result['calldataSelector'], '0x18160ddd')
        self.assertEqual(result['accessList'], [])

    def test_gathering_single_zero_reproduction(self):
        for index in (0, 1, 2, 3, 4, 6):
            for invalid in (b'\x00', b'\x00\x01'):
                fields = payload()
                fields[index] = invalid
                with self.subTest(index=index, invalid=invalid):
                    with self.assertRaisesRegex(ValueError, 'invalid'):
                        decoder.decode(envelope(fields))

    def test_empty_zero_and_canonical_integer_roundtrips(self):
        rng = random.Random(737)
        for value in [0, 1, 127, 128, 255, 256, 2**256-1] + [rng.getrandbits(256) for _ in range(100)]:
            fields = payload()
            fields[1] = value
            self.assertEqual(decoder.decode(envelope(fields))['nonce'], value)

    def test_zero_bytes_remain_valid_in_calldata(self):
        fields = payload()
        fields[7] = b'\x00'
        self.assertEqual(decoder.decode(envelope(fields))['data'], '0x00')

    def test_contract_creation_and_access_list(self):
        fields = payload()
        fields[5] = b''
        fields[8] = [[bytes.fromhex(decoder.ZTO[2:]), [bytes(32)]]]
        result = decoder.decode(envelope(fields))
        self.assertIsNone(result['to'])
        self.assertEqual(result['accessList'][0]['storageKeys'], ['0x' + '00'*32])

    def test_signed_envelope_and_trailing_bytes_rejected(self):
        for transaction in (envelope(payload()+[0, 1, 1]), decoder.demo_transaction()+'00', '0x01c0'):
            with self.assertRaises(ValueError):
                decoder.decode(transaction)

    def test_invalid_shapes(self):
        for index, invalid in ((5, bytes(19)), (7, []), (8, b''),
                               (8, [[bytes(20), [bytes(31)]]]),
                               (8, [[bytes(19), []]]), (0, [])):
            fields = payload()
            fields[index] = invalid
            with self.subTest(index=index, invalid=invalid):
                with self.assertRaises(ValueError):
                    decoder.decode(envelope(fields))

    def test_strict_text_input(self):
        for transaction in ('', '0x', '0x0', '02 c0 ', '02\tc0\n', 'zz', None, 2):
            with self.assertRaises(ValueError):
                decoder.decode(transaction)

    def test_canonical_lengths_and_parent_boundaries(self):
        for raw in (b'\x81\x00', b'\xb8\x01a', b'\xb9\x00\x38'+bytes(56),
                    b'\xf8\x01\x80', b'\xc1\x81\x80', b'\xc1\xc1\x80', b'\xb8'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    decoder.rlp_item(raw)
        for size in (0, 1, 55, 56, 255, 256):
            value = bytes([128])*size
            raw = decoder.rlp_encode(value)
            self.assertEqual(decoder.rlp_item(raw), (value, len(raw)))

    def test_resource_limits(self):
        with self.assertRaisesRegex(ValueError, 'limit'):
            decoder.decode('02' + '00'*decoder.MAX_TRANSACTION_BYTES)
        raw = b'\x80'
        for _ in range(decoder.MAX_RLP_DEPTH + 2):
            raw = self.wrap(raw)
        with self.assertRaisesRegex(ValueError, 'depth'):
            decoder.rlp_item(raw)
        with self.assertRaisesRegex(ValueError, 'count'):
            decoder.rlp_item(decoder.rlp_encode([b'']*decoder.MAX_RLP_ITEMS))
        for position in (-1, '0', 1):
            with self.assertRaises(ValueError):
                decoder.rlp_item(b'\x80', position)

    @staticmethod
    def wrap(raw):
        if len(raw) < 56:
            return bytes([0xc0 + len(raw)]) + raw
        length = len(raw).to_bytes((len(raw).bit_length()+7)//8, 'big')
        return bytes([0xf7 + len(length)]) + length + raw

    def test_random_malformed_inputs_raise_only_value_error(self):
        rng = random.Random(1559)
        for _ in range(1500):
            raw = b'\x02' + rng.randbytes(rng.randrange(100))
            try:
                decoder.decode(raw.hex())
            except ValueError:
                pass

    def test_cli_demo_json(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            decoder.main(['--demo'])
        self.assertIn(decoder.ZTO, output.getvalue())


if __name__ == '__main__':
    unittest.main()
