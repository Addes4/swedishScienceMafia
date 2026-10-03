"""Standalone HTML report (inline SVG, no dependencies) from the experiment outputs.

    python -m strategist.demo --benchmark labs --seed 1003 --trace experiments/strategist-v1/demo.json
    python -m strategist.report --dir experiments/strategist-v1
"""
import argparse
import html
import json
import math
from pathlib import Path

SLOTS = ('var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)')
NAMES = {'adaptive': 'adaptive (ours)', 'timing_shuffled': 'same moves, shuffled timing',
         'patience_best': 'best patience rule (tuned post hoc)', 'static_mix': 'static mix 0.6/0.3/0.1',
         'uniform': 'uniform random moves', 'edits_only': 'small edits only',
         'adaptive_blind': 'ablation: no stall context', 'adaptive_no_crossover': 'ablation: no crossover'}
UNITS = {'labs': 'merit factor', 'heilbronn': 'smallest triangle area', 'nk': 'fitness',
         'binpacking': 'excess bins over best-fit'}
TITLES = {'labs': 'LABS n=40', 'heilbronn': 'Heilbronn n=12', 'nk': 'NK landscape N=48 K=6',
          'binpacking': 'Online bin packing (team benchmark)'}
W, H, PAD = 640, 300, (54, 16, 30, 40)       # width, height, (left, right, bottom, top)


def esc(x): return html.escape(str(x), quote=True)


def fmt(v):
    if v == 0: return '0'
    a = abs(v)
    return f'{v:.3g}' if a >= .01 else f'{v:.2e}'


def ticks(lo, hi, n=5):
    if hi <= lo: hi = lo+1
    raw = (hi-lo)/n
    mag = 10**math.floor(math.log10(raw))
    step = min((m*mag for m in (1, 2, 2.5, 5, 10) if m*mag >= raw), default=raw)
    t = math.ceil(lo/step)*step
    out = []
    while t <= hi+1e-12: out.append(round(t, 12)); t += step
    return out


class Frame:
    """Linear scales and recessive axes for one chart."""
    def __init__(self, xlo, xhi, ylo, yhi, w=W, h=H, pad=PAD):
        span = (yhi-ylo) or abs(yhi) or 1.
        self.xlo, self.xhi, self.ylo, self.yhi = xlo, xhi, ylo-.04*span, yhi+.04*span
        self.w, self.h, (self.l, self.r, self.b, self.t) = w, h, pad

    def x(self, v): return self.l+(v-self.xlo)/(self.xhi-self.xlo or 1)*(self.w-self.l-self.r)
    def y(self, v): return self.h-self.b-(v-self.ylo)/(self.yhi-self.ylo or 1)*(self.h-self.b-self.t)

    def axes(self, xlabel, ylabel):
        out = []
        for t in ticks(self.ylo, self.yhi):
            out.append(f'<line class="grid" x1="{self.l}" x2="{self.w-self.r}" y1="{self.y(t):.1f}" y2="{self.y(t):.1f}"/>'
                       f'<text class="tick" x="{self.l-6}" y="{self.y(t)+4:.1f}" text-anchor="end">{fmt(t)}</text>')
        for t in ticks(self.xlo, self.xhi, 6):
            out.append(f'<text class="tick" x="{self.x(t):.1f}" y="{self.h-self.b+16}" text-anchor="middle">{fmt(t)}</text>')
        out.append(f'<line class="axis" x1="{self.l}" x2="{self.w-self.r}" y1="{self.h-self.b}" y2="{self.h-self.b}"/>')
        out.append(f'<text class="label" x="{self.w-self.r}" y="{self.h-4}" text-anchor="end">{esc(xlabel)}</text>')
        out.append(f'<text class="label" x="{self.l}" y="{self.t-14}">{esc(ylabel)}</text>')
        return ''.join(out)


def svg(body, w=W, h=H, label=''):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">{body}</svg>'


