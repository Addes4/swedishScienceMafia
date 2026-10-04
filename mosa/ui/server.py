"""The workbench server (localhost only): notebooks, best known solutions, verified records, launching labs.

    python -m mosa serve        # then open http://127.0.0.1:8777

Notebooks are the events.jsonl files under runs/ (labs started here or from the command line) and history/ (imported
labs). The app polls /api/events with the number of events it already has, so a running lab streams into the page.
"""
from __future__ import annotations

from functools import lru_cache
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parent/"static"
FOLDERS = ("runs", "history")


def notebooks():
    out = {}
    for folder in FOLDERS:
        for path in sorted((ROOT/folder).glob("*/events.jsonl")):
            out[f"{folder}/{path.parent.name}"] = path
        for path in sorted((ROOT/folder).glob("*/process.log")):  # a workspace whose planner has not written yet
            out.setdefault(f"{folder}/{path.parent.name}", path.parent/"events.jsonl")
    return out


@lru_cache(maxsize=256)
def _events(path, stamp):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.endswith("}")]


def events(path):
    if not os.path.exists(path):
        return []
    stat = os.stat(path)
    return _events(str(path), (stat.st_mtime_ns, stat.st_size))


def summary(lab_id, path):
    ev = events(path)
    head = next((e for e in ev if e["type"] == "lab"), {})
    records = {}
    for e in ev:
        if e["type"] == "record" and e.get("record"):
            if e["n"] not in records or e["side"] < records[e["n"]]:
                records[e["n"]] = e["side"]
    done = sum(e["type"] == "done" for e in ev) >= max(1, sum(e["type"] == "lab" for e in ev))  # every session finished
    updated = ev[-1]["time"] if ev else 0
    sessions = [e for e in ev if e["type"] == "lab"]
    request = next((e["request"] for e in ev if e["type"] == "request"), None)
    names = [e["name"] for e in ev if e["type"] == "name"] or [head.get("name")]  # a rename appends a name event
    targets = sorted({n for e in sessions for n in e.get("targets", [])})
    return {"id": lab_id, "name": path.parent.name, "label": names[-1], "request": request, "folder": lab_id.split("/")[0], "kind": head.get("kind", "lab"),
            "sessions": len(sessions), "all_targets": targets,
            "title": head.get("title", ""), "domain": head.get("domain", ""), "started": ev[0]["time"] if ev else os.path.getmtime(path.parent),
            "updated": updated, "done": done, "running": not done and time.time()-(updated or os.path.getmtime(path.parent)) < 900,
            "chains": head.get("chains", 1), "rounds": head.get("rounds", 1), "targets": head.get("targets", []),
            "seeds": head.get("seeds", []), "backend": head.get("backend"), "events": len(ev),
            "records": {str(k): v for k, v in sorted(records.items())}, "source": head.get("source"), "brief": bool(head.get("brief"))}


@lru_cache(maxsize=8)
def domain(name="squares"):
    sys.path.insert(0, str(ROOT))
    from mosa.domain import get
    return get(name)


def reference(n, name="squares"):
    d = domain(name)
    poses, side = d.reference(n)
    return {"n": n, "side": side, "poses": poses.tolist() if poses is not None else None, "info": d.info(n)}


def records():
    best = {}
    for lab_id, path in notebooks().items():
        for e in events(path):
            if e["type"] == "record" and e.get("record") and (e["n"] not in best or e["side"] < best[e["n"]]["side"]):
                best[e["n"]] = {**{k: e.get(k) for k in ("n", "side", "reference_side", "improvement", "chain", "round", "seed",
                                                          "min_pair_clearance", "min_wall_clearance", "float_zero_tolerance",
                                                          "high_precision", "poses", "time")}, "lab": lab_id}
    return [best[n] for n in sorted(best)]


def launch(spec):
    """Start a session: in an existing workspace (spec["workspace"], a lab id) or a new one. kind "lab" runs researchers;
    kind "apply" runs an existing idea (spec["idea"] = [session, researcher, round]) on more instances."""
    kind = spec.get("kind", "lab")
    if kind not in ("lab", "apply", "run"):
        raise ValueError("kind must be run, lab or apply")
    workspace = spec.get("workspace")
    if workspace and workspace not in notebooks():
        raise ValueError(f"unknown workspace {workspace}")
    out = workspace or f"runs/{time.strftime('%Y%m%d-%H%M%S')}"
    if kind == "run":  # a request in plain words: the planning agent sets up and runs the session
        if not spec.get("prompt", "").strip():
            raise ValueError("describe what to research")
        (ROOT/out).mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "mosa", "run", spec["prompt"], "--out", out, "--backend", spec.get("backend", "modal")]
        if spec.get("backend") == "local":  # a smaller budget per run, so a session on a few cores finishes
            command += ["--init", "96", "--children", "32", "--generations", "5", "--population", "16", "--polish", "8", "--workers", "4"]
        with open(ROOT/out/"process.log", "a") as log:
            subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        return {"id": out, "command": " ".join(command)}
    command = [sys.executable, "-m", "mosa", kind, "--out", out, "--backend", spec.get("backend", "modal"),
               "--domain", spec.get("domain", "squares"),
               "--targets", *map(str, spec["targets"]), "--seeds", *map(str, spec.get("seeds") or [0 if kind == "lab" else 1])]
    if spec.get("references"):
        command += ["--references", *map(str, spec["references"])]
    if spec.get("name"):
        command += ["--name", spec["name"]]
    (ROOT/out).mkdir(parents=True, exist_ok=True)
    if kind == "lab":
        command += ["--chains", str(int(spec.get("chains", 4))), "--rounds", str(int(spec.get("rounds", 3)))]
        if spec.get("brief"):
            brief = ROOT/out/f"brief-{time.strftime('%H%M%S')}.md"
            brief.write_text(spec["brief"])
            command += ["--brief", str(brief)]
    else:
        command += ["--idea", ":".join(map(str, spec["idea"]))]
    with open(ROOT/out/"process.log", "a") as log:
        subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return {"id": out, "command": " ".join(command)}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, *args):
        pass

    def send_json(self, value, status=200):
        body = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/api/labs":
                return self.send_json(sorted((summary(i, p) for i, p in notebooks().items()), key=lambda s: -s["started"]))
            if url.path == "/api/events":
                ev = events(notebooks()[q["lab"]])
                since = int(q.get("since", 0))
                return self.send_json({"events": ev[since:], "next": len(ev)})
            if url.path == "/api/reference":
                return self.send_json(reference(int(q["n"]), q.get("domain", "squares")))
            if url.path == "/api/records":
                return self.send_json(records())
            if url.path == "/api/targets":
                d = domain()
                return self.send_json([{"n": n, **d.info(n)} for n in d.targets()])
        except (KeyError, ValueError) as error:
            return self.send_json({"error": str(error)}, 400)
        if url.path.startswith("/api/"):
            return self.send_json({"error": "not found"}, 404)
        if url.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        try:
            spec = json.loads(self.rfile.read(length) or b"{}")
            if url.path == "/api/launch":
                return self.send_json(launch(spec))
        except (KeyError, ValueError, TypeError) as error:
            return self.send_json({"error": str(error)}, 400)
        return self.send_json({"error": "not found"}, 404)


def serve(runs="runs", port=8777):
    import threading
    threading.Thread(target=lambda: reference(1), daemon=True).start()  # load data and compile the checker before the first request
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Mosa workbench: http://127.0.0.1:{port}")
    server.serve_forever()
