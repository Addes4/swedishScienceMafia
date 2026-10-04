"use strict";
// Mosa workbench. State comes from lab notebooks (append-only event lists); every view is rebuilt from a model of
// those events, so a live lab and a replay of a finished one use the same code.

const $ = (s, el = document) => el.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const attr = (v) => esc(JSON.stringify(v));

const ICON = {
  labs: '<path d="M9 3h6M10 3v6l-5.6 9.6A1.6 1.6 0 0 0 5.8 21h12.4a1.6 1.6 0 0 0 1.4-2.4L14 9V3"/><path d="M7.5 15h9"/>',
  records: '<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/>',
  library: '<path d="M5 4h4v16H5zM10 4h4v16h-4z"/><path d="M15.5 4.6l3.8-1 3.7 15.4-3.9 1z"/>',
  targets: '<path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4z"/><path d="M14.6 17l2.4-2.4 2.4 2.4-2.4 2.4z"/>',
  launch: '<path d="M7 4.5l12 7.5-12 7.5z"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.3-4.3"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/>',
  moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
  chev: '<path d="M9 6l6 6-6 6"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  x: '<path d="M7 7l10 10M17 7L7 17"/>',
  play: '<path d="M8 5.5l10 6.5-10 6.5z"/>',
  pause: '<path d="M8 5h3v14H8zM13 5h3v14h-3z"/>',
  replay: '<path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 4v4.5h4.5"/>',
  doc: '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/>',
  download: '<path d="M12 4v11M7 10.5l5 5 5-5M5 20h14"/>',
  home: '<path d="M4 11l8-7 8 7v9H4z"/>',
  panel: '<path d="M4 5h16v14H4zM4 15h16"/>',
};
const icon = (name, extra = "") => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" ${extra}>${ICON[name]}</svg>`;
const BRAND = `<svg viewBox="0 0 24 24" width="22" height="22"><rect x="3" y="3" width="8" height="8" rx="1.2" fill="var(--accent)"/><rect x="13" y="3" width="8" height="8" rx="1.2" fill="var(--faint)"/><rect x="3" y="13" width="8" height="8" rx="1.2" fill="var(--faint)"/><rect x="13.2" y="13.2" width="7.6" height="7.6" rx="1.2" fill="var(--text-strong)" transform="rotate(22 17 17)"/></svg>`;

const S = {
  activity: "labs", labs: [], records: [], targets: [], library: [], briefs: [],
  books: {}, tabs: [], active: null, open: {}, panel: "progress", currentLab: null,
  replay: null, refs: {}, palette: { items: [], index: 0 }, launchKind: "lab", launchBackend: "modal",
};

// ---------- data ----------
const api = async (path, body) => {
  const response = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || response.statusText);
  return data;
};

async function loadBook(id) {
  const book = S.books[id] || (S.books[id] = { events: [], next: 0, model: null });
  const data = await api(`/api/events?lab=${encodeURIComponent(id)}&since=${book.next}`);
  if (data.events.length || !book.model) {
    book.events.push(...data.events);
    book.next = data.next;
    book.model = buildModel(book.events);
    return true;
  }
  return false;
}

async function ensureRef(n) {
  if (S.refs[n]) return S.refs[n];
  S.refs[n] = "loading";
  S.refs[n] = await api(`/api/reference?n=${n}`);
  render();
  return S.refs[n];
}

function buildModel(events, until = Infinity) {
  const m = { lab: null, chains: new Map(), records: [], errors: [], done: false, start: null, end: null, results: 0, library: [] };
  const round = (e) => {
    const c = e.chain ?? 0, k = e.round ?? 1;
    if (!m.chains.has(c)) m.chains.set(c, { index: c, rounds: new Map() });
    const ch = m.chains.get(c);
    if (!ch.rounds.has(k)) ch.rounds.set(k, { chain: c, round: k, results: [], records: [], progress: {}, prompt: null, strategy: null, done: null, error: null });
    return ch.rounds.get(k);
  };
  for (const e of events) {
    if (e.time > until) continue;
    if (m.start === null || e.time < m.start) m.start = e.time;
    if (m.end === null || e.time > m.end) m.end = e.time;
    switch (e.type) {
      case "lab": m.lab = e; break;
      case "prompt": round(e).prompt = e; break;
      case "strategy": round(e).strategy = e; break;
      case "progress": round(e).progress[`${e.n}/${e.seed}`] = e; break;
      case "result": { const r = round(e); r.results.push(e); delete r.progress[`${e.n}/${e.seed}`]; m.results++; break; }
      case "record": round(e).records.push(e); m.records.push(e); break;
      case "round": round(e).done = e; break;
      case "error": m.errors.push(e); if (e.chain !== undefined) round(e).error = e; break;
      case "library": m.library.push(e); break;
      case "done": m.done = true; break;
    }
  }
  return m;
}

const modelOf = (id) => {
  const book = S.books[id];
  if (!book) return null;
  if (S.replay && S.replay.lab === id) return buildModel(book.events, S.replay.t);
  return book.model;
};
const summaryOf = (id) => S.labs.find((l) => l.id === id);

// ---------- formatting ----------
const fmtSide = (v) => (v == null ? "—" : Number(v).toFixed(9));
const fmtGap = (v) => {
  if (v == null || Number.isNaN(v)) return "—";
  if (Math.abs(v) < 1e-9) return "0";
  const s = Math.abs(v).toExponential(1).replace("e-", "e−");
  return (v < 0 ? "−" : "+") + s;
};
const fmtTime = (t) => (t ? new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "—");
const fmtDur = (s) => (s < 90 ? `${Math.round(s)} s` : s < 5400 ? `${Math.round(s / 60)} min` : `${(s / 3600).toFixed(1)} h`);
const span = (ns) => {
  const t = [...ns].sort((a, b) => a - b);
  if (!t.length) return "";
  const parts = [];
  let a = t[0], b = t[0];
  for (const n of t.slice(1).concat([null])) {
    if (n === b + 1) { b = n; continue; }
    parts.push(a === b ? `${a}` : `${a}–${b}`);
    a = b = n;
  }
  return parts.join(", ");
};
const prettyName = (s) => {
  if (!s) return "";
  const m = s.name.match(/^(\d{4}-\d{2}-\d{2})-(.*)$/);
  if (m) return m[2].replace(/-/g, " ");
  const r = s.name.match(/^(lab|apply)-(\d{8})-(\d{2})(\d{2})(\d{2})$/);
  if (r) return `${r[1] === "lab" ? "research lab" : "apply"} · ${r[3]}:${r[4]}`;
  return s.name.replace(/-/g, " ");
};
const ideaTitle = (src) => {
  if (!src) return "";
  let t = src.split(/:\s|\s—\s|;\s/)[0].trim();
  if (t.length > 96) t = t.slice(0, 93).replace(/\s+\S*$/, "") + "…";
  return t;
};
const researcher = (c) => `Researcher ${c + 1}`;
const seedsOf = (lab) => (lab && lab.seeds && lab.seeds.length ? lab.seeds : [0]);
const expectedRuns = (lab) => (lab ? (lab.targets || []).length * seedsOf(lab).length : 0);
const verified = (r) => r.records.filter((x) => x.record);
const nearMiss = (results) => {
  const v = results.map((x) => x.runner_up_gap).filter((x) => x != null && x > 0);
  return v.length ? Math.min(...v) : null;
};
const cellClass = (x) => (x.error ? "err" : x.record ? "rec" : x.runner_up_gap == null ? "held" : "");
const cellStyle = (x) => {
  if (x.error || x.record || x.runner_up_gap == null) return "";
  const a = Math.max(0.12, Math.min(1, (Math.log10(Math.max(x.runner_up_gap, 1e-7)) + 1) / -5));
  return `background: color-mix(in srgb, var(--near) ${Math.round(a * 100)}%, transparent)`;
};
const cellTip = (x) => x.error ? `n=${x.n} seed ${x.seed}\nerror: ${String(x.error).split("\n").filter(Boolean).slice(-1)[0]}` :
  `n=${x.n} seed ${x.seed}\npolished ${fmtSide(x.polished)}\ngap ${fmtGap(x.gap)}\nnear miss ${fmtGap(x.runner_up_gap)}\ninitial ${fmtGap(x.initial_gap)}`;