def curves(bench, s):
    """Median best-so-far vs cost (interquartile band for ours) for four arms."""
    arms = ['adaptive', 'timing_shuffled', 'patience_best', 'static_mix']
    data = {a: s['arms'][s['patience_best'] if a == 'patience_best' else a] for a in arms}
    budget = 3000
    xs = [budget*(i+1)/30 for i in range(30)]
    vals = [v for a in arms for v in data[a]['curve_median']]+data['adaptive']['curve_q25']+data['adaptive']['curve_q75']
    f = Frame(0, budget, min(vals), max(vals))
    body = [f.axes('cost units', UNITS[bench])]
    q25, q75 = data['adaptive']['curve_q25'], data['adaptive']['curve_q75']
    band = ' '.join(f'{f.x(x):.1f},{f.y(v):.1f}' for x, v in zip(xs, q75)) + ' ' + \
           ' '.join(f'{f.x(x):.1f},{f.y(v):.1f}' for x, v in reversed(list(zip(xs, q25))))
    body.append(f'<polygon class="band" points="{band}"/>')
    ends = []
    for slot, a in zip(SLOTS, arms):
        ys = data[a]['curve_median']
        pts = ' '.join(f'{f.x(x):.1f},{f.y(v):.1f}' for x, v in zip(xs, ys))
        body.append(f'<polyline class="line" style="stroke:{slot}" points="{pts}"/>')
        ends.append([f.y(ys[-1]), slot, a])
    ends.sort()
    for i in range(1, len(ends)): ends[i][0] = max(ends[i][0], ends[i-1][0]+20)
    overflow = ends[-1][0]-(H-PAD[2])                 # keep the stack of labels inside the plot
    if overflow > 0:
        for e in ends: e[0] -= overflow
    label = lambda a: (f"patience {s['patience_best'].split('_')[1]}" if a == 'patience_best'
                       else {'timing_shuffled': 'shuffled', 'static_mix': 'static mix'}.get(a, a))
    legend = ''.join(f'<span class="key"><i style="background:{slot}"></i>{esc(NAMES[a])}</span>'
                     for slot, a in zip(SLOTS, arms))
    cols = []
    for i, x in enumerate(xs):
        tip = f'<b>{x:.0f} cu</b>' + ''.join(f'<br>{esc(label(a))}: {fmt(data[a]["curve_median"][i])}' for a in arms)
        x0 = f.x(x-budget/60)
        cols.append(f'<rect class="col" x="{x0:.1f}" y="{f.t}" width="{f.x(budget/30)-f.x(0):.1f}" '
                    f'height="{f.h-f.b-f.t}" data-tip="{esc(tip)}" data-cx="{f.x(x):.1f}"/>')
    body.append(f'<line class="cross" x1="0" x2="0" y1="{f.t}" y2="{f.h-f.b}"/>')
    f.r = 0
    out = svg(''.join(body)+''.join(cols), label=f'{TITLES[bench]} median best-so-far by arm')
    labels = ''.join(f'<div class="end" style="top:{y/H*100:.2f}%"><i style="background:{slot}"></i>{esc(label(a))}</div>'
                     for y, slot, a in ends)
    return f'<div class="legend">{legend}</div><div class="plot">{out}<div class="ends">{labels}</div></div>'


