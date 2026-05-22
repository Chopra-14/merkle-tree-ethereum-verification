# Merkle Tree Ethereum Transaction Verification

Blockchain bonus project: build a Merkle tree in Python, fetch a real Ethereum block, and verify transaction inclusion with a cryptographic proof.

## Project Overview

This repository implements a binary Merkle tree from scratch, generates inclusion proofs, and verifies them without access to the original tree. It connects to an Ethereum JSON-RPC node, loads a block with full transaction objects, hashes transactions with a simplified scheme (SHA-256 of the `hash` field), reconstructs a Merkle root, and proves one transaction is included.

## Features

- `MerkleTree` with odd-leaf duplication and 32-byte root
- `get_proof(index)` returning ordered `hash` + `position` steps
- Standalone `verify_proof()` for off-tree verification
- `fetch_block()` via `eth_getBlockByNumber` with full transactions
- Local pytest suite (valid proof, tampered leaf, tampered proof)
- Docker and docker-compose for reproducible runs

## Architecture

```text
Ethereum RPC (Alchemy / Infura)
           |
           v
     fetch_block()
           |
           v
     inspect_block()
           |
           v
   hash_transaction()  (per tx)
           |
           v
      MerkleTree
           |
     +-----+-----+
     v           v
 get_proof()  verify_proof()
```

## Folder Structure

```text
merkle-tree-ethereum-verification/
├── app/
│   ├── __init__.py
│   ├── merkle_tree.py
│   ├── verifier.py
│   ├── ethereum.py
│   └── main.py
├── tests/
│   ├── test_merkle_tree.py
│   ├── test_verification.py
│   └── test_ethereum.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone and enter the project

```bash
cd merkle-tree-ethereum-verification
```

### 2. Virtual environment (Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure RPC URL

Copy the example env file and add your Alchemy or Infura mainnet HTTPS URL:

```bash
copy .env.example .env
```

Edit `.env`:

```env
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
```

Never commit `.env` or API keys.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RPC_URL` | Yes | Ethereum JSON-RPC HTTPS endpoint |
| `BLOCK_NUMBER` | No | Block to fetch (default `19000000`) |
| `TX_INDEX` | No | Transaction index for proof demo (default `0`) |

## Running the Application

```bash
python -m app.main
```

## Running Tests

```bash
pytest -v
```

Expected: all tests pass (valid proof, tampered leaf fails, tampered proof fails).

## Docker Instructions

```bash
docker compose build
docker compose run --rm test
docker compose up --build app
```

`docker-compose` uses `.env` for `RPC_URL`.

## Sample Output

```text
Fetching Ethereum block...

========== BLOCK DETAILS ==========
Block Number      : 19000000
Transactions Root : 0x...
Transaction Count : 150
===================================

Reconstructed Merkle Root:
4bc89e12d77f...

Generated Merkle Proof
Proof Length: 8

Verification Result:
True

Tampered leaf rejected : True
Tampered proof rejected: True

Done — transaction inclusion verified against reconstructed root.
```

## Technologies Used

- Python 3.12
- `requests` — JSON-RPC calls
- `hashlib` — SHA-256 Merkle hashing
- `pytest` — unit tests
- `python-dotenv` — environment configuration
- Docker / docker-compose

## How Hashing Works

| Step | Method |
|------|--------|
| Leaf | `SHA-256(tx["hash"].encode())` |
| Internal node | `SHA-256(left \|\| right)` |
| Odd level | Duplicate last leaf, then pair |

The on-chain `transactionsRoot` uses RLP + Keccak. This project uses the simplified leaf rule from the assignment so tree logic can be tested independently.

## Future Improvements

- Match Ethereum’s real `transactionsRoot` using RLP + Keccak (`pysha3`, `rlp`)
- CLI flags for block number and tx index
- Proof export to JSON for auditing
- Support Sepolia / Holesky for cheaper testing

## References

- [Merkle tree (Wikipedia)](https://en.wikipedia.org/wiki/Merkle_tree)
- [Ethereum JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [Alchemy](https://www.alchemy.com/)
