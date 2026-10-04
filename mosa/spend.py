"""Modal spend, from Modal's own billing: the month so far, the credits used, and the spend of each workspace (each
session's app is tagged with its workspace, in modal_app.py). Billing lags by about an hour; results are cached for
ten minutes. Set MOSA_MODAL_CREDIT to the credit you were granted to also see what is left.
"""
from __future__ import annotations

import datetime as dt
import os
import time

from .failure import reason

_cache: dict = {}


def snapshot():
    if _cache and _cache["at"] > time.time()-600:
        return _cache["value"]
    try:
        import modal
        billing = modal.Workspace.from_context().billing
        summary = billing.summary()
        now = dt.datetime.now(dt.timezone.utc)
        mosa = sum(float(i["cost"]) for i in billing.report(start=summary.start, end=now, resolution="d") if i["description"] == "mosa")
        per = {}  # only sessions started since the apps were tagged carry their workspace
        for item in billing.report(start=summary.start, end=now, resolution="d", tag_names=["workspace"]):
            name = (item["tags"] or {}).get("workspace")
            if name:
                per[name] = per.get(name, 0.)+float(item["cost"])
        used = -float(summary.adjustments.get("Credits", 0))
        credit = float(os.environ.get("MOSA_MODAL_CREDIT", 0)) or None
        value = {"month": float(summary.metered_cost), "credits_used": used, "credit": credit,
                 "left": None if credit is None else credit-used, "mosa": mosa, "per_workspace": per, "as_of": time.time()}
    except Exception as error:  # no Modal credentials, no network: say so instead of failing the page
        value = {"error": reason(error)}
    _cache.update(at=time.time(), value=value)
    return value
