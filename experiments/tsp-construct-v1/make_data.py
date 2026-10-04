"""Recreate MCTS-AHD's TSP construction datasets and our fresh sets under data/, and check hashes.

MCTS-AHD's gen_inst.py (github.com/zz1358m/MCTS-AHD-master, problems/tsp_constructive) draws, after
np.random.seed(1234): train50 (64 instances), val{20,50,100,200} (64 each) and
test{20,50,100,200,500,1000} (1,000 each), in that order. We replay the same stream, keep the sets
we use, and verify their SHA-256 against the files in MCTS-AHD's repository (commit ee9c4f4).

    python make_data.py
"""
import hashlib
import os

import numpy as np

from gen_fresh import SETS as FRESH

SHA256 = {
    "mctsahd/test50.npy": "7154aa3e5b8b2e7b4363ea47d71a3a5235ceaadbacbdcda785c66d49bee98232",
    "mctsahd/test100.npy": "af47bec781fccd3509ae88bc80c8e6e26dd7e38260f88e17e6566bdfed0d28e3",
    "mctsahd/test200.npy": "ed2325fe4b7cd7d5d49c5d8053d22fd250817611d11d1b786b38230f618859c6",
    "mctsahd/val50.npy": "9f76b4d45a24c71c667136ad1a8476a43946f701c6983a8f222d978c291948ff",
    "mctsahd/val100.npy": "4ef5dfee5cc5de3ba7bcbda20d71e4386a90a6967eeb49544f58e66bc00e84aa",
    "mctsahd/val200.npy": "440664fa9ed89c7773770f8983597d4d938bca44f53f71153142fc46c93290f1",
    "fresh50.npy": "a4f48a54e5ee7ad8ff4ac9d6097732c98716c03ef53c7a2ba7f36feb36b3c4c0",
    "fresh100.npy": "5a556e9dbb4abbd56aae5d0cd44254533e7d9cce1776ba65f0dcacd96c22bf84",
    "fresh200.npy": "030aeb2e8797c0f1972602d97d4f8dbf0eb4856b5064053f92e5d0c0c9c83941",
}


def _save(rel, X):
    path = os.path.join("data", rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.save(path, X)


def main():
    np.random.seed(1234)
    _save("mctsahd/train50.npy", np.random.rand(64, 50, 2))
    for n in [20, 50, 100, 200]:
        X = np.random.rand(64, n, 2)
        if n != 20:
            _save(f"mctsahd/val{n}.npy", X)
    for n in [20, 50, 100, 200, 500, 1000]:
        X = np.random.rand(1000, n, 2)
        if n in (50, 100, 200):
            _save(f"mctsahd/test{n}.npy", X)
    for n, seeds in FRESH.items():
        _save(f"fresh{n}.npy", np.stack([np.random.default_rng(s).random((n, 2)) for s in seeds]))
    for rel, h in SHA256.items():
        got = hashlib.sha256(open(os.path.join("data", rel), "rb").read()).hexdigest()
        print(("ok  " if got == h else "BAD ") + rel)
        assert got == h, rel


if __name__ == "__main__":
    main()
