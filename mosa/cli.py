"""Command line: python -m mosa {lab, apply, verify, targets, serve}.

    python -m mosa lab --targets 101-110 --chains 4 --rounds 3 --backend modal --out runs/squares
    python -m mosa apply --out runs/squares --idea 0:3:3 --targets 88 --seeds 1 2 3 --backend local
    python -m mosa apply --domain thomson --strategy baselines/thomson-basin-hopping.py --targets 300-305 --out runs/baseline
    python -m mosa serve
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

from .evaluate import Budget


def sizes(tokens):
    """Sizes from tokens like 88, 101-110 or 122-132."""
    out = []
    for token in tokens:
        for part in token.split(","):
            if "-" in part:
                a, b = map(int, part.split("-"))
                out += range(a, b+1)
            elif part:
                out.append(int(part))
    return out


def main():
    parser = argparse.ArgumentParser(prog="mosa", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("lab", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--domain", default="squares")
        p.add_argument("--targets", nargs="+", required=True, help="sizes, e.g. 88 101-110 122-132")
        p.add_argument("--seeds", type=int, nargs="+", default=[0] if name == "lab" else [1])
        p.add_argument("--backend", choices=["local", "modal"], default="modal")
        p.add_argument("--out", default=None, help="workspace directory: a new session is added if it exists (default runs/<command>-<time>)")
        p.add_argument("--name", default=None, help="workspace name")
        p.add_argument("--references", type=int, nargs="*", default=[], help="extra sizes whose best solutions strategies receive")
        p.add_argument("--workers", type=int, default=None, help="local processes (default: cores - 1)")
        for field, value in vars(Budget()).items():
            p.add_argument(f"--{field}", type=int, default=value)
    lab = sub.choices["lab"]
    lab.add_argument("--chains", type=int, default=4)
    lab.add_argument("--rounds", type=int, default=3)
    lab.add_argument("--brief", default=None, help="text file of target-specific evidence for the researchers")
    lab.add_argument("--model", default=None)
    sub.choices["apply"].add_argument("--strategy", default=None, help="a .py file with initialize and vary (e.g. a baseline)")
    sub.choices["apply"].add_argument("--idea", default=None, help="session:researcher:round of an idea in the workspace (--out)")
    runp = sub.add_parser("run", help="describe what to research; the planning agent sets up and runs the session")
    runp.add_argument("request")
    runp.add_argument("--out", default=None, help="workspace directory (default: a new one in runs/)")
    runp.add_argument("--backend", choices=["local", "modal"], default="modal")
    runp.add_argument("--workers", type=int, default=None)
    runp.add_argument("--model", default=None)
    runp.add_argument("--context", default=None, help='what the message is about, as JSON: {"idea": "0:1:2"} or {"n": 125}')
    for field in vars(Budget()):  # unset: the research agent's scale decides (quick sessions use a small budget)
        runp.add_argument(f"--{field}", type=int, default=None)
    verify = sub.add_parser("verify")
    verify.add_argument("--domain", default="squares")
    verify.add_argument("--n", type=int, required=True)
    verify.add_argument("--file", required=True, help="JSON with 'poses' (or 'x')")
    targets = sub.add_parser("targets")
    targets.add_argument("--domain", default="squares")
    serve = sub.add_parser("serve")
    serve.add_argument("--runs", default="runs")
    serve.add_argument("--port", type=int, default=8777)
    args = parser.parse_args()
    if args.command in ("run", "lab", "apply"):
        out = args.out or f"runs/{(args.command+'-') if args.command != 'run' else ''}{time.strftime('%Y%m%d-%H%M%S')}"
        os.environ["MOSA_WORKSPACE"] = Path(out).name  # tags the Modal app, so billing can be attributed to this workspace
        try:
            session(args, out)
        except BaseException as error:  # say why in the notebook, then fail loudly as before
            from .failure import record
            from .store import Notebook
            record(Notebook(out), error)
            raise
        return

    if args.command == "verify":
        from .domain import get
        data = json.loads(Path(args.file).read_text())
        certificate = get(args.domain).verify(data.get("poses", data.get("x")), args.n)
        print(json.dumps({k: v for k, v in certificate.items() if k != "poses"}, indent=1))
    elif args.command == "targets":
        from .domain import get
        domain = get(args.domain)
        for n in domain.targets():
            info = domain.info(n)
            print(f"{n:4d} {info['best_known']:.9f} {'closed form' if info.get('closed_form') else ''}")
    elif args.command == "serve":
        from .ui.server import serve
        serve(args.runs, args.port)


def session(args, out):
    """run, lab or apply: one session in the workspace at out."""
    if args.command == "run":
        from .orchestrator import run
        given = {field: getattr(args, field) for field in vars(Budget()) if getattr(args, field) is not None}
        run(args.request, out, args.backend, args.model, args.workers, Budget(**{**vars(Budget()), **given}) if given else None,
            json.loads(args.context) if args.context else None)
        print(f"workspace: {out}")
    else:
        from .research import Lab
        budget = Budget(**{field: getattr(args, field) for field in vars(Budget())})
        lab = Lab(args.domain, args.backend, out, budget, args.references, args.workers)
        if args.command == "lab":
            brief = Path(args.brief).read_text() if args.brief else ""
            lab.lab(sizes(args.targets), args.chains, args.rounds, args.seeds, brief, args.model, args.name)
        elif args.idea:
            idea = tuple(int(x) for x in args.idea.split(":"))
            lab.apply(None, f"idea {args.idea}", sizes(args.targets), args.seeds, idea, args.name)
        else:
            lab.apply(Path(args.strategy).read_text(), Path(args.strategy).stem, sizes(args.targets), args.seeds, name=args.name)
        print(f"notebook: {out}/events.jsonl")
