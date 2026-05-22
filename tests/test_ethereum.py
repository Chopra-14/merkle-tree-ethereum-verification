"""Tests for Ethereum helper functions."""

import hashlib

from app.ethereum import hash_transaction, reconstruct_transactions_root
from app.merkle_tree import MerkleTree


def test_hash_transaction():
    tx = {"hash": "0xabc123"}
    expected = hashlib.sha256("0xabc123".encode()).digest()
    assert hash_transaction(tx) == expected


def test_reconstruct_root():
    txs = [{"hash": "0x1111"}, {"hash": "0x2222"}, {"hash": "0x3333"}]
    leaves = [hash_transaction(t) for t in txs]
    assert reconstruct_transactions_root(txs) == MerkleTree(leaves).root
