"""The researcher's model: one structured call per round, through the Codex CLI (`codex exec`).

The prompt, the JSON schema of the answer, the streamed events and stderr are kept in the round's directory, so every
answer can be traced to exactly what the model saw. The model works in an empty temporary directory with a read-only
sandbox: it writes code as text, and only the framework runs it. With `search`, the model may also search the web; the
searches and pages it opened are read back from the events.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


def codex():
    """The Codex CLI: $MOSA_CODEX, else `codex` on the PATH, else the copy installed with the ChatGPT desktop app."""
    for candidate in (os.environ.get("MOSA_CODEX"), shutil.which("codex"), "/usr/lib/chatgpt/resources/codex"):
        if candidate and os.access(candidate, os.X_OK):
            return candidate
    raise RuntimeError("the Codex CLI was not found: install it, put `codex` on the PATH, or set MOSA_CODEX to its path")


def ask(prompt, schema, directory, model=None, timeout=900, search=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory/"schema.json").write_text(json.dumps(schema, indent=1))
    (directory/"prompt.txt").write_text(prompt)
    with tempfile.TemporaryDirectory(prefix="mosa-") as cwd:
        answer = Path(cwd)/"answer.json"
        command = [codex()]+(["--search"] if search else [])+["exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--sandbox", "read-only",
                   "--skip-git-repo-check", "-C", cwd, "--json", "--output-schema", str(directory/"schema.json"), "-o", str(answer)]
        if model:
            command += ["--model", model]
        environment = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY") or k == "OPENAI_API_KEY"}
        started = time.perf_counter()
        with open(directory/"events.jsonl", "w") as events, open(directory/"stderr.txt", "w") as errors:
            process = subprocess.run(command+["-"], input=prompt, text=True, stdout=events, stderr=errors, timeout=timeout, env=environment)
        if process.returncode or not answer.exists():
            raise RuntimeError(f"the model call failed; see {directory}")
        result = json.loads(answer.read_text())
    result["model_seconds"] = time.perf_counter()-started
    if search:
        result["searches"] = searches(directory/"events.jsonl")
    return result


SOURCES = {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["title", "url"],
                                      "properties": {"title": {"type": "string"}, "url": {"type": "string"}}}}
SOURCES_PROMPT = """list every web page you read and relied on, with its title and exact URL; never list a page you did not
open; leave it empty if you used none"""


def cited(sources):
    """The web pages a model cited: http(s) links only, one per URL, at most 12."""
    pages = {s["url"].strip(): {"title": s["title"].strip(), "url": s["url"].strip()}
             for s in sources if s["url"].strip().startswith(("https://", "http://"))}
    return list(pages.values())[:12]


def searches(path):
    """The web searches and pages a call made, from its events: {"query": ...} or {"url": ...}, in order."""
    found = []
    for line in Path(path).read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        item = event.get("item") or {}
        if event.get("type") != "item.completed" or item.get("type") != "web_search":
            continue
        action = item.get("action") or {}
        text = (action.get("query") or item.get("query") or "").strip()
        url = action.get("url") or (text if text.startswith(("https://", "http://")) else None)  # a page open logs its URL as the query
        step = {"url": url} if url else {"query": text}
        if any(step.values()) and step not in found:
            found.append(step)
    return found
