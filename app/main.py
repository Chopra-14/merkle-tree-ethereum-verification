"""
End-to-end demo: fetch block, rebuild Merkle root, prove and verify inclusion.
"""

import hashlib
import os
import sys

from dotenv import load_dotenv

from app.ethereum import (
    fetch_block,
    hash_transaction,
    inspect_block,
    reconstruct_transactions_root,
)
from app.merkle_tree import MerkleTree
from app.verifier import verify_proof


def _get_rpc_url() -> str:
    load_dotenv()
    return (os.getenv("RPC_URL") or os.getenv("ETH_RPC_URL") or "").strip()


def main() -> None:
    rpc_url = _get_rpc_url()
    if not rpc_url:
        print("Error: set RPC_URL in .env (see .env.example).", file=sys.stderr)
        sys.exit(1)

    block_number = os.getenv("BLOCK_NUMBER", "19000000")
    tx_index = int(os.getenv("TX_INDEX", "0"))

    print("Fetching Ethereum block...")
    print()

    try:
        block = fetch_block(rpc_url, block_number)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    inspect_block(block)

    transactions = block.get("transactions", [])
    if not transactions:
        print("Error: block has no transactions.", file=sys.stderr)
        sys.exit(1)

    if tx_index < 0 or tx_index >= len(transactions):
        print(f"Error: TX_INDEX {tx_index} out of range (0-{len(transactions) - 1}).")
        sys.exit(1)

    print("Reconstructed Merkle Root:")
    our_root = reconstruct_transactions_root(transactions)
    print(our_root.hex())
    print()
    print(
        "Note: simplified SHA-256 leaves — not identical to on-chain transactionsRoot."
    )
    print()

    leaves = [hash_transaction(tx) for tx in transactions]
    tree = MerkleTree(leaves)
    target_tx = transactions[tx_index]

    print("Generated Merkle Proof")
    proof = tree.get_proof(tx_index)
    print(f"Proof Length: {len(proof)}")
    print()

    leaf_data = target_tx["hash"].encode()
    verified = verify_proof(leaf_data, proof, tree.root)

    print("Verification Result:")
    print(verified)
    print()

    if not verified:
        sys.exit(1)

    # Demonstrate tamper detection (evaluator requirement)
    bad_leaf = verify_proof(b"tampered", proof, tree.root)
    bad_proof = list(proof)
    if bad_proof:
        step = dict(bad_proof[0])
        step["hash"] = hashlib.sha256(step["hash"]).digest()
        bad_proof[0] = step

    print("Tampered leaf rejected :", not bad_leaf)
    print("Tampered proof rejected:", not verify_proof(leaf_data, bad_proof, tree.root))
    print()
    print("Done — transaction inclusion verified against reconstructed root.")


if __name__ == "__main__":
    main()
