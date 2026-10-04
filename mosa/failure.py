"""Why a session stopped, in words a person can act on, written to the workspace's notebook.

A session that dies must say so: the workbench stops showing it as running and the conversation shows the reason, so
nobody waits for results that will never come.
"""
from __future__ import annotations

import traceback


def reason(error):
    """A short, actionable explanation of an exception."""
    text = f"{type(error).__name__}: {error}"
    lowered = text.lower()
    if "spend limit" in lowered or "resourceexhausted" in lowered:
        return "Modal refused the work: the workspace has reached its spend limit. Raise the limit or add credit on Modal, or continue on this machine."
    if "quota" in lowered or "rate limit" in lowered or "429" in lowered:
        return f"A quota or rate limit was hit ({text[:160]}). Wait and retry, or continue on this machine."
    if "token" in lowered and "modal" in lowered:
        return "Modal rejected the credentials. Run `modal token set` (or activate the right profile) and retry."
    if isinstance(error, ModuleNotFoundError):
        return f"A module is missing where the code ran ({error}). Install it (for Modal: the image in mosa/modal_app.py) and retry."
    if "model call failed" in lowered:
        return f"The model call failed ({text[:160]}). Check that the codex CLI is logged in, then retry."
    return text[:300]


def record(book, error):
    """Write a failure event: the reason for people, the traceback for debugging."""
    book.write("failed", reason=reason(error), error=f"{type(error).__name__}: {error}"[:500],
               traceback="".join(traceback.format_exception(error))[-3000:])
