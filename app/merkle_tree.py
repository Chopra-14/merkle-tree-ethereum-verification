"""
Merkle tree data structure for building roots and inclusion proofs.
"""

import hashlib
from typing import Literal


def _hash_pair(left: bytes, right: bytes) -> bytes:
    """Combine two child hashes into a parent hash."""
    return hashlib.sha256(left + right).digest()


class MerkleTree:
    """
    Binary Merkle tree built from a list of leaf byte strings.

    Odd-length levels duplicate the last leaf before pairing, per spec.
    """

    def __init__(self, leaves: list[bytes]) -> None:
        if not leaves:
            raise ValueError("Merkle tree requires at least one leaf")

        self._levels: list[list[bytes]] = [list(leaves)]
        current = self._levels[0]

        while len(current) > 1:
            if len(current) % 2 == 1:
                current.append(current[-1])

            next_level: list[bytes] = []
            for i in range(0, len(current), 2):
                next_level.append(_hash_pair(current[i], current[i + 1]))

            self._levels.append(next_level)
            current = next_level

    @property
    def root(self) -> bytes:
        """Final 32-byte Merkle root hash."""
        return self._levels[-1][0]

    def get_proof(self, index: int) -> list[dict[str, bytes | str]]:
        """
        Build a Merkle proof for the leaf at index.

        Returns siblings from leaf level up to the level below the root.
        Each step: {"hash": <sibling bytes>, "position": "left" | "right"}.
        """
        if index < 0 or index >= len(self._levels[0]):
            raise IndexError("leaf index out of range")

        proof: list[dict[str, bytes | str]] = []
        idx = index

        for depth in range(len(self._levels) - 1):
            level = self._levels[depth]
            working = list(level)
            if len(working) % 2 == 1:
                working.append(working[-1])

            if idx % 2 == 0:
                sibling_idx = idx + 1
                position: Literal["left", "right"] = "right"
            else:
                sibling_idx = idx - 1
                position = "left"

            proof.append({"hash": working[sibling_idx], "position": position})
            idx //= 2

        return proof