def forest(bench, s):
    arms = ['timing_shuffled', 'patience_best', 'static_mix', 'uniform', 'edits_only',
            'adaptive_blind', 'adaptive_no_crossover']
    comps = [(a, s['comparisons'][a]['final']) for a in arms]
    lo = min(min(c['interval95'][0] for _, c in comps), 0)
    hi = max(max(c['interval95'][1] for _, c in comps), 0)
    rowh, top, left = 30, 10, 250
    h = top+rowh*len(comps)+30
    f = Frame(lo, hi, 0, 1, w=W, h=h, pad=(left, 70, 30, top))
    body = [f'<line class="zero" x1="{f.x(0):.1f}" x2="{f.x(0):.1f}" y1="{top}" y2="{h-30}"/>']
    for t in ticks(f.xlo, f.xhi, 4):
        body.append(f'<text class="tick" x="{f.x(t):.1f}" y="{h-12}" text-anchor="middle">{fmt(t)}</text>')
    for i, (a, c) in enumerate(comps):
        y = top+rowh*i+rowh/2
        name = NAMES[a] if a != 'patience_best' else f"best patience rule (T={s['patience_best'].split('_')[1]}, post hoc)"
        tip = (f'<b>{esc(name)}</b><br>adaptive minus arm: {fmt(c["mean"])}<br>95% CI {fmt(c["interval95"][0])} '
               f'to {fmt(c["interval95"][1])}<br>wins/ties/losses {c["wins"]}/{c["ties"]}/{c["losses"]}'
               f'<br>sign test p={c["sign_p"]:.2g}' + (f', Holm p={c["holm_p"]:.2g}' if 'holm_p' in c else ''))
        body.append(f'<text class="row" x="{left-10}" y="{y+4:.1f}" text-anchor="end">{esc(name)}</text>'
                    f'<line class="ci" x1="{f.x(c["interval95"][0]):.1f}" x2="{f.x(c["interval95"][1]):.1f}" y1="{y}" y2="{y}"/>'
                    f'<circle class="dot" cx="{f.x(c["mean"]):.1f}" cy="{y}" r="5"/>'
                    f'<text class="wtl" x="{W-64}" y="{y+4:.1f}">{c["wins"]}/{c["ties"]}/{c["losses"]}</text>'
                    f'<rect class="hit" x="0" y="{y-rowh/2}" width="{W}" height="{rowh}" data-tip="{esc(tip)}"/>')
    body.append(f'<text class="label" x="{W-64}" y="{top-0}" dy="-0">W/T/L</text>')
    return svg(''.join(body), h=h, label=f'{TITLES[bench]} paired differences')


def heat(bench, s):
    usage = s['adaptive_usage']
    order = ['fresh', 'warm', 'slowing', 'stuck', 'stagnant', 'frozen']
    moves = ['edit', 'rewrite', 'crossover', 'restart', 'resume']
    states = sorted(usage, key=lambda k: (k.split('/')[0] != 'lead', order.index(k.split('/')[1])))
    steps = ['var(--q1)', 'var(--q2)', 'var(--q3)', 'var(--q4)', 'var(--q5)', 'var(--q6)']
    cw, ch, left, top = 92, 24, 150, 26
    w, h = left+cw*len(moves)+10, top+ch*len(states)+8
    body = [f'<text class="label" x="{left+i*cw+cw/2}" y="{top-9}" text-anchor="middle">{m}</text>' for i, m in enumerate(moves)]
    for r, st in enumerate(states):
        n = sum(usage[st].values())
        nice = ('leader' if st.startswith('lead') else 'excursion')+', '+st.split('/')[1]
        body.append(f'<text class="row" x="{left-8}" y="{top+r*ch+ch/2+4}" text-anchor="end">{esc(nice)}</text>')
        for c, m in enumerate(moves):
            share = usage[st].get(m, 0)/n if n else 0
            k = min(5, int(share*6)) if share > 0 else -1
            fill = steps[k] if k >= 0 else 'var(--empty)'
            ink = 'var(--on-dark)' if k >= 3 else 'var(--ink2)'
            tip = f'<b>{esc(nice)}</b><br>{m}: {share:.1%} of {n} moves'
            body.append(f'<rect class="cell" x="{left+c*cw+1}" y="{top+r*ch+1}" width="{cw-2}" height="{ch-2}" rx="3" '
                        f'style="fill:{fill}" data-tip="{esc(tip)}"/>'
                        f'<text class="cellv" x="{left+c*cw+cw/2}" y="{top+r*ch+ch/2+4}" text-anchor="middle" '
                        f'style="fill:{ink}">{share:.0%}</text>' if share >= .005 else
                        f'<rect class="cell" x="{left+c*cw+1}" y="{top+r*ch+1}" width="{cw-2}" height="{ch-2}" rx="3" '
                        f'style="fill:var(--empty)" data-tip="{esc(tip)}"/>')
    return svg(''.join(body), w=w, h=h, label=f'{TITLES[bench]} learned move usage by context')


