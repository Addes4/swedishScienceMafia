# Frozen run protocol

```json
{
  "problem": "circle",
  "approach": "lean",
  "model": "gpt-6.1-sol",
  "steps": 1,
  "seed": 7101,
  "budget": 3.0,
  "ledger": "/private/tmp/ssm-all-approaches/runs/campaign_usage.jsonl",
  "out": "runs/software-check-circle",
  "ranker": "openai",
  "scheduler": "patience",
  "gate": null,
  "timeout": 30,
  "mock": true,
  "git_head": "3bb715a4b785570a439200cab04e9b1ec4346b32",
  "counts": {
    "fixed": 2,
    "stress": 0,
    "validation": 2,
    "probes": 0,
    "audit": 8,
    "simplify": 8
  },
  "actual_gate": "strict",
  "llm_used": false,
  "started_utc": "2026-10-03T18:46:51Z",
  "note": "One pilot trajectory; fresh audit never feeds selection. Full ranker identity is explicit."
}
```

Scores are minimized. All required cases must be valid. Packing gate arms share proposals and evaluator work; they are conditional replay controls, not independent autonomous trajectories. Archive is frozen before each batch. Final candidates and simplifications are frozen before fresh audit generation. Public reference sets are separately labelled. All model requests, including incomplete outputs, cost money and are logged. No automatic retries. Model randomness is not controlled by the harness seed. Generic code simplification is one model proposal plus measured confirmation, not a proof.
