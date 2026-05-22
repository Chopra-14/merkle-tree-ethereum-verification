"""
Ethereum JSON-RPC helpers and simplified transaction Merkle root reconstruction.
"""

import hashlib

import requests

from app.merkle_tree import MerkleTree


def fetch_block(rpc_url: str, block_number: int | str) -> dict:
    """
    Fetch a full Ethereum block via eth_getBlockByNumber.

    Uses the second parameter True so full transaction objects are returned.
    """
    if not rpc_url or not rpc_url.strip():
        raise ValueError("RPC URL is required")

    if isinstance(block_number, int):
        block_param = hex(block_number)
    elif isinstance(block_number, str) and not block_number.startswith("0x"):
        block_param = hex(int(block_number))
    else:
        block_param = block_number

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_param, True],
        "id": 1,
    }

    try:
        response = requests.post(rpc_url, json=payload, timeout=30)
        response.raise_for_status()
        body = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"RPC request failed: {exc}") from exc

    if "error" in body:
        raise RuntimeError(f"RPC error: {body['error']}")

    result = body.get("result")
    if result is None:
        raise RuntimeError("RPC returned no block result")

    return result


def inspect_block(block: dict) -> None:
    """Print block number, transactions root, and transaction count."""
    number = int(block["number"], 16)
    tx_root = block["transactionsRoot"]
    tx_count = len(block.get("transactions", []))

    print()
    print("========== BLOCK DETAILS ==========")
    print(f"Block Number      : {number}")
    print(f"Transactions Root : {tx_root}")
    print(f"Transaction Count : {tx_count}")
    print("===================================")
    print()


def hash_transaction(tx: dict) -> bytes:
    """
    Simplified leaf hash: SHA-256 of the transaction hash field string.

    This is for validating Merkle logic, not Ethereum's real trie encoding.
    """
    return hashlib.sha256(tx["hash"].encode()).digest()


def reconstruct_transactions_root(transactions: list[dict]) -> bytes:
    """
    Hash each transaction, build a MerkleTree, and return the computed root.
    """
    if not transactions:
        raise ValueError("Cannot reconstruct root from empty transaction list")

    leaves = [hash_transaction(tx) for tx in transactions]
    tree = MerkleTree(leaves)
    return tree.root