def demo_chart(d):
    tr = d['trace']
    vals = [t['working'] for t in tr]+[t['best'] for t in tr]
    f = Frame(0, d['budget'], min(vals), max(vals), h=330)
    body = [f.axes('cost units', UNITS[d['benchmark']])]
    start = None
    for t in tr:                                   # shade excursions
        on = not t['leader']
        if on and start is None: start = t['spent']
        if not on and start is not None:
            body.append(f'<rect class="exc" x="{f.x(start):.1f}" y="{f.t}" width="{f.x(t["spent"])-f.x(start):.1f}" height="{f.h-f.b-f.t}"/>')
            start = None
    if start is not None:
        body.append(f'<rect class="exc" x="{f.x(start):.1f}" y="{f.t}" width="{f.x(d["budget"])-f.x(start):.1f}" height="{f.h-f.b-f.t}"/>')
    work = ' '.join(f'{f.x(t["spent"]):.1f},{f.y(t["working"]):.1f}' for t in tr)
    best, previous = [], tr[0]['best']
    for t in tr:                                   # step function: hold the previous best until it changes
        best += [f'{f.x(t["spent"]):.1f},{f.y(previous):.1f}', f'{f.x(t["spent"]):.1f},{f.y(t["best"]):.1f}']
        previous = t['best']
    body.append(f'<polyline class="line thin" style="stroke:var(--s2)" points="{work}"/>')
    body.append(f'<polyline class="line" style="stroke:var(--s1)" points="{" ".join(best)}"/>')
    for t in tr:
        if t['op'] == 'restart':
            body.append(f'<line class="tickmark" x1="{f.x(t["spent"]):.1f}" x2="{f.x(t["spent"]):.1f}" y1="{f.h-f.b}" y2="{f.h-f.b-8}"/>')
    tips = []
    for e in d['events']:
        x = f.x(e['spent'])
        tips.append(f'<rect class="hit" x="{x-3:.1f}" y="{f.t}" width="6" height="{f.h-f.b-f.t}" data-tip="{esc("<b>"+fmt(e["spent"])+" cu</b><br>"+esc(e["text"]))}"/>')
    return svg(''.join(body)+''.join(tips), h=330, label='single run timeline')


def table(bench, s):
    sign = 1 if s['higher_is_better'] else -1
    rows = sorted(s['arms'].items(), key=lambda kv: -sign*kv[1]['mean'])
    out = ['<table><thead><tr><th>arm</th><th>mean</th><th>median</th><th>anytime (AUC)</th>'
           '<th>restarts/run</th><th>adaptive − arm</th><th>95% CI</th><th>W/T/L</th><th>p (Holm)</th></tr></thead><tbody>']
    for arm, a in rows:
        c = s['comparisons'].get(arm, {}).get('final')
        if arm == s['patience_best']: c = s['comparisons']['patience_best']['final']
        diff = (f'<td>{fmt(c["mean"])}</td><td>{fmt(c["interval95"][0])} to {fmt(c["interval95"][1])}</td>'
                f'<td>{c["wins"]}/{c["ties"]}/{c["losses"]}</td>'
                f'<td>{c["sign_p"]:.2g}' + (f' ({c["holm_p"]:.2g})' if 'holm_p' in c else '') + '</td>') if c else '<td colspan="4">—</td>'
        out.append(f'<tr{" class=ours" if arm == "adaptive" else ""}><td>{esc(NAMES.get(arm, arm.replace("_", " ")))}</td>'
                   f'<td>{fmt(a["mean"])}</td><td>{fmt(a["median"])}</td><td>{fmt(a["auc"])}</td>'
                   f'<td>{a["restarts_per_run"]:.1f}</td>{diff}</tr>')
    return ''.join(out)+'</tbody></table>'


