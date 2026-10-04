# Frozen run protocol

```json
{
  "problem": "rich",
  "approach": "full",
  "model": "gpt-5.4-mini",
  "tier_models": [
    "gpt-6-astra",
    "gpt-5.4-mini",
    "gpt-6-luna"
  ],
  "code_output_tokens": 4000,
  "steps": 6,
  "seed": 7506,
  "budget": 2.5,
  "ledger": "/private/tmp/ssm-all-approaches/runs/campaign_usage.jsonl",
  "out": "runs/full-rich-random-headers",
  "ranker": "random",
  "scheduler": null,
  "gate": null,
  "timeout": 30,
  "api_scheduler": "headers",
  "eval_backend": "local",
  "eval_workers": 4,
  "env_file": null,
  "mock": false,
  "git_head": "228b5466f6f051d9e8ceb02cc22c769fe5944cfc",
  "counts": {
    "fixed": 6,
    "stress": 4,
    "validation": 6,
    "probes": 2,
    "audit": 20,
    "simplify": 6
  },
  "actual_gate": "validated_budget",
  "effective_eval_workers": 4,
  "live_mode_requested": true,
  "started_utc": "2026-10-03T20:45:16Z",
  "note": "One pilot trajectory; fresh audit never feeds selection. Full ranker identity is explicit.",
  "evaluation_profile": {
    "backend": "local",
    "platform": "macOS-26.5-arm64-arm-64bit-Mach-O",
    "python": "3.14.8",
    "numpy": "2.5.3",
    "worker_threads": 1,
    "cpu_limit": "host shared"
  }
}
```

Scores are minimized. All required cases must be valid. Packing gate arms share proposals and evaluator work; they are conditional replay controls, not independent autonomous trajectories. Archive is frozen before each batch. Final candidates and simplifications are frozen before fresh audit generation. Public reference sets are separately labelled. All model requests, including incomplete outputs, cost money and are logged. Only confirmed rate/overload rejections are retried; ambiguous network failures retain spend reservations. Model randomness is not controlled by the harness seed. Generic code simplification is one model proposal plus measured confirmation, not a proof.
