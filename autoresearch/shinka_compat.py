"""Make ShinkaEvolve 0.0.7 work with current Claude models.

Two problems with stock shinka-evolve 0.0.7 (also present on its GitHub main for 5.x models):
  1. Its pricing table does not list Claude Opus 5.5 / Sonnet 5.5 / Fable 5.1, so it cannot
     resolve them to the Anthropic provider.
  2. It sends `temperature` (and `thinking.budget_tokens` for models it marks as reasoning).
     Claude Opus 4.7 and later reject both with HTTP 400; effort is set with
     `output_config.effort` instead.
apply() fixes both in-process without forking ShinkaEvolve.
"""
import math

# model -> (input $ per 1M tokens, output $ per 1M tokens)
CLAUDE_MODELS = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
# Models where sampling parameters and thinking budgets are rejected.
_NO_SAMPLING_PREFIXES = ("claude-fable-5", "claude-opus-5", "claude-sonnet-5", "claude-opus-4-7", "claude-opus-4-8")

_applied = False


def apply(effort: str = "high") -> None:
    global _applied
    if _applied:
        return
    from shinka.llm import kwargs as shinka_kwargs
    from shinka.llm import llm as shinka_llm
    from shinka.llm.providers import pricing

    df = pricing._PRICING_DF
    for name, (inp, out) in CLAUDE_MODELS.items():
        if name not in df.index:
            df.loc[name, ["provider", "input_price", "output_price"]] = ["anthropic", inp / 1e6, out / 1e6]
            df.loc[name, ["input_price_tier2", "output_price_tier2", "tier_threshold"]] = [math.nan] * 3
            df.loc[name, ["is_reasoning", "think_temp_fixed", "requires_reasoning"]] = [False, False, False]

    original = shinka_kwargs.sample_model_kwargs

    def sample_model_kwargs(*args, **kwargs):
        out = original(*args, **kwargs)
        if str(out.get("model_name", "")).startswith(_NO_SAMPLING_PREFIXES):
            for key in ("temperature", "top_p", "top_k", "thinking"):
                out.pop(key, None)
            if effort:
                out["output_config"] = {"effort": effort}
        return out

    shinka_kwargs.sample_model_kwargs = sample_model_kwargs
    shinka_llm.sample_model_kwargs = sample_model_kwargs
    _applied = True