def forks_section(fk):
    if not fk: return ''
    s, w = fk['summary'], fk['config']['window']
    benches = list(s)
    gw, bw, left, top, h = 180, 56, 60, 30, 260
    width = left+gw*len(benches)+20
    f = Frame(0, 1, 0, max(max(s[b]['p_improve'].values()) for b in benches), w=width, h=h, pad=(left, 20, 40, top))
    body = []
    for t in ticks(0, f.yhi, 4):
        body.append(f'<line class="grid" x1="{left}" x2="{width-20}" y1="{f.y(t):.1f}" y2="{f.y(t):.1f}"/>'
                    f'<text class="tick" x="{left-6}" y="{f.y(t)+4:.1f}" text-anchor="end">{t:.0%}</text>')
    for i, b in enumerate(benches):
        for j, (arm, slot) in enumerate((('switch', SLOTS[0]), ('stay', SLOTS[1]))):
            v = s[b]['p_improve'][arm]
            x = left+gw*i+gw/2-bw-1+j*(bw+2)
            y = f.y(v)
            tip = (f'<b>{TITLES[b]}</b><br>{"follow the controller" if arm == "switch" else "stay with small edits"}: '
                   f'{v:.1%} of forks found a new best within {w:g} cu<br>{s[b]["moments"]} switch points, {s[b]["seeds"]} seeds')
            body.append(f'<path class="bar" style="fill:{slot}" d="M{x:.1f},{f.h-f.b} V{y+4:.1f} q0,-4 4,-4 H{x+bw-4:.1f} q4,0 4,4 V{f.h-f.b} Z" data-tip="{esc(tip)}"/>'
                        f'<text class="cellv" x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" style="fill:var(--ink)">{v:.0%}</text>')
        body.append(f'<text class="row" x="{left+gw*i+gw/2:.1f}" y="{h-18}" text-anchor="middle">{esc(TITLES[b].split(" ")[0])}</text>')
    legend = (f'<div class="legend"><span class="key"><i style="background:{SLOTS[0]}"></i>follow the controller (switch)</span>'
              f'<span class="key"><i style="background:{SLOTS[1]}"></i>stay on the line with small edits</span></div>')
    rows = ''.join(f'<tr><td>{TITLES[b]}</td><td>{s[b]["moments"]}</td><td>{s[b]["p_improve"]["switch"]:.1%}</td>'
                   f'<td>{s[b]["p_improve"]["stay"]:.1%}</td><td>{s[b]["p_improve_difference"]["mean"]:+.1%}</td>'
                   f'<td>{s[b]["p_improve_difference"]["interval95"][0]:+.1%} to {s[b]["p_improve_difference"]["interval95"][1]:+.1%}</td></tr>'
                   for b in benches)
    return (f'<section><h2>Counterfactual forks: was the progress after a switch luck?</h2>'
            f'<p>At every moment the controller left the leader line, the whole search state was copied. '
            f'{fk["config"]["forks"]} forks followed the controller and {fk["config"]["forks"]} stayed on the line with small edits, '
            f'each with its own random stream, for {w:g} cost units. Bars show the share of forks that found a new overall best.</p>'
            f'{legend}<div class="plot">{svg("".join(body), w=width, h=h, label="fork outcomes")}</div>'
            f'<details><summary>Table</summary><table><thead><tr><th>benchmark</th><th>switch points</th><th>P(new best), switch</th>'
            f'<th>P(new best), stay</th><th>difference</th><th>95% CI</th></tr></thead><tbody>{rows}</tbody></table></details></section>')


