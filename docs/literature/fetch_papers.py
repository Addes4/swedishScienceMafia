"""Download the papers reviewed in docs/literature/related-work.md into docs/literature/related-papers/.

The PDFs are not committed: the repository is public and most of them may not be
redistributed. This script fetches them again from arXiv or the authors' and publishers'
open copies. Existing valid files are skipped, every download is checked to be a real PDF
(or PostScript/HTML where noted), and arXiv requests are spaced 3 seconds apart as arXiv asks.

    python3 docs/literature/fetch_papers.py              # everything
    python3 docs/literature/fetch_papers.py --only RAISE # entries whose file name contains "RAISE"

Papers behind a bot check or paywall are listed at the end with a link to open in a browser.
Standard library only.
"""
import argparse
import os
import time
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "related-papers")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko)"


def arxiv(i):
    return [f"https://arxiv.org/pdf/{i}", f"https://export.arxiv.org/pdf/{i}"]


# (folder, file name, candidate URLs). The kind of file is taken from the extension.
PAPERS = [
    ("0-read-first", "2025 Herrmann & Pallez - In-depth study of LLM contributions to bin packing.pdf", arxiv("2510.27353")),
    ("0-read-first", "2025 Sim, Renau & Hart - Beyond the hype, benchmarking LLM-evolved bin packing heuristics.pdf", arxiv("2501.11411")),
    ("0-read-first", "2026 Liu, Figalli et al - RAISE, robust adversary instance search.pdf", arxiv("2606.31801")),
    ("0-read-first", "2026 Ke et al - ASRO, game-theoretic co-evolution of heuristics and instances.pdf", arxiv("2601.22896")),
    ("0-read-first", "2026 Gideoni, Risi & Gal - Simple baselines are competitive with code evolution.pdf", arxiv("2602.16805")),
    ("0-read-first", "2026 Oved et al - Evolution or illusion, rethinking evaluation in LLM evolutionary search.pdf", arxiv("2609.19799")),
    ("0-read-first", "2026 Gupta et al - Automated discovery has no universally superior harness.pdf", arxiv("2607.18235")),
    ("0-read-first", "2026 Cemri et al - AdaEvolve.pdf", arxiv("2602.20133")),
    ("0-read-first", "2026 Yan et al - PACEvolve.pdf", arxiv("2601.10657")),
    ("0-read-first", "2015 Dwork et al - Generalization in adaptive data analysis and holdout reuse (reusable holdout).pdf", arxiv("1506.02629")),
    ("0-read-first", "2015 Blum & Hardt - The Ladder, a reliable leaderboard.pdf", arxiv("1502.04585")),
    ("0-read-first", "2025 Wen et al - Predicting empirical AI research outcomes with language models.pdf", arxiv("2506.00794")),
    ("0-read-first", "2026 Ning et al - One run is not an idea, the implementation lottery.pdf", arxiv("2607.26587")),

    ("1-falsify-bin-packing", "2006 Solar-Lezama et al - Combinatorial sketching for finite programs (CEGIS).pdf",
     ["https://people.csail.mit.edu/asolar/papers/asplos06-final.pdf"]),
    ("1-falsify-bin-packing", "2023 Namyar et al - MetaOpt, finding adversarial inputs for heuristics.pdf", arxiv("2311.12779")),
    ("1-falsify-bin-packing", "2025 Karimi et al - Robust heuristic algorithm design with LLMs.pdf", arxiv("2510.08755")),
    ("1-falsify-bin-packing", "2026 Nikoleit et al - The art of being difficult, adversarial instances for heuristics.pdf", arxiv("2601.16849")),
    ("1-falsify-bin-packing", "2006 Csirik et al - On the sum-of-squares algorithm for bin packing.pdf", arxiv("cs/0210013")),
    ("1-falsify-bin-packing", "2007 Bender et al - Sum-of-squares heuristics for bin packing and memory allocation.pdf",
     ["https://www3.cs.stonybrook.edu/~bender/pub/JEA07-sumsquares.pdf"]),
    ("1-falsify-bin-packing", "2022 Angelopoulos, Kamali & Shadkami - Online bin packing with predictions.pdf", arxiv("2102.03311")),
    ("1-falsify-bin-packing", "2002 Kenyon & Mitzenmacher - Linear waste of best fit bin packing on skewed distributions.ps",
     ["https://cs.brown.edu/people/claire/Publis/mitzen.ps"]),
    ("1-falsify-bin-packing", "2016 Lopez-Ibanez et al - The irace package, iterated racing.pdf",
     ["https://iridia.ulb.ac.be/IridiaTrSeries/link/IridiaTr2011-004.pdf"]),  # IRIDIA technical-report version
    ("1-falsify-bin-packing", "2010 Cawley & Talbot - Over-fitting in model selection and selection bias.pdf",
     ["https://jmlr.org/papers/volume11/cawley10a/cawley10a.pdf"]),
    ("1-falsify-bin-packing", "2002 Zeller & Hildebrandt - Simplifying and isolating failure-inducing input (delta debugging).pdf",
     ["https://www.cs.purdue.edu/homes/xyzhang/fall07/Papers/delta-debugging.pdf"]),
    ("1-falsify-bin-packing", "2020 MacIver & Donaldson - Test-case reduction via test-case generation (Hypothesis).pdf",
     ["https://drops.dagstuhl.de/storage/00lipics/lipics-vol166-ecoop2020/LIPIcs.ECOOP.2020.13/LIPIcs.ECOOP.2020.13.pdf"]),

    ("2-simplify", "2026 Pelleriti et al - What do evolutionary coding agents evolve.pdf", arxiv("2605.20086")),
    ("2-simplify", "2026 Li et al (DeepMind) - Discovering multiagent learning algorithms with LLMs.pdf", arxiv("2602.16928")),
    ("2-simplify", "1998 Langdon & Poli - Fitness causes bloat, mutation.pdf",
     ["http://www0.cs.ucl.ac.uk/staff/W.Langdon/ftp/papers/WBL.euro98_bloatm.pdf"]),

    ("3-strategist", "1993 Luby, Sinclair & Zuckerman - Optimal speedup of Las Vegas algorithms.pdf",
     ["https://www.cs.utexas.edu/~diz/Sub%20Websites/Research/optimal_speedup_of_las_vegas_algorithms.pdf"]),
    ("3-strategist", "2011 Gyorgy & Kocsis - Efficient multi-start strategies for local search algorithms.pdf", arxiv("1401.3894")),
    ("3-strategist", "2017 Friedrich, Kotzing & Wagner - A generic bet-and-run strategy.pdf",
     ["https://ojs.aaai.org/index.php/AAAI/article/download/10645/10504"]),
    ("3-strategist", "2005 Cicirello & Smith - The max k-armed bandit.pdf", ["https://cdn.aaai.org/AAAI/2005/AAAI05-215.pdf"]),
    ("3-strategist", "1979 Weitzman - Optimal search for the best alternative (MIT working paper).pdf",
     ["https://dspace.mit.edu/server/api/core/bitstreams/53ba0aeb-c975-4919-a0d9-1b5a760c6919/content"]),
    ("3-strategist", "2019 Davidson & El Hady - Foraging as an evidence accumulation process.pdf", arxiv("1809.05023")),
    ("3-strategist", "2021 Kilpatrick, Davidson & El Hady - Uncertainty drives deviations in normative foraging.pdf",
     ["https://www.biorxiv.org/content/10.1101/2021.04.24.441241v1.full.pdf"]),
    ("3-strategist", "2026 Cheng et al - To diff or not to diff.pdf", arxiv("2604.27296")),
    ("3-strategist", "2016 Packebusch & Mertens - Low autocorrelation binary sequences.pdf", arxiv("1512.02475")),
    ("3-strategist", "2026 Psenicnik et al - Prioritizing search space regions in LABS (Thompson sampling).pdf", arxiv("2607.09688")),

    ("4-triage", "2026 Luo et al - Relay, don't route.pdf", arxiv("2608.05651")),
    ("4-triage", "2026 Tanveer - LEVI.pdf", arxiv("2605.09764")),
    ("4-triage", "2026 Ray et al - AdaptEvolve.pdf", arxiv("2602.11931")),
    ("4-triage", "2025 Yu et al - AlphaResearch.pdf", arxiv("2511.08522")),
    ("4-triage", "2023 Chen, Zaharia & Zou - FrugalGPT.pdf", arxiv("2305.05176")),
    ("4-triage", "2024 Ong et al - RouteLLM.pdf", arxiv("2406.18665")),
    ("4-triage", "2025 Si, Hashimoto & Yang - The ideation-execution gap.pdf", arxiv("2506.20803")),
    ("4-triage", "2026 Zheng et al - Can we predict before executing ML agents (FOREAGENT).pdf", arxiv("2601.05930")),
    ("4-triage", "2026 Madeyski - Triage, routing SE tasks to LLM tiers (name clash).pdf", arxiv("2604.07494")),

    ("5-integrity-gate", "2026 Luo et al - HASE, harness-aware self-evolving.pdf", arxiv("2607.03935")),
    ("5-integrity-gate", "2025 Wang et al - ThetaEvolve.pdf", arxiv("2511.23473")),
    ("5-integrity-gate", "2025 Zhong, Raghunathan & Carlini - ImpossibleBench.pdf", arxiv("2510.20270")),
    ("5-integrity-gate", "2025 Luo, Kasirzadeh & Shah - Hidden pitfalls of AI scientist systems.pdf", arxiv("2509.08713")),
    ("5-integrity-gate", "2025 Huang et al - POPPER, agentic sequential falsifications.pdf", arxiv("2502.09858")),
    ("5-integrity-gate", "2025 METR - Recent frontier models are reward hacking (blog).html",
     ["https://metr.org/blog/2025-06-05-recent-reward-hacking/"]),

    ("6-evaluation-and-benchmarks", "2026 Ferreira, Hutter et al - Can LLMs beat classical HPO, a study on autoresearch.pdf", arxiv("2603.24647")),
    ("6-evaluation-and-benchmarks", "2025 Sun et al - CO-Bench.pdf", arxiv("2504.04310")),
    ("6-evaluation-and-benchmarks", "2025 Chen et al - HeuriGym.pdf", arxiv("2506.07972")),
    ("6-evaluation-and-benchmarks", "2025 Imajuku et al - ALE-Bench.pdf", arxiv("2506.09050")),
    ("6-evaluation-and-benchmarks", "2025 Press et al - AlgoTune.pdf", arxiv("2507.15887")),
]

