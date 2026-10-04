"""Launch ShinkaEvolve on any problem folder.

    python -m autoresearch.run problems/erdos_squares --generations 50
    python -m autoresearch.run problems/circle_packing --model claude-sonnet-5-5 --effort medium

Every LLM role (proposals, meta-recommendations, novelty judge) uses the same Claude model,
and code-embedding novelty (which needs an OpenAI key) is off unless --embedding is given.
This is the stock-ShinkaEvolve baseline; research-layer components plug in on top.
"""
import argparse
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("problem", help="path to problems/<name>")
    ap.add_argument("--generations", type=int, default=50)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--max-tokens", type=int, default=32000)
    ap.add_argument("--results", default=None, help="results directory (default results/<problem>_<time>)")
    ap.add_argument("--no-text-feedback", action="store_true", help="hide the evaluator's per-instance feedback from the LLM")
    ap.add_argument("--embedding", default=None, help="embedding model for novelty filtering (off by default)")
    ap.add_argument("--max-cost", type=float, default=None, help="stop after this many dollars of API spend")
    ap.add_argument("--eval-jobs", type=int, default=2)
    ap.add_argument("--proposal-jobs", type=int, default=2)
    args = ap.parse_args()

    from . import shinka_compat
    shinka_compat.apply(effort=args.effort)
    from shinka.core import EvolutionConfig, ShinkaEvolveRunner
    from shinka.database import DatabaseConfig
    from shinka.launch import LocalJobConfig

    problem = Path(args.problem).resolve()
    for f in ("initial.py", "evaluate.py", "verify.py", "problem.md"):
        if not (problem / f).exists():
            raise SystemExit(f"{problem} is missing {f} (see problems/README.md)")
    results = args.results or f"results/{problem.name}_{time.strftime('%Y%m%d_%H%M%S')}"

    evo = EvolutionConfig(
        task_sys_msg=(problem / "problem.md").read_text(),
        init_program_path=str(problem / "initial.py"),
        results_dir=results,
        num_generations=args.generations,
        language="python",
        llm_models=[args.model],
        llm_kwargs={"max_tokens": args.max_tokens},
        meta_llm_models=[args.model],
        meta_llm_kwargs={"max_tokens": args.max_tokens},
        novelty_llm_models=[args.model],
        novelty_llm_kwargs={"max_tokens": args.max_tokens},
        embedding_model=args.embedding,
        use_text_feedback=not args.no_text_feedback,
        max_api_costs=args.max_cost,
    )
    job = LocalJobConfig(eval_program_path=str(problem / "evaluate.py"))
    runner = ShinkaEvolveRunner(
        evo_config=evo, job_config=job, db_config=DatabaseConfig(),
        max_evaluation_jobs=args.eval_jobs, max_proposal_jobs=args.proposal_jobs,
    )
    runner.run()


if __name__ == "__main__":
    main()