CSS = """
:root{color-scheme:light;--bg:#fcfcfb;--panel:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--rule:#e4e3df;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--band:rgba(42,120,214,.13);--exc:rgba(235,104,52,.08);
--q1:#cde2fb;--q2:#9ec5f4;--q3:#6da7ec;--q4:#3987e5;--q5:#256abf;--q6:#104281;--empty:#f3f2ef;--on-dark:#ffffff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#1a1a19;--panel:#222221;--ink:#ffffff;
--ink2:#c3c2b7;--muted:#8f8e86;--rule:#383835;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--band:rgba(57,135,229,.18);
--exc:rgba(217,89,38,.12);--q1:#104281;--q2:#184f95;--q3:#256abf;--q4:#3987e5;--q5:#6da7ec;--q6:#b7d3f6;--empty:#2a2a28;--on-dark:#0b0b0b}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#1a1a19;--panel:#222221;--ink:#ffffff;--ink2:#c3c2b7;--muted:#8f8e86;--rule:#383835;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--band:rgba(57,135,229,.18);--exc:rgba(217,89,38,.12);
--q1:#104281;--q2:#184f95;--q3:#256abf;--q4:#3987e5;--q5:#6da7ec;--q6:#b7d3f6;--empty:#2a2a28;--on-dark:#0b0b0b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1060px;margin:0 auto;padding:28px 16px 60px}h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 8px}
h3{font-size:15px;margin:18px 0 6px}p,li{color:var(--ink2);max-width:76ch}.sub{color:var(--ink2);margin:0 0 18px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,470px),1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 14px 8px;min-width:0}
svg{width:100%;height:auto;display:block;overflow:visible}.plot{position:relative}
.grid{stroke:var(--rule);stroke-width:1}.axis{stroke:var(--muted);stroke-width:1}.zero{stroke:var(--muted);stroke-dasharray:3 3}
.tick,.label,.row,.wtl,.cellv{font-size:11px;fill:var(--ink2)}.label{fill:var(--muted)}.row{font-size:12px;fill:var(--ink)}
.line{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}.thin{stroke-width:1.2;opacity:.8}
.band{fill:var(--band)}.exc{fill:var(--exc)}.tickmark{stroke:var(--s2);stroke-width:2}
.ci{stroke:var(--s1);stroke-width:2;stroke-linecap:round}.dot{fill:var(--s1);stroke:var(--panel);stroke-width:2}
.col,.hit{fill:transparent}.cross{stroke:var(--muted);stroke-width:1;opacity:0}.cell{stroke:none}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--ink2);margin:2px 0 6px}
.key i,.end i{display:inline-block;width:10px;height:3px;border-radius:2px;margin-right:6px;vertical-align:middle}
.ends{position:absolute;inset:0;pointer-events:none}.end{position:absolute;right:-2px;transform:translate(100%,-50%);font-size:11px;
color:var(--ink2);white-space:nowrap;display:none}
@media (min-width:1100px){.end{display:block}}
#tip{position:fixed;pointer-events:none;background:var(--panel);color:var(--ink);border:1px solid var(--rule);border-radius:8px;
padding:7px 9px;font-size:12px;line-height:1.4;box-shadow:0 4px 14px rgba(0,0,0,.12);opacity:0;max-width:320px;z-index:5}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:8px 0}th,td{text-align:right;padding:5px 8px;border-bottom:1px solid var(--rule);white-space:nowrap}
th:first-child,td:first-child{text-align:left}th{color:var(--muted);font-weight:600}tr.ours td{font-weight:600}
.tablewrap{overflow-x:auto}details{margin:6px 0 4px}summary{cursor:pointer;color:var(--ink2);font-size:13px}
.findings{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px;margin:16px 0}
.finding{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:12px}
.finding b{display:block;font-size:22px;color:var(--ink)}.finding span{font-size:12.5px;color:var(--ink2)}
pre{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:10px;overflow-x:auto;font-size:12px;color:var(--ink2)}
code{font-size:12.5px}.verdict td{text-align:left;white-space:normal;vertical-align:top}.verdict small{color:var(--muted)}
"""

