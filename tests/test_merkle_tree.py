"""Tests for MerkleTree construction and proof generation."""

import hashlib

import pytest

from app.merkle_tree import MerkleTree


def _leaf(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def test_root_is_32_bytes():
    tree = MerkleTree([_leaf(b"a"), _leaf(b"b")])
    assert len(tree.root) == 32


def test_odd_leaf_duplication():
    raw = [b"1", b"2", b"3"]
    leaves = [_leaf(x) for x in raw]
    tree = MerkleTree(leaves)
    assert len(tree.root) == 32


def test_proof_structure():
    leaves = [_leaf(b"a"), _leaf(b"b"), _leaf(b"c"), _leaf(b"d")]
    proof = MerkleTree(leaves).get_proof(1)

    for step in proof:
        assert set(step.keys()) == {"hash", "position"}
        assert isinstance(step["hash"], bytes)
        assert step["position"] in ("left", "right")


def test_empty_tree_raises():
    with pytest.raises(ValueError):
        MerkleTree([])


def test_invalid_index_raises():
    tree = MerkleTree([_leaf(b"x"), _leaf(b"y")])
    with pytest.raises(IndexError):
        tree.get_proof(5)
