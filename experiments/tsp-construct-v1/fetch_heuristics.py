"""Download released LLM-designed heuristics whose repositories carry no licence.

They are not redistributed here; this script fetches them at pinned commits into
heuristics/fetched/ (git-ignored) and prepends a provenance comment. MIT-licensed heuristics
(MCTS-AHD, ReEvo/AEL, HiFo-Prompt) are committed in heuristics/ with their notices.

    python fetch_heuristics.py
"""
import os
import urllib.request

PINNED = {
    "clade_released.py": ("Mriya0306/Clade-AHD", "ffd566b70070331dbd2759a2cb828543e43da2ac",
                          "problems/tsp_constructive/gpt.py"),
    "refineevo_released.py": ("samwu-learn/RefineEvo", "7de015d5230e32b8b85fa83a3ecc55d117489138",
                              "problems/tsp_constructive/gpt.py"),
}

if __name__ == "__main__":
    os.makedirs("heuristics/fetched", exist_ok=True)
    for name, (repo, sha, path) in PINNED.items():
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
        code = urllib.request.urlopen(url, timeout=30).read().decode()
        head = f"# Fetched from github.com/{repo} at commit {sha}, {path}. Not redistributed.\n"
        open(os.path.join("heuristics/fetched", name), "w").write(head + code)
        print("fetched", name)
