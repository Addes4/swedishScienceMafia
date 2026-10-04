# Frozen run protocol

```json
{
  "problem": "bounded",
  "approach": "lean",
  "model": "gpt-6-sol",
  "tier_models": [
    "gpt-6-astra",
    "gpt-6.1-sol",
    "gpt-6-luna"
  ],
  "code_output_tokens": 4000,
  "steps": 12,
  "seed": 7501,
  "budget": 1.7,
  "ledger": "/private/tmp/ssm-all-approaches/runs/campaign_usage.jsonl",
  "out": "runs/lean-bounded-headers",
  "ranker": "openai",
  "scheduler": null,
  "gate": null,
  "timeout": 30,
  "api_scheduler": "headers",
  "eval_backend": "local",
  "eval_workers": 4,
  "env_file": null,
  "mock": false,
  "git_head": "1c4a88291a5b678f5266926c5bdc202c8a8901b2",
  "counts": {
    "fixed": 24,
    "stress": 16,
    "validation": 64,
    "probes": 8,
    "audit": 1600,
    "simplify": 1000
  },
  "actual_gate": "strict",
  "effective_eval_workers": 1,
  "live_mode_requested": true,
  "started_utc": "2026-10-03T20:36:01Z",
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