const roundState = (r) => (r.error ? "failed" : r.done ? "done" : r.strategy ? "running" : r.prompt ? "thinking" : "waiting");

// ---------- packings ----------
function packingSVG(poses, side, highlight = null) {
  const sw = side * 0.0022;
  let out = `<svg viewBox="${-sw} ${-sw} ${side + 2 * sw} ${side + 2 * sw}" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="${side}" height="${side}" fill="#fff" stroke="#000" stroke-width="${sw}"/>`;
  poses.forEach(([x, y, a], i) => {
    const fill = highlight && highlight[i] ? "#e7a07d" : "#B2B2B2";
    out += `<rect x="-0.5" y="-0.5" width="1" height="1" transform="translate(${x} ${side - y}) rotate(${(-a * 180) / Math.PI})" fill="${fill}" stroke="#000" stroke-width="${sw}"/>`;
  });
  return out + "</svg>";
}

function catalogueSVG(poses, side, comment) {
  const uses = poses.map(([x, y, a]) => `        <use xlink:href="#one" transform="translate(${x} ${side - y}) rotate(${(-a * 180) / Math.PI}) translate(-0.5 -0.5)"/>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<!--\n${comment}\n-->\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" [\n    <!ENTITY  s "${side}">\n    <!ENTITY hs  "${side / 2}">\n]>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="100%" viewBox="-&hs; -&hs; &s; &s;" style="fill:#B2B2B2; stroke:black; stroke-width:0.002" id="svg">\n    <defs>\n        <rect width="&s;" height="&s;" id="outer" x="-&hs;" y="-&hs;"/>\n        <rect width="1"   height="1"   id="one"/>\n    </defs>\n    <use xlink:href="#outer" style="fill:white; stroke:none"/>\n    <g transform="translate(-&hs; -&hs;)">\n${uses}\n    </g>\n    <use xlink:href="#outer" style="fill:none"/>\n</svg>\n`;
}

// Squares of `after` with no counterpart in `before` (best of the 8 symmetries of the square).
function changed(after, sa, before, sb) {
  let best = null;
  for (let k = 0; k < 8; k++) {
    const moved = after.map(([x, y]) => {
      let u = x - sa / 2, v = y - sa / 2;
      if (k & 4) u = -u;
      for (let r = 0; r < (k & 3); r++) [u, v] = [-v, u];
      return [u + sb / 2, v + sb / 2];
    });
    const flags = moved.map(([x, y]) => !before.some(([p, q]) => (p - x) ** 2 + (q - y) ** 2 < 0.0025));
    const count = flags.filter(Boolean).length;
    if (!best || count < best.count) best = { flags, count };
  }
  return best;
}

const download = (name, text, type) => {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
};

// ---------- tabs ----------
function openTab(type, args = {}, title = "") {
  const key = `${type}:${JSON.stringify(args)}`;
  if (!S.tabs.find((t) => t.key === key)) S.tabs.push({ key, type, args, title });
  S.active = key;
  if (args.lab) S.currentLab = args.lab;
  if (args.lab && !S.books[args.lab]) loadBook(args.lab).then(render);
  render();
  $("#content").scrollTop = 0;
}
function closeTab(key) {
  const i = S.tabs.findIndex((t) => t.key === key);
  if (i < 0) return;
  S.tabs.splice(i, 1);
  if (S.active === key) S.active = S.tabs.length ? S.tabs[Math.max(0, i - 1)].key : null;
  render();
}
const activeTab = () => S.tabs.find((t) => t.key === S.active);
const tabIcon = { welcome: "home", lab: "labs", round: "doc", record: "records", target: "targets", library: "library", launch: "launch" };
function tabTitle(t) {
  const lab = summaryOf(t.args.lab);
  switch (t.type) {
    case "welcome": return "Welcome";
    case "lab": return prettyName(lab) || t.args.lab;
    case "round": return `${researcher(t.args.chain)} · round ${t.args.round}`;
    case "record": return `Record n = ${t.args.n}`;
    case "target": return `n = ${t.args.n}`;
    case "library": return "Strategy library";
    case "launch": return "New lab";
  }
  return t.title;
}

// ---------- shell ----------
function renderActivity() {
  const items = [["labs", "Labs"], ["records", "Records"], ["library", "Strategy library"], ["targets", "Problem sizes"], ["launch", "New lab"]];
  $("#activity").innerHTML = `<div class="brand" title="Mosa">${BRAND}</div>` +
    items.map(([k, label]) => `<button class="${S.activity === k ? "on" : ""}" data-act="activity" data-k="${k}" title="${label}">${icon(k)}${k === "records" && S.records.length ? `<span class="badge">${S.records.length}</span>` : ""}</button>`).join("") +
    `<div class="spacer"></div><button data-act="palette" title="Search (⌘K)">${icon("search")}</button>` +
    `<button data-act="theme" title="Toggle theme">${icon(document.documentElement.dataset.theme === "light" ? "moon" : "sun")}</button>`;
}

function labRow(l) {
  const book = S.books[l.id];
  const open = S.open[l.id];
  const n = Object.keys(l.records).length;
  let html = `<div class="row ${S.currentLab === l.id && activeTab()?.type === "lab" ? "active" : ""}" style="padding-left:8px" data-act="lab" data-lab="${esc(l.id)}">
    <span class="chev ${open ? "open" : ""}" data-act="toggle" data-node="${esc(l.id)}">${icon("chev")}</span>
    <span class="dot ${l.running ? "live" : n ? "record" : ""}"></span>
    <span class="label">${esc(prettyName(l))}</span>${n ? `<span class="meta star">★ ${n}</span>` : ""}</div>`;
  if (open && book && book.model) {
    const m = modelOf(l.id);
    for (const ch of [...m.chains.values()].sort((a, b) => a.index - b.index)) {
      if (l.kind === "lab") html += `<div class="row" style="padding-left:30px;color:var(--muted)"><span class="label">${researcher(ch.index)}</span></div>`;
      for (const r of [...ch.rounds.values()].sort((a, b) => a.round - b.round)) {
        const st = roundState(r), v = verified(r).length;
        const sel = activeTab()?.type === "round" && activeTab().args.lab === l.id && activeTab().args.chain === r.chain && activeTab().args.round === r.round;
        html += `<div class="row ${sel ? "active" : ""}" style="padding-left:${l.kind === "lab" ? 44 : 30}px" data-act="round" data-lab="${esc(l.id)}" data-chain="${r.chain}" data-round="${r.round}">
          <span class="ico">${st === "running" || st === "thinking" ? '<span class="spinner"></span>' : `<span class="dot ${v ? "record" : st === "failed" ? "error" : ""}"></span>`}</span>
          <span class="label"><span class="mono" style="color:var(--faint)">r${r.round}</span> ${esc(ideaTitle(r.strategy?.source) || (st === "thinking" ? "thinking…" : ""))}</span>${v ? `<span class="meta star">★ ${v}</span>` : ""}</div>`;
      }
    }
  }
  return html;
}

function renderSidebar() {
  const titles = { labs: "Labs", records: "Verified records", library: "Strategy library", targets: "Problem sizes", launch: "New lab" };
  $("#sidebar-title").innerHTML = `<span>${titles[S.activity]}</span>`;
  let html = "";
  if (S.activity === "labs") {
    for (const [folder, label] of [["runs", "Runs"], ["history", "History"]]) {
      const labs = S.labs.filter((l) => l.folder === folder);
      html += `<div class="tree-section"><div class="tree-head">${label}<span style="margin-left:auto;font-weight:400">${labs.length}</span></div>`;
      html += labs.length ? labs.map(labRow).join("") : `<div class="empty">${folder === "runs" ? "No labs yet: start one from New lab." : ""}</div>`;
      html += "</div>";
    }
  } else if (S.activity === "records") {
    html = S.records.length ? S.records.map((r) => `<div class="row ${activeTab()?.type === "record" && activeTab().args.n === r.n ? "active" : ""}" style="padding-left:16px" data-act="record" data-n="${r.n}">
      <span class="star">★</span><span class="label">n = ${r.n}</span><span class="meta">${fmtGap(-r.improvement)}</span></div>`).join("") : `<div class="empty">No verified records yet.</div>`;
  } else if (S.activity === "library") {
    html = S.library.map((e, i) => `<div class="row" style="padding-left:16px" data-act="library" data-i="${i}"><span class="label">${esc(ideaTitle(e.source))}</span><span class="meta star">★ ${Object.keys(e.records_broken || {}).length}</span></div>`).join("") || `<div class="empty">Empty.</div>`;
  } else if (S.activity === "targets") {
    const best = Object.fromEntries(S.records.map((r) => [r.n, r]));
    html = S.targets.map((t) => `<div class="row ${activeTab()?.type === "target" && activeTab().args.n === t.n ? "active" : ""}" style="padding-left:16px" data-act="target" data-n="${t.n}">
      <span class="label"><span class="mono">${String(t.n).padStart(3, " ")}</span>${t.closed_form ? ' <span style="color:var(--faint)">closed form</span>' : ""}</span>${best[t.n] ? '<span class="meta star">★</span>' : ""}<span class="meta mono">${Number(t.best_known).toFixed(4)}</span></div>`).join("");
  } else if (S.activity === "launch") {
    html = `<div class="empty" style="padding-top:4px">Briefs</div>` + S.briefs.map((b) => `<div class="row" style="padding-left:16px" data-act="brief" data-name="${esc(b.name)}"><span class="ico">${icon("doc", 'width="14"')}</span><span class="label">${esc(b.name)}</span></div>`).join("");
  }
  $("#explorer").innerHTML = html;
}

function renderTabs() {
  $("#tabs").innerHTML = S.tabs.map((t) => `<div class="tab ${t.key === S.active ? "on" : ""}" data-act="tab" data-key="${esc(t.key)}" role="tab">
    ${icon(tabIcon[t.type] || "doc")}<span class="t">${esc(tabTitle(t))}</span><span class="x" data-act="close" data-key="${esc(t.key)}">${icon("x", 'width="12" height="12"')}</span></div>`).join("");
}

// ---------- views ----------
const VIEWS = {};

VIEWS.welcome = () => {
  const strategies = Object.values(S.books).reduce((a, b) => a + b.events.filter((e) => e.type === "strategy").length, 0);
  const runs = Object.values(S.books).reduce((a, b) => a + b.events.filter((e) => e.type === "result").length, 0);
  return `<div class="hero">
    <div style="display:flex;gap:12px;align-items:center;margin-bottom:12px">${BRAND.replace('width="22" height="22"', 'width="34" height="34"')}<h1 style="margin:0">Mosa</h1></div>
    <p class="lede" style="font-size:14px">An autoresearch workbench. LLM researchers write <b>search strategies</b> as code, drawing on methods from other
    fields; trusted tools run every strategy at equal budget on many problem sizes and seeds; nothing counts until it is independently verified.
    Researchers see their near misses and refine, combine or replace their ideas.</p>
    <div class="stats">
      <div class="card stat"><div class="v star">${S.records.length}</div><div class="k">verified new best-known packings</div></div>
      <div class="card stat"><div class="v">${S.labs.length}</div><div class="k">labs</div></div>
      <div class="card stat"><div class="v">${strategies}</div><div class="k">strategies written</div></div>
      <div class="card stat"><div class="v">${runs.toLocaleString()}</div><div class="k">evaluated runs</div></div>
    </div>
    <h2>How it works</h2>
    <div class="how">
      <div class="card"><h3>${icon("labs", 'width="16"')} Researchers write strategies</h3><p>Each round a researcher reads the evidence, its past results and near misses, and the library, then writes <code>initialize</code> and <code>vary</code> for an evolutionary template.</p></div>
      <div class="card"><h3>${icon("targets", 'width="16"')} Tools test them fairly</h3><p>Sandboxed strategy code makes candidates; compiled relaxation and an exact SQP polish find the basins, at the same budget for every strategy, on Modal or locally.</p></div>
      <div class="card"><h3>${icon("records", 'width="16"')} Only verified results count</h3><p>A candidate record is checked at zero tolerance and at 80 and 160 digits, independently of the search, and linked to the exact round, code and seed that found it.</p></div>
    </div>
    <h2>Verified records</h2>
    <table class="data"><tr><th>n</th><th class="num">best known before</th><th class="num">Mosa</th><th class="num">improvement</th><th>found by</th></tr>
    ${S.records.map((r) => `<tr class="click" data-act="record" data-n="${r.n}"><td>★ ${r.n}</td><td class="num">${fmtSide(r.reference_side)}</td><td class="num">${fmtSide(r.side)}</td><td class="num neg">${Number(r.improvement).toExponential(2)}</td><td>${esc(prettyName(summaryOf(r.lab)))}</td></tr>`).join("")}</table>
    <h2>What Mosa does and does not do</h2>
    <div class="does">
      <div class="card"><h3>Does</h3><ul><li>Lets the model make high-level choices: which search, imported from which field, at what scale.</li><li>Runs every strategy at equal budget on many sizes and seeds, and reports near misses, not just pass/fail.</li><li>Keeps a library of strategies that broke records, so later researchers build on them.</li><li>Records every prompt, answer, run and certificate in an append-only notebook you can replay.</li></ul></div>
      <div class="card"><h3>Does not</h3><ul><li>Let the model place pieces or judge pictures (we measured: no better than random).</li><li>Let model-written code touch the relaxation, the polish or the verifier.</li><li>Claim optimality: a record is a verified improvement on the best known value.</li><li>Need training: neural networks are optional, not the method.</li></ul></div>
    </div>
    <div class="toolbar" style="margin-top:22px"><button class="btn primary" data-act="activity" data-k="launch">${icon("launch")} New research lab</button>
    ${S.labs.find((l) => l.name.endsWith("strategy-lab")) ? `<button class="btn" data-act="lab" data-lab="${esc(S.labs.find((l) => l.name.endsWith("strategy-lab")).id)}">${icon("labs")} Open the strategy lab that found three records</button>` : ""}</div>
  </div>`;
};

function roundCard(lab, r, m) {
  const st = roundState(r), v = verified(r), expected = expectedRuns(m.lab);
  const ns = [...new Set(v.map((x) => x.n))].sort((a, b) => a - b);
  const near = nearMiss(r.results), errors = r.results.filter((x) => x.error).length;
  const decision = r.strategy?.decision;
  const results = [...r.results].sort((a, b) => a.n - b.n || a.seed - b.seed);
  const inflight = Object.values(r.progress);
  const gens = m.lab?.budget?.generations || 12;
  const frac = expected ? (r.results.length + inflight.reduce((a, p) => a + p.generation / (gens + 1), 0)) / expected : 0;
  return `<div class="round-card ${v.length ? "hit" : ""}" data-act="round" data-lab="${esc(lab)}" data-chain="${r.chain}" data-round="${r.round}">
    <div class="rc-top"><span class="r">R${r.round}</span>${decision ? `<span class="pill ${esc(decision)}">${esc(decision)}</span>` : ""}${v.length ? `<span class="pill record">★ ${ns.join(", ")}</span>` : ""}<span style="margin-left:auto">${st === "done" ? fmtTime(r.done.time) : ""}</span></div>
    ${st === "thinking" ? `<div class="thinking"><span class="spinner"></span> Researching and writing a strategy…</div>` :
      `<div class="rc-title">${esc(ideaTitle(r.strategy?.source) || "—")}</div><div class="rc-why">${esc(r.strategy?.mapping || r.strategy?.strategy || "")}</div>`}
    ${results.length || st === "running" ? `<div class="strip">${results.map((x) => `<span class="cell ${cellClass(x)}" style="${cellStyle(x)}" data-tip="${attr(cellTip(x))}"></span>`).join("")}${st === "running" ? Array.from({ length: Math.max(0, expected - results.length) }, () => '<span class="cell pending"></span>').join("") : ""}</div>` : ""}
    ${st === "running" ? `<div class="progress"><div style="width:${Math.round(frac * 100)}%"></div></div>` : ""}
    <div class="rc-foot">${st === "failed" ? `<span style="color:var(--error)">model call failed</span>` : ""}
      ${r.results.length ? `<span>${r.results.length}/${expected} runs</span>` : ""}${near != null ? `<span data-tip="best other basin found, after polish">near miss ${fmtGap(near)}</span>` : ""}${errors ? `<span style="color:var(--error)">${errors} errors</span>` : ""}</div>
  </div>`;
}

VIEWS.lab = ({ lab }) => {
  const m = modelOf(lab), s = summaryOf(lab);
  if (!m || !m.lab) return `<div class="doc"><div class="thinking"><span class="spinner"></span> Loading notebook…</div></div>`;
  const L = m.lab, chains = [...m.chains.values()].sort((a, b) => a.index - b.index);
  const recs = [...new Set(m.records.filter((x) => x.record).map((x) => x.n))].sort((a, b) => a - b);
  const duration = m.end && m.start ? fmtDur(m.end - m.start) : "";
  const header = `<div class="crumbs"><a data-act="activity" data-k="labs">Labs</a> / ${esc(s?.folder || "")}</div>
    <h1>${esc(prettyName(s))}</h1>
    <p class="lede">${L.kind === "apply" ? `Applying <b>${esc(ideaTitle(L.source))}</b>` : `${L.chains} researcher${L.chains > 1 ? "s" : ""} × ${L.rounds} rounds`} ·
      ${(L.targets || []).length} size${(L.targets || []).length === 1 ? "" : "s"} (n = ${esc(span(L.targets || []))}) · ${seedsOf(L).length} seed${seedsOf(L).length > 1 ? "s" : ""} per size ·
      ${esc(L.backend || "")} · started ${fmtTime(m.start)}${m.done ? `, finished after ${duration}` : s?.running ? " · running" : ""}</p>
    <div class="toolbar">${recs.length ? `<span class="pill record">★ new best-known: n = ${recs.join(", ")}</span>` : ""}
      ${L.references?.length ? `<span class="pill">references n = ${L.references.join(", ")}</span>` : ""}
      ${L.brief ? `<span class="pill">brief</span>` : ""}
      <span style="flex:1"></span>
      <button class="btn" data-act="replay" data-lab="${esc(lab)}">${icon("replay")} Replay</button></div>`;
  if (L.kind === "apply") {
    const results = chains.flatMap((c) => [...c.rounds.values()]).flatMap((r) => r.results);
    const records = m.records.filter((x) => x.record);
    return `<div class="doc">${header}
      <h2>Verified records</h2>${records.length ? `<table class="data"><tr><th>n</th><th>seed</th><th class="num">side</th><th class="num">improvement</th></tr>${records.map((r) => `<tr class="click" data-act="record" data-n="${r.n}"><td>★ ${r.n}</td><td>${r.seed}</td><td class="num">${fmtSide(r.side)}</td><td class="num neg">${Number(r.improvement).toExponential(2)}</td></tr>`).join("")}</table>` : `<p class="lede">None yet.</p>`}
      ${results.length ? `<h2>Runs</h2>${resultsTable(results)}` : ""}</div>`;
  }
  const brief = L.brief ? `<details class="fold"><summary>${icon("doc", 'width="14"')} Research brief</summary><pre class="code" style="white-space:pre-wrap">${esc(L.brief)}</pre></details>` : "";
  return `<div class="doc wide">${header}${brief}
    <h2>Research threads</h2>
    <div class="threads">${chains.map((c) => `<div><div class="thread-head"><div class="who">${researcher(c.index)}</div><div class="focus">${esc((L.foci || [])[c.index] || "")}</div></div>
      ${[...c.rounds.values()].sort((a, b) => a.round - b.round).map((r) => roundCard(lab, r, m)).join('<div class="connector"></div>')}</div>`).join("")}</div>
    ${matrix(lab, m)}
  </div>`;
};

function matrix(lab, m) {
  const targets = [...(m.lab.targets || [])].sort((a, b) => a - b);
  const rounds = [...m.chains.values()].flatMap((c) => [...c.rounds.values()]).filter((r) => r.results.length).sort((a, b) => a.chain - b.chain || a.round - b.round);
  if (!rounds.length || targets.length < 2) return "";
  const best = (r, n) => {
    const xs = r.results.filter((x) => x.n === n);
    if (!xs.length) return null;
    return xs.find((x) => x.record) || xs.filter((x) => !x.error).sort((a, b) => (a.runner_up_gap ?? 9) - (b.runner_up_gap ?? 9))[0] || xs[0];
  };
  return `<h2>Every strategy on every size</h2>
    <div class="heat" style="grid-template-columns: 150px repeat(${targets.length}, minmax(12px, 1fr))">
      <div></div>${targets.map((n) => `<div class="h-n" style="text-align:center;padding:0">${n}</div>`).join("")}
      ${rounds.map((r) => `<div class="h-n" style="text-align:left;cursor:pointer" data-act="round" data-lab="${esc(lab)}" data-chain="${r.chain}" data-round="${r.round}" data-tip="${attr(r.strategy?.source || "")}">R${r.chain + 1}.${r.round} ${esc(ideaTitle(r.strategy?.source)).slice(0, 15)}</div>` +
        targets.map((n) => { const x = best(r, n); return x ? `<span class="cell ${cellClass(x)}" style="${cellStyle(x)}" data-tip="${attr(cellTip(x))}"></span>` : `<span class="cell pending"></span>`; }).join("")).join("")}
    </div>
    <div class="legend"><span><span class="cell rec"></span> verified new best-known</span><span><span class="cell" style="background:var(--near)"></span> near miss (darker is closer)</span><span><span class="cell held"></span> best known held</span><span><span class="cell err"></span> error</span></div>`;
}

function resultsTable(results) {
  const rows = [...results].sort((a, b) => a.n - b.n || a.seed - b.seed);
  return `<table class="data"><tr><th>n</th><th>seed</th><th class="num">polished</th><th class="num">gap</th><th class="num">near miss</th><th class="num">initial</th><th class="num">dropped</th><th></th></tr>
    ${rows.map((x) => `<tr class="click" data-act="target" data-n="${x.n}"><td>${x.record ? "★ " : ""}${x.n}</td><td>${x.seed}</td><td class="num">${fmtSide(x.polished)}</td><td class="num ${x.gap < -1e-9 ? "neg" : ""}">${fmtGap(x.gap)}</td><td class="num">${fmtGap(x.runner_up_gap)}</td><td class="num">${fmtGap(x.initial_gap)}</td><td class="num">${x.dropped ?? ""}</td><td style="color:var(--error);max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${x.error ? esc(String(x.error).split("\n").filter(Boolean).slice(-1)[0]) : ""}</td></tr>`).join("")}</table>`;
}

VIEWS.round = ({ lab, chain, round }) => {
  const m = modelOf(lab);
  const r = m && m.chains.get(chain)?.rounds.get(round);
  if (!r) return `<div class="doc"><div class="thinking"><span class="spinner"></span> Loading…</div></div>`;
  const st = roundState(r), v = verified(r), expected = expectedRuns(m.lab);
  const targets = [...(m.lab.targets || [])].sort((a, b) => a - b), seeds = seedsOf(m.lab);
  const byKey = Object.fromEntries(r.results.map((x) => [`${x.n}/${x.seed}`, x]));
  const seedValues = [...new Set(r.results.map((x) => x.seed))].sort((a, b) => a - b);
  const rowsSeeds = seedValues.length ? seedValues : seeds.map((_, i) => i);
  const s = r.strategy || {};
  return `<div class="doc">
    <div class="crumbs"><a data-act="lab" data-lab="${esc(lab)}">${esc(prettyName(summaryOf(lab)))}</a> / ${researcher(chain)} / round ${round}</div>
    <h1>${esc(ideaTitle(s.source) || (st === "thinking" ? "The researcher is writing a strategy…" : "—"))}</h1>
    <div class="toolbar" style="margin:4px 0 14px">${s.decision ? `<span class="pill ${esc(s.decision)}">${esc(s.decision)}</span>` : ""}${s.builds_on && s.builds_on !== "none" ? `<span class="pill">builds on: ${esc(s.builds_on)}</span>` : ""}
      ${v.length ? `<span class="pill record">★ new best-known: n = ${[...new Set(v.map((x) => x.n))].join(", ")}</span>` : ""}
      <span class="pill">${r.results.length}/${expected} runs</span>${s.model_seconds ? `<span class="pill">model ${Math.round(s.model_seconds)} s</span>` : ""}</div>
    ${s.source ? `<p class="lede">${esc(s.source)}</p>` : ""}
    ${s.mapping ? `<h2>Why it should fit this landscape</h2><div class="quote">${esc(s.mapping)}</div>` : ""}
    ${s.strategy ? `<h2>Strategy</h2><div class="prose">${esc(s.strategy)}</div>` : ""}
    ${targets.length ? `<h2>Results</h2>
      <div class="heat" style="grid-template-columns: 54px repeat(${targets.length}, minmax(12px, 1fr))">
        <div></div>${targets.map((n) => `<div class="h-n" style="text-align:center;padding:0">${n}</div>`).join("")}
        ${rowsSeeds.map((seed) => `<div class="h-n">${rowsSeeds.length > 1 ? `seed ${seed % 100000 === seed ? seed : Math.floor(seed / 100000)}` : ""}</div>` + targets.map((n) => {
          const x = byKey[`${n}/${seed}`];
          const p = r.progress[`${n}/${seed}`];
          return x ? `<span class="cell ${cellClass(x)}" style="${cellStyle(x)}" data-tip="${attr(cellTip(x))}" data-act="target" data-n="${n}"></span>` :
            `<span class="cell pending" ${p ? `data-tip="${attr(`n=${n} generation ${p.generation}\nbest ${fmtSide(p.best)}`)}"` : ""}></span>`;
        }).join("")).join("")}
      </div>
      <div class="legend"><span><span class="cell rec"></span> verified new best-known</span><span><span class="cell" style="background:var(--near)"></span> near miss (darker is closer)</span><span><span class="cell held"></span> best known held</span><span><span class="cell err"></span> error</span><span><span class="cell pending"></span> running</span></div>` : ""}
    ${v.length ? `<h2>Verified records</h2><table class="data"><tr><th>n</th><th>seed</th><th class="num">side</th><th class="num">improvement</th></tr>${v.map((x) => `<tr class="click" data-act="record" data-n="${x.n}"><td>★ ${x.n}</td><td>${x.seed}</td><td class="num">${fmtSide(x.side)}</td><td class="num neg">${Number(x.improvement).toExponential(2)}</td></tr>`).join("")}</table>` : ""}
    ${r.results.length ? `<details class="fold"><summary>${icon("doc", 'width="14"')} All runs (${r.results.length})</summary><div style="padding:6px 8px">${resultsTable(r.results)}</div></details>` : ""}
    ${s.code ? `<h2>Code</h2><pre class="code"><code class="language-python">${esc(s.code)}</code></pre>` : ""}
    ${r.prompt ? `<details class="fold"><summary>${icon("doc", 'width="14"')} What the researcher saw (prompt, ${Math.round(r.prompt.prompt.length / 1000)} k characters)</summary><pre class="code" style="white-space:pre-wrap">${esc(r.prompt.prompt)}</pre></details>` : ""}
    ${r.error ? `<h2>Error</h2><pre class="code" style="color:var(--error)">${esc(r.error.error)}</pre>` : ""}
  </div>`;
};

VIEWS.record = ({ n }) => {
  const rec = S.records.find((r) => r.n === n);
  if (!rec) return `<div class="doc"><p class="lede">No verified record for n = ${n}.</p></div>`;
  const ref = S.refs[n];
  if (!ref) ensureRef(n);
  const hasRef = ref && ref !== "loading";
  const diff = hasRef ? changed(rec.poses, rec.side, ref.poses, ref.side) : null;
  const lab = summaryOf(rec.lab), m = modelOf(rec.lab);
  const r = m && m.chains.get(rec.chain ?? 0)?.rounds.get(rec.round ?? 1);
  const hp = rec.high_precision || [];
  const comment = `    ${n} unit squares in a square of side ${rec.side}.\n    Found by Mosa (LLM-designed search strategy), verified at zero tolerance and at 80 and 160 digits.`;
  return `<div class="doc">
    <div class="crumbs"><a data-act="activity" data-k="records">Records</a> / n = ${n}</div>
    <h1>${n} squares in a square</h1>
    <div style="display:flex;gap:28px;align-items:flex-end;margin:10px 0 20px;flex-wrap:wrap">
      <div><div class="k" style="color:var(--muted);font-size:12px">best known before</div><div class="bignum" style="color:var(--muted)">${fmtSide(rec.reference_side)}</div></div>
      <div><div class="k" style="color:var(--muted);font-size:12px">Mosa</div><div class="bignum">${fmtSide(rec.side)}</div></div>
      <div><div class="k" style="color:var(--muted);font-size:12px">improvement</div><div class="bignum delta">${Number(rec.improvement).toExponential(3)}</div></div>
    </div>
    <div class="grid2">
      <div><div class="figure">${hasRef ? packingSVG(ref.poses, ref.side) : '<div class="thinking"><span class="spinner"></span></div>'}</div><div class="figcap"><span>best known before</span><b>${hasRef ? fmtSide(ref.side) : ""}</b></div></div>
      <div><div class="figure">${packingSVG(rec.poses, rec.side, diff?.flags)}</div><div class="figcap"><span>Mosa${diff ? ` · ${diff.count} squares rearranged` : ""}</span><b>${fmtSide(rec.side)}</b></div></div>
    </div>
    <div class="grid2" style="margin-top:22px">
      <div class="card"><h3>Verification</h3><div class="checks" style="margin-top:8px">
        <div class="check">${icon("check")} No overlap at zero tolerance (float separating-axis test)</div>
        ${hp.map((a) => `<div class="check">${a.valid ? icon("check") : icon("x")} ${a.digits}-digit audit: smallest pair gap ${esc(a.min_pair_gap)}</div>`).join("")}
        <div class="check">${icon("check")} Every pair and wall at least ${Number(rec.min_pair_clearance).toExponential(1)} apart</div></div>
        <p style="color:var(--faint);font-size:11.5px;margin:10px 0 0">High-precision numerical checks, independent of the search; not interval arithmetic or a proof of optimality.</p></div>
      <div class="card"><h3>Provenance</h3><dl class="kv" style="margin-top:8px">
        <dt>lab</dt><dd><a data-act="lab" data-lab="${esc(rec.lab)}">${esc(prettyName(lab))}</a></dd>
        ${lab?.kind === "lab" ? `<dt>found by</dt><dd><a data-act="round" data-lab="${esc(rec.lab)}" data-chain="${rec.chain}" data-round="${rec.round}">${researcher(rec.chain)}, round ${rec.round}</a></dd>` : ""}
        <dt>seed</dt><dd class="mono">${rec.seed}</dd>
        ${r?.strategy?.source ? `<dt>idea</dt><dd>${esc(ideaTitle(r.strategy.source))}</dd>` : lab?.source ? `<dt>strategy</dt><dd>${esc(lab.source)}</dd>` : ""}
        <dt>verified</dt><dd>${fmtTime(rec.time)}</dd></dl></div>
    </div>
    <div class="toolbar" style="margin-top:18px">
      <button class="btn" data-act="dl-svg" data-n="${n}">${icon("download")} square-${n}.svg (catalogue format)</button>
      <button class="btn" data-act="dl-json" data-n="${n}">${icon("download")} n${n}.json</button>
      <button class="btn" data-act="target" data-n="${n}">${icon("targets")} All attempts on n = ${n}</button></div>
  </div>`;
};

VIEWS.target = ({ n }) => {
  const ref = S.refs[n];
  if (!ref) ensureRef(n);
  const hasRef = ref && ref !== "loading";
  const info = hasRef ? ref.info : (S.targets.find((t) => t.n === n) || {});
  const attempts = [];
  for (const [id, book] of Object.entries(S.books)) {
    if (!book.model) continue;
    for (const c of book.model.chains.values()) for (const r of c.rounds.values()) for (const x of r.results) if (x.n === n) attempts.push({ id, r, x });
  }
  attempts.sort((a, b) => (a.x.gap ?? 9) - (b.x.gap ?? 9) || (a.x.runner_up_gap ?? 9) - (b.x.runner_up_gap ?? 9));
  const rec = S.records.find((r) => r.n === n);
  return `<div class="doc">
    <div class="crumbs"><a data-act="activity" data-k="targets">Problem sizes</a> / n = ${n}</div>
    <h1>n = ${n}</h1>
    <div class="toolbar" style="margin:4px 0 16px">${rec ? `<span class="pill record" data-act="record" data-n="${n}" style="cursor:pointer">★ Mosa ${fmtSide(rec.side)}</span>` : ""}${info.closed_form ? `<span class="pill">closed form</span>` : ""}</div>
    <div class="grid2">
      <div><div class="figure">${hasRef ? packingSVG(ref.poses, ref.side) : '<div class="thinking"><span class="spinner"></span></div>'}</div><div class="figcap"><span>best known packing (witness)</span><b>${hasRef ? fmtSide(ref.side) : ""}</b></div></div>
      <div><dl class="kv"><dt>best known</dt><dd class="mono">${fmtSide(info.best_known)}</dd><dt>official catalogue</dt><dd class="mono">${fmtSide(info.official)}</dd><dt>trivial grid</dt><dd class="mono">${info.grid ?? ""}</dd>
        ${info.closed_form ? `<dt>closed form</dt><dd class="mono">${esc(info.closed_form.replace(/\\over/g, "/").replace(/[{}]/g, ""))}</dd>` : ""}</dl>
        ${info.notes ? `<h2>Catalogue history</h2><p class="lede" style="font-size:12.5px">${esc(info.notes)}</p>` : ""}</div>
    </div>
    <h2>Attempts in these notebooks (${attempts.length})</h2>
    ${attempts.length ? `<table class="data"><tr><th>lab</th><th>strategy</th><th>seed</th><th class="num">gap</th><th class="num">near miss</th></tr>${attempts.slice(0, 200).map(({ id, r, x }) => `<tr class="click" data-act="round" data-lab="${esc(id)}" data-chain="${r.chain}" data-round="${r.round}"><td>${esc(prettyName(summaryOf(id)))}</td><td>${esc(ideaTitle(r.strategy?.source)).slice(0, 60)}</td><td>${x.seed}</td><td class="num ${x.gap < -1e-9 ? "neg" : ""}">${x.error ? "error" : fmtGap(x.gap)}</td><td class="num">${fmtGap(x.runner_up_gap)}</td></tr>`).join("")}</table>` : `<p class="lede">No runs on this size in the loaded notebooks.</p>`}
  </div>`;
};

VIEWS.library = () => `<div class="doc"><div class="crumbs">Strategy library</div><h1>Strategies that broke records</h1>
  <p class="lede">Later researchers see these (idea, strategy and code) and are asked to build on them, combine them or find what they miss.</p>
  ${S.library.map((e, i) => `<div class="card" style="margin-top:14px" id="lib-${i}"><h3>${esc(ideaTitle(e.source))}</h3>
    <div class="toolbar" style="margin:6px 0 10px">${Object.entries(e.records_broken || {}).map(([n, side]) => `<span class="pill record" data-act="target" data-n="${n}" style="cursor:pointer">★ n = ${n} · ${Number(side).toFixed(6)}</span>`).join("")}</div>
    <p class="lede" style="font-size:12.5px">${esc(e.source)}</p><div class="prose" style="font-size:12.5px">${esc(e.strategy)}</div>
    <p style="color:var(--faint);font-size:11.5px;margin-top:8px">origin: ${esc(e.origin)}</p>
    <details class="fold"><summary>${icon("doc", 'width="14"')} Code</summary><pre class="code"><code class="language-python">${esc(e.code)}</code></pre></details></div>`).join("")}</div>`;

VIEWS.launch = () => {
  const apply = S.launchKind === "apply";
  return `<div class="doc"><div class="crumbs">New lab</div><h1>${apply ? "Apply a strategy" : "Start a research lab"}</h1>
  <p class="lede">${apply ? "Run one library strategy, without a model, on more sizes and seeds." : "Researchers write strategies for these sizes; every strategy runs on every size and seed at the same budget. Candidate records are verified independently."}</p>
  <div class="form">
    <label>Kind</label><div class="seg"><button class="${apply ? "" : "on"}" data-act="launch-kind" data-k="lab">Research lab</button><button class="${apply ? "on" : ""}" data-act="launch-kind" data-k="apply">Apply strategy</button></div>
    <label>Sizes</label><div><input id="f-targets" value="${apply ? "88, 123, 129, 130" : "101-110, 122-132"}"><div class="hint">Ranges and lists, e.g. 67 or 101-110, 122-132. Known record-breaking pattern: records built by extending other packings.</div></div>
    ${apply ? `<label>Strategy</label><select id="f-strategy">${S.library.map((e, i) => `<option value="library:${i}">${esc(ideaTitle(e.source))}</option>`).join("")}</select>` :
      `<label>Researchers</label><input id="f-chains" type="number" min="1" max="8" value="4"><label>Rounds</label><input id="f-rounds" type="number" min="1" max="10" value="3">`}
    <label>Seeds</label><div><input id="f-seeds" value="${apply ? "1 2 3 4" : "0"}"><div class="hint">One run is a noisy sample: more seeds per size give a fairer verdict per idea.</div></div>
    <label>Backend</label><div class="seg"><button class="${S.launchBackend === "modal" ? "on" : ""}" data-act="launch-backend" data-k="modal">Modal</button><button class="${S.launchBackend === "local" ? "on" : ""}" data-act="launch-backend" data-k="local">This machine</button></div>
    <label>Reference sizes</label><div><input id="f-refs" placeholder="e.g. 17"><div class="hint">Extra best packings the strategy code receives (for analogies across sizes).</div></div>
    ${apply ? "" : `<label>Brief</label><div><select id="f-brief-pick" data-act-change="brief-pick"><option value="">No brief</option>${S.briefs.map((b) => `<option>${esc(b.name)}</option>`).join("")}</select><textarea id="f-brief" style="margin-top:8px" placeholder="Target-specific evidence for the researchers (optional)"></textarea></div>`}
    <span></span><div><button class="btn primary" data-act="launch-go">${icon("launch")} ${apply ? "Run" : "Start lab"}</button> <span id="f-status" style="color:var(--muted);margin-left:10px"></span></div>
  </div></div>`;
};

function renderContent() {
  const t = activeTab();
  const el = $("#content");
  const top = el.scrollTop;
  const openFolds = [...el.querySelectorAll("details[open]")].map((d) => d.querySelector("summary")?.textContent);
  el.innerHTML = t ? (VIEWS[t.type] || (() => ""))(t.args) : VIEWS.welcome();
  el.querySelectorAll("details").forEach((d) => { if (openFolds.includes(d.querySelector("summary")?.textContent)) d.open = true; });
  if (window.hljs) el.querySelectorAll("pre code.language-python").forEach((c) => window.hljs.highlightElement(c));
  el.scrollTop = top;
}

// ---------- panel and status ----------
function renderPanel() {
  const tabs = [["progress", "Progress"], ["notebook", "Notebook"], ["problems", "Problems"]];
  $("#panel-tabs").innerHTML = tabs.map(([k, l]) => `<button class="${S.panel === k ? "on" : ""}" data-act="panel" data-k="${k}">${l}</button>`).join("") +
    `<span class="grow"></span><span style="color:var(--faint);font-size:11.5px">${esc(prettyName(summaryOf(S.currentLab)) || "")}</span>`;
  const m = S.currentLab && modelOf(S.currentLab);
  const body = $("#panel-body");
  if (!m) { body.innerHTML = `<div style="color:var(--faint);padding-top:6px">Open a lab to follow its runs.</div>`; return; }
  const book = S.books[S.currentLab];
  if (S.panel === "progress") {
    const inflight = [...m.chains.values()].flatMap((c) => [...c.rounds.values()]).flatMap((r) => Object.values(r.progress).map((p) => ({ r, p })));
    const gens = m.lab?.budget?.generations || 12;
    const thinking = [...m.chains.values()].flatMap((c) => [...c.rounds.values()]).filter((r) => roundState(r) === "thinking");
    body.innerHTML = (thinking.map((r) => `<div class="prog-row"><span>${researcher(r.chain)} · round ${r.round}</span><span style="color:var(--muted)">model</span><span class="thinking"><span class="spinner"></span> writing a strategy</span><span></span></div>`).join("") +
      inflight.sort((a, b) => a.p.n - b.p.n).map(({ r, p }) => `<div class="prog-row"><span>${researcher(r.chain)} · round ${r.round}</span><span>n = ${p.n} · seed ${p.seed}</span><div class="bar"><div style="width:${Math.round((p.generation / gens) * 100)}%"></div></div><span style="color:var(--muted)">gen ${p.generation}/${gens} · ${fmtGap(p.best - (S.targets.find((t) => t.n === p.n)?.best_known ?? p.best))}</span></div>`).join("")) ||
      `<div style="color:var(--faint);padding-top:6px">${m.done ? `Finished: ${m.results} runs, ${m.records.filter((x) => x.record).length} verified records.` : "Nothing in flight."}</div>`;
  } else if (S.panel === "notebook") {
    const events = (S.replay && S.replay.lab === S.currentLab ? book.events.filter((e) => e.time <= S.replay.t) : book.events).filter((e) => e.type !== "progress").slice(-400);
    const line = (e) => {
      const tag = e.chain !== undefined ? `${researcher(e.chain)} r${e.round}` : "";
      const msg = { lab: () => `lab started: ${(e.targets || []).length} sizes`, prompt: () => `${tag}: prompt (${Math.round(e.prompt.length / 1000)} k chars)`,
        strategy: () => `${tag}: ${ideaTitle(e.source)}`, result: () => `${tag}: n=${e.n} seed ${e.seed} ${e.error ? "error" : `gap ${fmtGap(e.gap)} near ${fmtGap(e.runner_up_gap)}`}`,
        record: () => `${tag}: ★ verified n=${e.n} side ${fmtSide(e.side)} (${Number(e.improvement).toExponential(2)})`, round: () => `${tag}: round done, ${e.records} records`,
        error: () => `${tag}: ${e.error}`, library: () => `library: + ${ideaTitle(e.source)}`, done: () => "lab finished" }[e.type];
      return `<div class="log-line ${e.type === "record" ? "rec" : e.type === "error" || e.error ? "err" : ""}"><span class="t">${fmtTime(e.time)}</span><span class="k">${e.type}</span><span class="m">${esc(msg ? msg() : "")}</span></div>`;
    };
    body.innerHTML = events.map(line).join("");
    body.scrollTop = body.scrollHeight;
  } else {
    const errs = [...m.errors, ...[...m.chains.values()].flatMap((c) => [...c.rounds.values()]).flatMap((r) => r.results.filter((x) => x.error))];
    body.innerHTML = errs.length ? errs.map((e) => `<div class="log-line err"><span class="k">${e.chain !== undefined ? `R${e.chain + 1}.${e.round}` : ""}</span><span class="m">${esc(e.n ? `n=${e.n} seed ${e.seed}: ` : "")}${esc(String(e.error).split("\n").filter(Boolean).slice(-1)[0])}</span></div>`).join("") : `<div style="color:var(--faint);padding-top:6px">No problems.</div>`;
  }
}

function renderStatus() {
  const s = summaryOf(S.currentLab), m = S.currentLab && modelOf(S.currentLab);
  const running = S.labs.filter((l) => l.running).length;
  let left = `<span class="item">${BRAND.replace('width="22" height="22"', 'width="13" height="13"')} Mosa</span>`;
  if (S.replay) {
    const r = S.replay;
    left += `<span class="item replay">${icon("replay")} Replay</span><button data-act="replay-play">${icon(r.playing ? "pause" : "play")}</button>
      <input type="range" id="replay-range" min="${r.start}" max="${r.end}" step="1" value="${r.t}"><span class="item mono">${fmtTime(r.t)}</span><button data-act="replay-stop">${icon("x")} exit</button>`;
  } else if (s) {
    left += `<span class="item"><span class="dot ${s.running ? "live" : ""}"></span>${s.running ? "Running" : s.done ? "Finished" : "Stopped"} · ${esc(prettyName(s))}</span>${s.backend ? `<span class="item">${esc(s.backend)}</span>` : ""}`;
    if (m) left += `<span class="item">${m.results} runs</span>`;
  }
  $("#status").innerHTML = `${left}<span class="grow"></span>${running ? `<span class="item"><span class="dot live"></span>${running} running</span>` : ""}
    <button data-act="activity" data-k="records" class="item"><span class="star">★</span> ${S.records.length} verified</button>
    <button data-act="toggle-panel" class="item">${icon("panel")}</button><button data-act="palette" class="item">⌘K</button>`;
}

function render() {
  renderActivity();
  renderSidebar();
  renderTabs();
  renderContent();
  renderPanel();
  renderStatus();
}

// ---------- palette ----------
function paletteItems() {
  const items = [
    { k: "action", label: "New research lab", run: () => { S.activity = "launch"; openTab("launch"); } },
    { k: "action", label: "Toggle theme", run: toggleTheme },
    { k: "action", label: "Toggle bottom panel", run: () => $("#editor").classList.toggle("no-panel") },
    { k: "action", label: "Toggle sidebar", run: () => $("#app").classList.toggle("no-sidebar") },
    { k: "view", label: "Welcome", run: () => openTab("welcome") },
    { k: "view", label: "Strategy library", run: () => openTab("library") },
  ];
  for (const l of S.labs) items.push({ k: "lab", label: prettyName(l), run: () => openTab("lab", { lab: l.id }) });
  for (const [id, b] of Object.entries(S.books)) if (b.model) for (const c of b.model.chains.values()) for (const r of c.rounds.values()) if (r.strategy?.source)
    items.push({ k: "round", label: `${ideaTitle(r.strategy.source)} — ${researcher(r.chain)} r${r.round}`, run: () => openTab("round", { lab: id, chain: r.chain, round: r.round }) });
  for (const r of S.records) items.push({ k: "record", label: `n = ${r.n}  ${fmtSide(r.side)}`, run: () => openTab("record", { n: r.n }) });
  for (const t of S.targets) items.push({ k: "size", label: `n = ${t.n}`, run: () => openTab("target", { n: t.n }) });
  return items;
}
function openPalette() {
  $("#palette").hidden = false;
  $("#palette-input").value = "";
  S.palette.all = paletteItems();
  filterPalette();
  $("#palette-input").focus();
}
function filterPalette() {
  const q = $("#palette-input").value.toLowerCase().trim();
  const match = (s) => { let i = 0; for (const c of s.toLowerCase()) if (c === q[i]) i++; return i === q.length; };
  S.palette.items = S.palette.all.filter((x) => !q || x.label.toLowerCase().includes(q) || match(x.label)).slice(0, 60);
  S.palette.index = 0;
  drawPalette();
}
function drawPalette() {
  $("#palette-list").innerHTML = S.palette.items.map((x, i) => `<li class="${i === S.palette.index ? "on" : ""}" data-act="palette-pick" data-i="${i}"><span class="k">${x.k}</span><span>${esc(x.label)}</span></li>`).join("");
  $("#palette-list li.on")?.scrollIntoView({ block: "nearest" });
}
const closePalette = () => { $("#palette").hidden = true; };

// ---------- actions ----------
function toggleTheme() {
  const now = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  document.documentElement.dataset.theme = now === "light" ? "dark" : "light";
  try { localStorage.setItem("mosa-theme", document.documentElement.dataset.theme); } catch (e) { /* storage unavailable */ }
  render();
}

function parseList(text) {
  const out = [];
  for (const part of String(text).split(/[\s,]+/).filter(Boolean)) {
    const m = part.match(/^(\d+)[-–](\d+)$/);
    if (m) for (let n = +m[1]; n <= +m[2]; n++) out.push(n);
    else if (/^\d+$/.test(part)) out.push(+part);
  }
  return out;
}

async function launch() {
  const status = $("#f-status");
  const apply = S.launchKind === "apply";
  const spec = { kind: apply ? "apply" : "lab", targets: parseList($("#f-targets").value), seeds: parseList($("#f-seeds").value),
    backend: S.launchBackend, references: parseList($("#f-refs").value) };
  if (apply) spec.strategy = $("#f-strategy").value;
  else Object.assign(spec, { chains: +$("#f-chains").value, rounds: +$("#f-rounds").value, brief: $("#f-brief").value });
  if (!spec.targets.length) { status.textContent = "Give at least one size."; return; }
  status.textContent = "Starting…";
  try {
    const r = await api("/api/launch", spec);
    status.textContent = "Started.";
    await refresh();
    S.activity = "labs";
    openTab("lab", { lab: r.id });
  } catch (e) { status.textContent = e.message; }
}

let replayTimer = null;
function startReplay(lab) {
  const m = S.books[lab]?.model;
  if (!m) return;
  S.replay = { lab, start: Math.floor(m.start), end: Math.ceil(m.end), t: Math.floor(m.start), playing: true };
  S.currentLab = lab;
  tickReplay();
  render();
}
function tickReplay() {
  clearInterval(replayTimer);
  if (!S.replay?.playing) return;
  const r = S.replay;
  const step = Math.max(1, (r.end - r.start) / 450);  // the whole lab in about 45 seconds
  replayTimer = setInterval(() => {
    r.t = Math.min(r.end, r.t + step);
    if (r.t >= r.end) { r.playing = false; clearInterval(replayTimer); }
    renderSidebar(); renderContent(); renderPanel(); renderStatus();
  }, 100);
}

document.addEventListener("click", (ev) => {
  const el = ev.target.closest("[data-act]");
  if (!el) return;
  const d = el.dataset;
  switch (d.act) {
    case "activity":
      S.activity = d.k;
      if (d.k === "launch") openTab("launch");
      else if (d.k === "library") openTab("library");
      else render();
      break;
    case "toggle": ev.stopPropagation(); S.open[d.node] = !S.open[d.node]; if (!S.books[d.node]) loadBook(d.node).then(render); render(); break;
    case "lab": S.open[d.lab] = true; openTab("lab", { lab: d.lab }); break;
    case "round": openTab("round", { lab: d.lab, chain: +d.chain, round: +d.round }); break;
    case "record": openTab("record", { n: +d.n }); break;
    case "target": openTab("target", { n: +d.n }); loadAllBooks(); break;
    case "library": openTab("library"); setTimeout(() => document.getElementById(`lib-${d.i}`)?.scrollIntoView({ behavior: "smooth" }), 50); break;
    case "brief": { S.activity = "launch"; openTab("launch"); const b = S.briefs.find((x) => x.name === d.name); setTimeout(() => { if ($("#f-brief")) $("#f-brief").value = b.text; }, 0); break; }
    case "tab": S.active = d.key; const t = activeTab(); if (t?.args.lab) S.currentLab = t.args.lab; render(); break;
    case "close": ev.stopPropagation(); closeTab(d.key); break;
    case "theme": toggleTheme(); break;
    case "palette": openPalette(); break;
    case "palette-pick": closePalette(); S.palette.items[+d.i].run(); break;
    case "panel": S.panel = d.k; renderPanel(); break;
    case "toggle-panel": $("#editor").classList.toggle("no-panel"); break;
    case "replay": startReplay(d.lab); break;
    case "replay-play": if (S.replay) { if (S.replay.t >= S.replay.end) S.replay.t = S.replay.start; S.replay.playing = !S.replay.playing; tickReplay(); renderStatus(); } break;
    case "replay-stop": clearInterval(replayTimer); S.replay = null; render(); break;
    case "launch-kind": S.launchKind = d.k; renderContent(); break;
    case "launch-backend": S.launchBackend = d.k; renderContent(); break;
    case "launch-go": launch(); break;
    case "dl-svg": { const r = S.records.find((x) => x.n === +d.n); download(`square-${r.n}.svg`, catalogueSVG(r.poses, r.side, `    ${r.n} unit squares in a square of side ${r.side}.\n    Found by Mosa; verified at zero tolerance and at 80 and 160 digits.`), "image/svg+xml"); break; }
    case "dl-json": { const r = S.records.find((x) => x.n === +d.n); download(`n${r.n}.json`, JSON.stringify({ n: r.n, side: r.side, previous_best_known: r.reference_side, squares: r.poses.map(([x, y, a]) => ({ x, y, angle_radians: a })) }, null, 1), "application/json"); break; }
  }
});
document.addEventListener("change", (ev) => {
  if (ev.target.id === "f-brief-pick") { const b = S.briefs.find((x) => x.name === ev.target.value); $("#f-brief").value = b ? b.text : ""; }
});
document.addEventListener("input", (ev) => {
  if (ev.target.id === "replay-range" && S.replay) { S.replay.t = +ev.target.value; S.replay.playing = false; clearInterval(replayTimer); renderSidebar(); renderContent(); renderPanel(); $("#status .mono").textContent = fmtTime(S.replay.t); }
  if (ev.target.id === "palette-input") filterPalette();
});
document.addEventListener("keydown", (ev) => {
  const mod = ev.metaKey || ev.ctrlKey;
  if (mod && ev.key.toLowerCase() === "k") { ev.preventDefault(); $("#palette").hidden ? openPalette() : closePalette(); return; }
  if (mod && ev.key.toLowerCase() === "b") { ev.preventDefault(); $("#app").classList.toggle("no-sidebar"); return; }
  if (mod && ev.key.toLowerCase() === "j") { ev.preventDefault(); $("#editor").classList.toggle("no-panel"); return; }
  if (!$("#palette").hidden) {
    if (ev.key === "Escape") closePalette();
    else if (ev.key === "ArrowDown") { S.palette.index = Math.min(S.palette.items.length - 1, S.palette.index + 1); drawPalette(); ev.preventDefault(); }
    else if (ev.key === "ArrowUp") { S.palette.index = Math.max(0, S.palette.index - 1); drawPalette(); ev.preventDefault(); }
    else if (ev.key === "Enter") { const x = S.palette.items[S.palette.index]; closePalette(); x?.run(); }
  }
});
$("#palette").addEventListener("click", (ev) => { if (ev.target.id === "palette") closePalette(); });

// tooltips
document.addEventListener("mouseover", (ev) => {
  const el = ev.target.closest("[data-tip]");
  const tip = $("#tooltip");
  if (!el) { tip.hidden = true; return; }
  let text = el.dataset.tip;
  try { text = JSON.parse(text); } catch (e) { /* plain text */ }
  if (!text) { tip.hidden = true; return; }
  tip.textContent = text;
  tip.style.whiteSpace = "pre-wrap";
  tip.hidden = false;
});
document.addEventListener("mousemove", (ev) => {
  const tip = $("#tooltip");
  if (tip.hidden) return;
  const x = Math.min(ev.clientX + 14, innerWidth - tip.offsetWidth - 8), y = Math.min(ev.clientY + 16, innerHeight - tip.offsetHeight - 8);
  tip.style.left = `${x}px`;
  tip.style.top = `${y}px`;
});

// ---------- polling ----------
async function loadAllBooks() {
  const loads = S.labs.filter((l) => !S.books[l.id]).map((l) => loadBook(l.id));
  if (loads.length) { await Promise.all(loads); render(); }
}
async function refresh() {
  const [labs, records] = await Promise.all([api("/api/labs"), api("/api/records")]);
  const changedLabs = JSON.stringify(labs.map((l) => [l.id, l.events])) !== JSON.stringify(S.labs.map((l) => [l.id, l.events]));
  const changedRecords = records.length !== S.records.length || records.some((r, i) => r.side !== S.records[i]?.side);
  S.labs = labs;
  S.records = records;
  let dirty = changedLabs || changedRecords;
  for (const l of labs) if (S.books[l.id] && S.books[l.id].next < l.events) dirty = (await loadBook(l.id)) || dirty;
  return dirty;
}

async function main() {
  try { const t = localStorage.getItem("mosa-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) { /* storage unavailable */ }
  await refresh();
  [S.targets, S.library, S.briefs] = await Promise.all([api("/api/targets"), api("/api/library"), api("/api/briefs")]);
  const live = S.labs.find((l) => l.running);
  openTab("welcome");
  await loadAllBooks();
  if (live) { S.open[live.id] = true; openTab("lab", { lab: live.id }); }
  render();
  setInterval(async () => { if (S.replay) return; try { if (await refresh()) render(); } catch (e) { /* server restarting */ } }, 2500);
}
main();
