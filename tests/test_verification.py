"""Tests for verify_proof and tamper detection."""

import hashlib

from app.merkle_tree import MerkleTree
from app.verifier import verify_proof


def _setup():
    raw_leaves = [b"alpha", b"beta", b"gamma", b"delta"]
    leaves = [hashlib.sha256(x).digest() for x in raw_leaves]
    tree = MerkleTree(leaves)
    return raw_leaves, tree


def test_valid_proof():
    raw_leaves, tree = _setup()
    proof = tree.get_proof(2)
    assert verify_proof(raw_leaves[2], proof, tree.root) is True


def test_tampered_leaf_fails():
    raw_leaves, tree = _setup()
    proof = tree.get_proof(1)
    assert verify_proof(b"wrong-data", proof, tree.root) is False


def test_tampered_proof_hash_fails():
    raw_leaves, tree = _setup()
    proof = tree.get_proof(0)
    bad_proof = list(proof)
    bad_proof[0] = {"hash": b"\x00" * 32, "position": bad_proof[0]["position"]}
    assert verify_proof(raw_leaves[0], bad_proof, tree.root) is False


def test_odd_leaf_count_all_verify():
    raw = [b"one", b"two", b"three"]
    leaves = [hashlib.sha256(x).digest() for x in raw]
    tree = MerkleTree(leaves)
    for i, data in enumerate(raw):
        assert verify_proof(data, tree.get_proof(i), tree.root) is True


def test_ethereum_style_leaf_encoding():
    txs = [{"hash": "0xaaaa"}, {"hash": "0xbbbb"}]
    leaves = [hashlib.sha256(tx["hash"].encode()).digest() for tx in txs]
    tree = MerkleTree(leaves)
    proof = tree.get_proof(0)
    assert verify_proof(txs[0]["hash"].encode(), proof, tree.root) is True