JS = """
const tip=document.getElementById('tip');
document.addEventListener('pointermove',e=>{const t=e.target.closest('[data-tip]');
 document.querySelectorAll('.cross').forEach(c=>c.style.opacity=0);
 if(!t){tip.style.opacity=0;return}
 tip.innerHTML=t.dataset.tip;tip.style.opacity=1;
 const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8),y=Math.min(e.clientY+14,innerHeight-tip.offsetHeight-8);
 tip.style.left=x+'px';tip.style.top=y+'px';
 if(t.dataset.cx){const c=t.ownerSVGElement.querySelector('.cross');c.setAttribute('x1',t.dataset.cx);c.setAttribute('x2',t.dataset.cx);c.style.opacity=.7}});
"""


def findings(summary):
    out = []
    for bench, s in summary.items():
        c = s['comparisons']['timing_shuffled']['final']
        out.append(f'<div class="finding"><span>{esc(TITLES[bench])}: adaptive vs. same moves at shuffled times</span>'
                   f'<b>{c["wins"]}–{c["losses"]}</b><span>seed wins–losses ({c["ties"]} ties), Holm p={c["holm_p"]:.2g}</span></div>')
    return '<div class="findings">'+''.join(out)+'</div>'


def verdicts(summary):
    """The five pre-registered comparisons per benchmark, judged at Holm-adjusted p < 0.05."""
    head = ''.join(f'<th>{esc(TITLES[b].split(" (")[0])}</th>' for b in summary)
    rows = []
    for arm in ('timing_shuffled', 'static_mix', 'uniform', 'edits_only', 'patience_best'):
        cells = []
        for bench, s in summary.items():
            c = s['comparisons'][arm]['final']
            word = ('better' if c['mean'] > 0 else 'worse') if c['holm_p'] < .05 else 'no clear difference'
            arrow = {'better': '▲ ', 'worse': '▼ '}.get(word, '')
            cells.append(f'<td title="mean difference {fmt(c["mean"])}, Holm p={c["holm_p"]:.2g}">{arrow}{word}'
                         f'<br><small>{c["wins"]}/{c["ties"]}/{c["losses"]}, p={c["holm_p"]:.2g}</small></td>')
        name = NAMES[arm] if arm != 'patience_best' else 'best patience rule (tuned post hoc)'
        rows.append(f'<tr><td>{esc(name)}</td>{"".join(cells)}</tr>')
    return (f'<section><h2>Verdict on the pre-registered comparisons</h2><p>Adaptive versus each arm, at the end of the '
            f'budget: better or worse when the Holm-adjusted sign test gives p &lt; 0.05. Small print: seed wins/ties/losses.</p>'
            f'<div class="tablewrap"><table class="verdict"><thead><tr><th>adaptive versus</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></section>')