# Behind a bot check (HAL), a paywall (ACM, Science) or with no open copy found.
MANUAL = [
    ("Da Costa et al. 2008, Adaptive operator selection with dynamic multi-armed bandits", "https://inria.hal.science/inria-00278542/document"),
    ("Fialho et al. 2008, Extreme value based adaptive operator selection", "https://inria.hal.science/inria-00287355/document"),
    ("Fialho et al. 2010, Analyzing bandit-based adaptive operator selection mechanisms", "https://inria.hal.science/inria-00519579/document"),
    ("de Vries 2023, falsify: internal shrinking reimagined for Haskell", "https://doi.org/10.1145/3609026.3609733"),
    ("Dwork et al. 2015, The reusable holdout (Science version)", "https://doi.org/10.1126/science.aaa9375"),
    ("Nordin, Francone & Banzhaf 1996, Explicitly defined introns and destructive crossover", "MIT Press, Advances in Genetic Programming 2 (no open copy found)"),
]

MAGIC = {".pdf": b"%PDF-", ".ps": b"%!PS"}


def valid(data, name):
    ext = os.path.splitext(name)[1]
    if ext == ".html":
        return b"<html" in data[:2000].lower() or b"<!doctype html" in data[:2000].lower()
    return data.startswith(MAGIC[ext]) and len(data) > 20000


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", help="fetch only entries whose file name contains this text")
    args = ap.parse_args()
    got, failed = 0, []
    for folder, name, urls in PAPERS:
        if args.only and args.only.lower() not in name.lower():
            continue
        path = os.path.join(ROOT, folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path) and valid(open(path, "rb").read(), name):
            got += 1
            continue
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                data = urllib.request.urlopen(req, timeout=60).read()
                if valid(data, name):
                    with open(path, "wb") as f:
                        f.write(data)
                    got += 1
                    print(f"ok      {folder}/{name}")
                    break
                print(f"  not a valid file from {url}")
            except Exception as e:
                print(f"  {type(e).__name__}: {e} ({url})")
            finally:
                if "arxiv.org" in url:
                    time.sleep(3)
        else:
            failed.append(f"{folder}/{name}")
    print(f"\n{got} present, {len(failed)} failed")
    for f in failed:
        print("FAILED", f)
    if not args.only:
        print("\nOpen these in a browser (bot check, paywall or no open copy):")
        for title, url in MANUAL:
            print(f"  {title}: {url}")


if __name__ == "__main__":
    main()
