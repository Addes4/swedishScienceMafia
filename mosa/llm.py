"""The researcher's model: one structured call per round, through the Codex CLI (`codex exec`).

The prompt, the JSON schema of the answer, the streamed events and stderr are kept in the round's directory, so every
answer can be traced to exactly what the model saw. The model works in an empty temporary directory with a read-only
sandbox: it writes code as text, and only the framework runs it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import time


def ask(prompt, schema, directory, model=None, timeout=900):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory/"schema.json").write_text(json.dumps(schema, indent=1))
    (directory/"prompt.txt").write_text(prompt)
    with tempfile.TemporaryDirectory(prefix="mosa-") as cwd:
        answer = Path(cwd)/"answer.json"
        command = ["codex", "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--sandbox", "read-only",
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
    return result
