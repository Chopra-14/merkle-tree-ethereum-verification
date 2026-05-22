"""
Standalone Merkle proof verification (no access to the original tree).
"""

import hashlib

from app.merkle_tree import _hash_pair


def verify_proof(leaf_data: bytes, proof: list[dict], expected_root: bytes) -> bool:
    """
    Recompute the Merkle root from leaf_data and a proof list.

    Starts with SHA-256(leaf_data), then combines with each sibling in order.
    Returns True only if the result equals expected_root.
    """
    current = hashlib.sha256(leaf_data).digest()

    for step in proof:
        sibling = step["hash"]
        if step["position"] == "left":
            current = _hash_pair(sibling, current)
        else:
            current = _hash_pair(current, sibling)

    return current == expected_root