def build(directory):
    d = Path(directory)
    summary = json.loads((d/'summary.json').read_text())
    forks = json.loads((d/'forks.json').read_text()) if (d/'forks.json').exists() else None
    demo = json.loads((d/'demo.json').read_text()) if (d/'demo.json').exists() else None
    seeds = next(iter(summary.values()))['seeds']
    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
             f'<title>Strategist results</title><style>{CSS}</style></head><body><main>'
             f'<h1>Strategist</h1><p class="sub">Learning when to change research strategy: small edits, rewrites, crossover and restarts, '
             f'chosen from progress and cost. Equal-cost, seed-paired comparison, {seeds} confirmatory seeds per benchmark.</p>',
             findings(summary), verdicts(summary),
             '<section><h2>How it decides</h2><ul>'
             '<li><b>Leave the best line</b> (restart) when its expected yield, P(improve) × typical gain ÷ cost of its best move in the '
             'current stall context, falls below the progress per cost that past excursions delivered. This is the marginal value theorem: '
             'leave a patch when its marginal rate drops below the average rate of the habitat.</li>'
             '<li><b>Abandon an excursion</b> once it has stalled as long as the leader had when it was left, and resume the best line.</li>'
             '<li><b>Within a line</b>, choose edit, rewrite or crossover by Thompson sampling on the same yield, per context.</li>'
             '<li>Failed excursions lower the exploration estimate, so the leader is given more patience. '
             'The estimate is forgotten exponentially in cost, so the controller tries again later.</li></ul></section>']
    if demo:
        restarts = sum(t['op'] == 'restart' for t in demo['trace'])
        log = '\n'.join(f'{e["spent"]:7.0f}  {e["text"]}' for e in demo['events'])
        parts.append(f'<section><h2>One run, narrated ({esc(TITLES[demo["benchmark"]])}, seed {demo["seed"]})</h2>'
                     f'<p>Blue: best so far. Orange: the line being worked on. Shaded: excursions. Ticks: the {restarts} restarts. '
                     f'Hover over the event markers for the controller\'s reasons.</p>'
                     f'<div class="legend"><span class="key"><i style="background:var(--s1)"></i>best so far</span>'
                     f'<span class="key"><i style="background:var(--s2)"></i>working line</span></div>'
                     f'<div class="card">{demo_chart(demo)}</div>'
                     f'<details><summary>Event log</summary><pre>{esc(log)}</pre></details></section>')
    parts.append('<section><h2>Best so far against cost (median over seeds; band = interquartile range for adaptive)</h2><div class="grid2">')
    for bench, s in summary.items():
        parts.append(f'<div class="card"><h3>{esc(TITLES[bench])}</h3>{curves(bench, s)}</div>')
    parts.append('</div></section><section><h2>Paired differences at the end of the budget</h2>'
                 '<p>Each dot is the mean over seeds of adaptive minus that arm, oriented so that right means adaptive did better. '
                 'Lines are 95% bootstrap intervals. W/T/L counts per-seed wins, ties and losses for adaptive.</p><div class="grid2">')
    for bench, s in summary.items():
        parts.append(f'<div class="card"><h3>{esc(TITLES[bench])}</h3>{forest(bench, s)}</div>')
    parts.append('</div></section>')
    parts.append(forks_section(forks))
    parts.append('<section><h2>What it learned: share of each move, by context (adaptive, pooled over seeds)</h2><div class="grid2">')
    for bench, s in summary.items():
        parts.append(f'<div class="card"><h3>{esc(TITLES[bench])}</h3>{heat(bench, s)}</div>')
    parts.append('</div></section><section><h2>All numbers</h2>')
    for bench, s in summary.items():
        parts.append(f'<h3>{esc(TITLES[bench])} ({UNITS[bench]}, {"higher" if s["higher_is_better"] else "lower"} is better)</h3>'
                     f'<div class="tablewrap">{table(bench, s)}</div>')
    parts.append('</section><section><h2>Reproduce</h2><pre>python3 -m strategist.experiment --seeds 1000:1200 --out experiments/strategist-v1\n'
                 'python3 -m strategist.forks --seeds 2000:2040 --out experiments/strategist-v1\n'
                 'python3 -m strategist.demo --benchmark labs --seed 1003 --trace experiments/strategist-v1/demo.json\n'
                 'python3 -m strategist.report --dir experiments/strategist-v1</pre>'
                 '<p>Pre-registration and disclosed development changes: <code>strategist/PROTOCOL.md</code>. '
                 'Development seeds overstated the controller on LABS: seeds 0-19 gave a mean merit factor of 4.29, while '
                 'never-used seeds 20-39 give 3.92, in line with the confirmatory 3.96. Choosing among about 15 variants '
                 'on 20 seeds produced a winner\'s curse, which the confirmatory run exposed.</p></section>'
                 f'</main><div id="tip"></div><script>{JS}</script></body></html>')
    (d/'report.html').write_text(''.join(parts))
    return d/'report.html'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='experiments/strategist-v1')
    print(build(parser.parse_args().dir))


if __name__ == '__main__': main()
