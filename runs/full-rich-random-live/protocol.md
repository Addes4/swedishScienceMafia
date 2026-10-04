# Frozen run protocol

```json
{
  "problem": "rich",
  "approach": "full",
  "model": "gpt-6.1-sol",
  "steps": 6,
  "seed": 7106,
  "budget": 3.0,
  "ledger": "/private/tmp/ssm-all-approaches/runs/campaign_usage.jsonl",
  "out": "runs/full-rich-random-live",
  "ranker": "random",
  "scheduler": null,
  "gate": null,
  "timeout": 30,
  "mock": false,
  "git_head": "cf026352dd48a58781f48e93b83773c019ada528",
  "counts": {
    "fixed": 6,
    "stress": 4,
    "validation": 6,
    "probes": 2,
    "audit": 20,
    "simplify": 6
  },
  "actual_gate": "validated_budget",
  "live_mode_requested": true,
  "started_utc": "2026-10-03T19:16:40Z",
  "note": "One pilot trajectory; fresh audit never feeds selection. Full ranker identity is explicit."
}
```

Scores are minimized. All required cases must be valid. Packing gate arms share proposals and evaluator work; they are conditional replay controls, not independent autonomous trajectories. Archive is frozen before each batch. Final candidates and simplifications are frozen before fresh audit generation. Public reference sets are separately labelled. All model requests, including incomplete outputs, cost money and are logged. No automatic retries. Model randomness is not controlled by the harness seed. Generic code simplification is one model proposal plus measured confirmation, not a proof.
