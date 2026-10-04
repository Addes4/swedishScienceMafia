"use strict";
// Mosa. Three things are visible: labs (a research question), ideas (one per researcher round, with an outcome) and
// discoveries (verified records). Everything is derived from the labs' notebooks, so a live lab and a replay of a
// finished one are drawn by the same code.

const $ = (s, el = document) => el.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const svg = (body, size = 16) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
const ICON = {
  star: `<svg viewBox="0 0 24 24" width="15" height="15"><path fill="var(--star)" d="M12 2.8l2.8 5.8 6.3.9-4.6 4.5 1.1 6.3L12 17.3l-5.6 3 1.1-6.3-4.6-4.5 6.3-.9z"/></svg>`,
  fail: svg('<circle cx="12" cy="12" r="8" stroke="var(--error)"/><path d="M9.5 9.5l5 5M14.5 9.5l-5 5" stroke="var(--error)"/>', 15),
  check: svg('<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16.5 9.5"/>', 15),
  plus: svg('<path d="M12 5v14M5 12h14"/>', 14),
  close: svg('<path d="M7 7l10 10M17 7L7 17"/>'),
  play: svg('<path d="M8 5.5l10 6.5-10 6.5z"/>', 14),
  pause: svg('<path d="M9 5.5v13M15 5.5v13"/>', 14),
  replay: svg('<path d="M4 12a8 8 0 1 0 2.4-5.7"/><path d="M4 4v4.5h4.5"/>', 14),
  sun: svg('<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M5 5l1.4 1.4M17.6 17.6L19 19M3 12h2M19 12h2M5 19l1.4-1.4M17.6 6.4L19 5"/>'),
  moon: svg('<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>'),
  download: svg('<path d="M12 4v11M7 10.5l5 5 5-5M5 20h14"/>', 14),
  send: svg('<path d="M12 19V5M6 11l6-6 6 6"/>', 16),
};
const LOGO = `<svg viewBox="0 0 24 24" width="18" height="18"><rect x="3" y="3" width="8" height="8" rx="1" fill="var(--accent)"/><rect x="13" y="3" width="8" height="8" rx="1" fill="var(--faint)"/><rect x="3" y="13" width="8" height="8" rx="1" fill="var(--faint)"/><rect x="13.2" y="13.2" width="7.6" height="7.6" rx="1" fill="var(--strong)" transform="rotate(22 17 17)"/></svg>`;

const S = { labs: [], discoveries: [], books: {}, refs: {}, lab: null, sel: null, compose: null, replay: null, view: "after" };

// ---------- data ----------
const api = async (path, body) => {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || r.statusText);
  return data;
};

async function loadBook(id) {
  const book = S.books[id] || (S.books[id] = { events: [], next: 0, model: null });
  const data = await api(`/api/events?lab=${encodeURIComponent(id)}&since=${book.next}`);
  if (!data.events.length && book.model) return false;
  book.events.push(...data.events);
  book.next = data.next;
  book.model = buildModel(book.events);
  return true;
}

async function reference(n, domain = "squares") {
  if (!S.refs[n]) { S.refs[n] = "loading"; S.refs[n] = await api(`/api/reference?n=${n}&domain=${domain}`); render(); }
  return S.refs[n];
}

const ideaKey = (e) => (e.idea ? e.idea.join(":") : `${e.session ?? 0}:${e.chain ?? 0}:${e.round ?? 1}`);

function buildModel(events, until = Infinity) {
  const m = { lab: null, sessions: [], ideas: new Map(), start: null, end: null, done: false, plans: [], requests: [] };
  const idea = (e) => {
    const key = ideaKey(e);
    if (!m.ideas.has(key)) {
      const [session, chain, round] = key.split(":").map(Number);
      m.ideas.set(key, { key, session, chain, round, results: [], records: [], progress: {}, prompt: null, strategy: null, done: false,
        error: null, sessions: new Set(), expected: 0 });
    }
    return m.ideas.get(key);
  };
  const runs = (s) => (s.targets || []).length * (s.seeds && s.seeds.length ? s.seeds.length : 1);
  for (const e of events) {
    if (e.time > until) continue;
    m.start = m.start === null ? e.time : Math.min(m.start, e.time);
    m.end = m.end === null ? e.time : Math.max(m.end, e.time);
    const s = e.session ?? 0;
    if (e.type === "plan") { m.plans.push(e); m.waiting = false; }
    else if (e.type === "request") { m.requests.push(e); m.waiting = "Reading your request"; }
    else if (e.type === "reply") m.waiting = e.drafting ? "Writing a harness for this problem and testing it" : false;
    else if (e.type === "harness") m.waiting = e.report?.passed ? "Planning the session" : "Writing the harness again";
    else if (e.type === "lab") {
      m.sessions[s] = { ...e, index: s, done: false };
      if (!m.lab) m.lab = e;
      if (e.idea) { const r = idea({ idea: e.idea }); r.sessions.add(s); r.expected += runs(e); }
    } else if (e.type === "prompt") idea(e).prompt = e;
    else if (e.type === "strategy") { const r = idea(e); r.strategy = e; r.sessions.add(s); r.expected += runs(m.sessions[s] || {}); }
    else if (e.type === "progress") idea(e).progress[`${e.n}/${e.seed}/${s}`] = e;
    else if (e.type === "result") { const r = idea(e); r.results.push(e); delete r.progress[`${e.n}/${e.seed}/${s}`]; }
    else if (e.type === "record" && e.record) idea(e).records.push(e);
    else if (e.type === "round") idea(e).done = true;
    else if (e.type === "error" && e.chain !== undefined) idea(e).error = e;
    else if (e.type === "done" && m.sessions[s]) m.sessions[s].done = true;
  }
  m.done = m.sessions.length > 0 && m.sessions.every((x) => !x || x.done);
  for (const r of m.ideas.values()) r.live = [...r.sessions].some((s) => m.sessions[s] && !m.sessions[s].done) && r.results.length < r.expected;
  m.problem = m.lab?.domain || "squares";  // the workspace's first problem: results without a problem field are its
  const seen = new Map();
  for (const x of m.sessions) for (const [p, n] of (x && (x.instances || (x.targets || []).map((n) => [x.domain || m.problem, n]))) || []) seen.set(`${p}:${n}`, { p, n });
  m.instances = [...seen.values()].sort((a, b) => a.p.localeCompare(b.p) || a.n - b.n);
  m.targets = [...new Set(m.instances.map((i) => i.n))].sort((a, b) => a - b);
  m.bestValue = {};
  for (const r of m.ideas.values()) for (const x of r.results) {
    const k = `${x.problem || m.problem}:${x.n}`;
    if (!x.error && x.polished != null && !(x.polished >= m.bestValue[k])) m.bestValue[k] = x.polished;
  }
  return m;
}

const model = (id) => {
  const book = S.books[id];
  if (!book || !book.model) return null;
  return S.replay && S.replay.lab === id ? buildModel(book.events, S.replay.t) : book.model;
};
const summary = (id) => S.labs.find((l) => l.id === id);

// ---------- words and numbers ----------
const span = (ns) => {
  const t = [...new Set(ns)].sort((a, b) => a - b), parts = [];
  for (let i = 0; i < t.length; i++) {
    let j = i;
    while (j + 1 < t.length && t[j + 1] === t[j] + 1) j++;
    parts.push(j > i ? `${t[i]}–${t[j]}` : `${t[i]}`);
    i = j;
  }
  return parts.join(", ");
};
const listN = (ns) => ns.length > 1 ? `${ns.slice(0, -1).join(", ")} and ${ns[ns.length - 1]}` : `${ns[0]}`;
const plain = (x) => (x < 1e-6 ? "less than 0.000001" : Number(x.toPrecision(2)).toString());
const side6 = (x) => Number(x).toFixed(6);
const clock = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
const duration = (s) => (s < 5400 ? `${Math.max(1, Math.round(s / 60))} min` : `${(s / 3600).toFixed(1)} h`);
const sizesWord = (k) => `${k} size${k === 1 ? "" : "s"}`;

function labTitle(l) {
  if (!l) return "";
  if (l.label) return l.label;
  if ((l.all_targets || []).length) return `n = ${span(l.all_targets)}`;
  return l.request || l.name;
}

// "Symmetry-aware cut-and-splice genetic search from molecular and atomic cluster optimization: …" ->
// name "Symmetry-aware cut-and-splice genetic search", field "molecular and atomic cluster optimization"
function idea(strategy) {
  if (!strategy) return { name: "", field: "" };
  if (strategy.name) return { name: strategy.name, field: strategy.field || "" };
  const head = (strategy.source || "").split(/:\s/)[0].split(/\.\s/)[0];
  const m = head.match(/^(.*?),?\s+(?:adapted\s+|imported\s+)?from\s+(.*)$/i);
  let name = m ? m[1] : head.split(",")[0];
  let field = m ? m[2].split(/,|;|\s+combined with\s+|\s+used as\s+|\s+adapted\s+/)[0] : "";
  if (name.length > 70) name = name.slice(0, 67).replace(/\s+\S*$/, "") + "…";
  if (field.length > 60) field = field.slice(0, 57).replace(/\s+\S*$/, "") + "…";
  return { name: name.charAt(0).toUpperCase() + name.slice(1), field };
}

const seeds = (lab) => (lab && lab.seeds && lab.seeds.length ? lab.seeds.length : 1);
const recordSizes = (r) => [...new Set(r.records.map((x) => x.n))].sort((a, b) => a - b);

function outcome(r, m) {
  if (r.error) return { kind: "fail", text: "The model call failed." };
  if (!r.strategy) return { kind: "wait", text: "Writing a strategy…" };
  if (r.live) return { kind: "live", text: `Testing: ${r.results.length} of ${r.expected} runs finished.`, short: `testing · ${r.results.length} of ${r.expected}` };
  const found = recordSizes(r);
  const links = (ns) => listN(ns.map((n) => `<a data-act="instance" data-n="${n}">${n}</a>`));
  if (!r.results.length) {  // imported reruns that kept only their record-breaking runs
    const note = " Only the record-breaking runs were saved.";
    return found.length ? { kind: "star", text: `New best-known for n = ${listN(found)}.${note}`, html: `New best-known for n = ${links(found)}.${note}`, short: `n = ${found.join(", ")}` }
      : { kind: "none", text: "No results were saved." };
  }
  const sizes = [...new Set(r.results.map((x) => x.n))];
  const errors = r.results.filter((x) => x.error);
  if (found.length) {
    const held = sizes.filter((n) => !found.includes(n)).length;
    const rest = held > 0 ? ` The best known held on the other ${sizesWord(held)}.` : "";
    return { kind: "star", text: `New best-known for n = ${listN(found)}.${rest}`, html: `New best-known for n = ${links(found)}.${rest}`, short: `n = ${found.join(", ")}` };
  }
  if (errors.length === r.results.length) return { kind: "fail", text: `The code failed on every size: ${lastLine(errors[0].error)}`, short: "code failed" };
  const ok = r.results.filter((x) => !x.error);
  if (ok.length && ok.every((x) => x.gap == null)) {  // no published values: compare with the rest of the workspace
    const tops = [...new Set(ok.filter((x) => x.polished <= m.bestValue[`${x.problem || m.problem}:${x.n}`] + 1e-9).map((x) => x.n))].sort((a, b) => a - b);
    const text = (tops.length ? `Best in this workspace on n = ${listN(tops)}.` : `Not the best in this workspace on any of the ${sizesWord(new Set(ok.map((x) => x.n)).size)}.`)
      + (errors.length ? ` The code failed on ${errors.length} of ${r.results.length} runs.` : "");
    return { kind: tops.length ? "reached" : "none", text, short: tops.length ? `best on n = ${tops.join(", ")}` : "" };
  }
  const best = (n) => Math.min(...r.results.filter((x) => x.n === n && !x.error && x.gap != null).map((x) => x.gap));
  const tried = sizes.filter((n) => Number.isFinite(best(n)));
  const reached = knownGiven(m) ? [] : tried.filter((n) => best(n) <= 1e-6).sort((a, b) => a - b);
  let text;
  if (reached.length) text = `Reached the best known on ${reached.length} of ${sizesWord(tried.length)} (n = ${listN(reached)}).`;
  else if (!knownGiven(m)) {
    const closest = tried.map((n) => [n, best(n)]).sort((a, b) => a[1] - b[1])[0];
    text = `Did not reach the best known; closest ${plain(closest[1])} above it (n = ${closest[0]}).`;
  } else {
    const near = r.results.filter((x) => x.runner_up_gap > 0).sort((a, b) => a.runner_up_gap - b.runner_up_gap)[0];
    text = near ? `No improvement. The closest other solution came within ${plain(near.runner_up_gap)} of the best known (n = ${near.n}).` : `No improvement on any of the ${sizesWord(sizes.length)}.`;
  }
  if (errors.length) text += ` The code failed on ${errors.length} of ${r.results.length} runs.`;
  return { kind: reached.length ? "reached" : "none", text, short: reached.length ? `reached ${reached.length} of ${tried.length}` : "" };
}
const lastLine = (e) => String(e || "").split("\n").map((s) => s.trim()).filter(Boolean).slice(-1)[0] || "";
const markHTML = (kind) => (kind === "star" ? ICON.star : kind === "fail" ? ICON.fail : `<span class="ring ${kind === "live" ? "spin" : kind === "wait" ? "wait" : kind === "reached" ? "full" : ""}"></span>`);

// ---------- packings ----------
function figure(poses, side) {
  const square = (x, y, a, style, width) => `<rect x="-0.5" y="-0.5" width="1" height="1" transform="translate(${x} ${side - y}) rotate(${(-a * 180) / Math.PI})" style="${style}" stroke-width="${width}" vector-effect="non-scaling-stroke"/>`;
  let out = `<svg viewBox="-0.05 -0.05 ${side + 0.1} ${side + 0.1}" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="${side}" height="${side}" style="fill:var(--paper);stroke:var(--sq-edge)" stroke-width="1" vector-effect="non-scaling-stroke"/>`;
  for (const [x, y, a] of poses) out += square(x, y, a, "fill:var(--sq);stroke:var(--sq-edge)", 0.75);
  return out + "</svg>";
}

function catalogueSVG(poses, side, n) {
  const uses = poses.map(([x, y, a]) => `        <use xlink:href="#one" transform="translate(${x} ${side - y}) rotate(${(-a * 180) / Math.PI}) translate(-0.5 -0.5)"/>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<!--\n    ${n} unit squares in a square of side ${side}.\n-->\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" [\n    <!ENTITY  s "${side}">\n    <!ENTITY hs  "${side / 2}">\n]>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="100%" viewBox="-&hs; -&hs; &s; &s;" style="fill:#B2B2B2; stroke:black; stroke-width:0.002" id="svg">\n    <defs>\n        <rect width="&s;" height="&s;" id="outer" x="-&hs;" y="-&hs;"/>\n        <rect width="1"   height="1"   id="one"/>\n    </defs>\n    <use xlink:href="#outer" style="fill:white; stroke:none"/>\n    <g transform="translate(-&hs; -&hs;)">\n${uses}\n    </g>\n    <use xlink:href="#outer" style="fill:none"/>\n</svg>\n`;
}
function download(name, text, type) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
}

// ---------- sidebar ----------
function renderSide() {
  const labs = S.labs.map((l) => {
    const found = Object.keys(l.records).length;
    return `<button class="item ${S.lab === l.id && !S.compose ? "on" : ""}" data-act="lab" data-id="${esc(l.id)}">
      <span class="name">${esc(labTitle(l))}</span>${l.running ? '<span class="live-dot" title="running"></span>' : found ? `<span class="aside"><span class="star">★</span> ${found}</span>` : ""}</button>`;
  }).join("");
  const dark = (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")) === "dark";
  $("#side").innerHTML = `<div class="brand">${LOGO} Mosa</div>
    <button class="new" data-act="compose">${ICON.plus} New workspace</button>
    <div class="list"><div class="heading">Workspaces</div>${labs}</div>
    <div class="side-foot"><button class="icon-btn" data-act="theme" title="${dark ? "Light" : "Dark"} theme">${dark ? ICON.sun : ICON.moon}</button></div>`;
}

// ---------- main: the lab ----------
function renderMain() {
  const el = $("#main");
  if (S.compose) {  // built once: the periodic refresh must not wipe what is being typed
    if (!el.querySelector(".compose")) el.innerHTML = composeView();
    return;
  }
  const m = model(S.lab), l = summary(S.lab);
  if (m && !m.lab && m.requests.length) {  // nothing has run yet: the conversation (right) is where things happen
    el.innerHTML = `<div class="lab-head"><div class="head-text"><h1>${esc(labTitle(l))}</h1></div></div>`;
    return;
  }
  if (!m || !m.lab) { el.innerHTML = `<div class="empty">${S.labs.length ? "Loading…" : "No workspaces yet. Start one with New workspace."}</div>`; return; }
  const L = m.lab, brief = (m.sessions.filter((x) => x && x.brief).slice(-1)[0] || {}).brief || "";  // what the researchers are told now
  const replay = S.replay && S.replay.lab === S.lab
    ? `<div class="replay"><button class="icon-btn" data-act="replay-toggle">${S.replay.playing ? ICON.pause : ICON.play}</button>
        <input type="range" id="scrub" min="${S.replay.start}" max="${S.replay.end}" value="${S.replay.t}"><span class="time">${clock(S.replay.t)}</span>
        <button class="icon-btn" data-act="replay-stop" title="Stop replay">${ICON.close}</button></div>`
    : m.done ? `<button class="text-btn" data-act="replay">${ICON.replay} Replay</button>` : "";
  el.innerHTML = `<div class="lab-head"><div class="head-text"><h1>${esc(labTitle(l || L))}</h1>${brief ? `<p class="bio">${esc(brief)}</p>` : ""}</div>${replay}</div>${instancesHTML(m)}${mapHTML(m)}`;
}

// Where each instance stands: ★ a verified new best-known; ● the best known reached (only meaningful when no known
// solution was given to start from); ○ not reached.
const knownGiven = (m) => (m.lab?.domain || "squares") === "squares";
function instanceState(m, n, p = m.problem) {
  const mine = (x) => x.n === n && (x.problem || m.problem) === p;
  const rounds = [...m.ideas.values()];
  const records = rounds.flatMap((r) => r.records).filter(mine).sort((a, b) => a.side - b.side);
  const results = rounds.flatMap((r) => r.results.map((x) => ({ ...x, key: r.key }))).filter((x) => mine(x) && !x.error && x.polished != null);
  const best = results.sort((a, b) => a.polished - b.polished)[0] || null;
  const kind = records.length ? "star" : !knownGiven(m) && best && best.gap != null && best.gap <= 1e-6 ? "reached" : "none";
  return { n, p, kind, record: records[0] || null, best, tried: results.length > 0 };
}
// A problem's short name, for a workspace holding several related problems.
const problemName = (p) => p === "circle-radii" ? "Sum of radii" : p === "riesz-inf" ? "Tammes (s = ∞)" : p === "thomson" ? "Thomson (s = 1)" : p === "riesz-0" ? "Logarithmic (s = 0)" : p.startsWith("riesz-") ? `Riesz s = ${p.slice(6)}` : p;
// The workspace's instances: plain numbers, with a new best-known (★) or a reached best known (●) standing out.
function instancesHTML(m) {
  const states = m.instances.map((i) => instanceState(m, i.n, i.p));
  if (!states.length) return "";
  const on = (s) => S.sel?.type === "instance" && S.sel.lab === S.lab && S.sel.n === s.n && (S.sel.problem || m.problem) === s.p;
  const link = (s) => `<a class="inst-link ${s.kind} ${on(s) ? "on" : ""}" data-act="instance" data-n="${s.n}" data-p="${esc(s.p)}">${s.kind === "star" ? "★" : s.kind === "reached" ? "●" : ""}${s.n}</a>`;
  const problems = [...new Set(states.map((s) => s.p))];
  if (problems.length === 1) return `<div class="instances">${states.map(link).join("")}</div>`;
  return `<div class="instances grouped">${problems.map((p) => `<div class="inst-row"><span class="inst-problem">${esc(problemName(p))}</span>${states.filter((s) => s.p === p).map(link).join("")}</div>`).join("")}</div>`;
}

function threads(m) {
  const out = new Map();
  for (const r of m.ideas.values()) {
    if (!r.strategy && !r.prompt && !r.error) continue;
    const solo = (m.sessions[r.session] || {}).kind === "apply";
    const key = solo ? "strategies" : `researcher ${r.chain}`;
    if (!out.has(key)) out.set(key, { key, solo, chain: solo ? 1e9 : r.chain, ideas: [] });
    out.get(key).ideas.push(r);
  }
  return [...out.values()].sort((a, b) => a.chain - b.chain).map((x) => ({ ...x, ideas: x.ideas.sort((a, b) => a.round - b.round || a.session - b.session) }));
}

function mapHTML(m) {
  const rows = threads(m).map((th) => {
    const ideas = th.ideas.map((r) => {
      const o = outcome(r, m), it = idea(r.strategy);
      const on = S.sel?.type === "idea" && S.sel.lab === S.lab && S.sel.idea === r.key;
      return `<button class="idea ${o.kind} ${on ? "on" : ""}" data-act="idea" data-idea="${r.key}">
        <span class="mark">${markHTML(o.kind)}</span>
        <div class="title">${esc(it.name || (o.kind === "wait" ? "Thinking…" : "—"))}</div>
        ${it.field ? `<div class="field">${esc(it.field)}</div>` : ""}
        ${o.kind === "star" ? `<div class="found">★ ${esc(o.short)}</div>` : o.short ? `<div class="state">${esc(o.short)}</div>` : ""}</button>`;
    }).join("");
    return `<div class="lane"><div class="who">${th.solo ? "Strategies" : `Researcher ${th.chain + 1}`}</div><div class="thread">${ideas}</div></div>`;
  }).join("");
  return `<div class="map">${rows}</div>`;
}

// ---------- detail: the selection ----------
// The right side: the conversation, or the idea or instance you opened, always with the message box underneath. A
// message sent while something is open is about it ("run this on 88-90", "why did this fail?").
function renderDetail() {
  const el = $("#detail");
  const pane = S.sel ? (S.sel.type === "idea" ? ideaView() : instanceView()) : "";
  const chat = !S.sel && S.lab && !S.compose;
  el.hidden = !(pane || chat);
  el.classList.add("chat-mode");
  if (el.hidden) return;
  const draft = $("#chat-input")?.value || "", old = el.querySelector(".messages, .scroll");
  const atEnd = !old || old.scrollHeight - old.scrollTop - old.clientHeight < 40, top = old?.scrollTop || 0;
  const open = [...el.querySelectorAll("details[open] > summary")].map((s) => s.textContent);
  const wasPane = old?.classList.contains("scroll"), samePane = wasPane && el.dataset.sel === JSON.stringify(S.sel);
  el.innerHTML = `<div class="chat">${pane
    ? `<div class="scroll"><button class="icon-btn close" data-act="unselect" title="Back to the conversation (Esc)">${ICON.close}</button>${pane}</div>`
    : `<div class="messages">${messagesHTML()}</div>`}${composerHTML()}</div>`;
  el.dataset.sel = JSON.stringify(S.sel);
  if (draft) $("#chat-input").value = draft;
  el.querySelectorAll("details > summary").forEach((s) => { if (open.includes(s.textContent)) s.parentElement.open = true; });
  if (window.hljs) el.querySelectorAll("code.language-python").forEach((c) => window.hljs.highlightElement(c));
  const fresh = el.querySelector(".messages, .scroll");
  if (pane) fresh.scrollTop = samePane ? top : 0;
  else fresh.scrollTop = atEnd || wasPane ? fresh.scrollHeight : top;
}

function composerHTML() {
  const m = model(S.lab), r = S.sel?.type === "idea" ? m?.ideas.get(S.sel.idea) : null;
  const hint = r ? `Ask about “${idea(r.strategy).name || "this idea"}”, or run it on more instances…`
    : S.sel?.type === "instance" ? `Ask about n = ${S.sel.n}…` : "Direct the research, or ask about it…";
  return `<div class="composer"><div class="box"><textarea id="chat-input" rows="2" placeholder="${esc(hint)}"></textarea><button class="send" data-act="send" title="Send (Enter)">${ICON.send}</button></div></div>`;
}

function resultsTable(r, m) {
  const by = new Map();
  for (const x of r.results) { if (!by.has(x.n)) by.set(x.n, []); by.get(x.n).push(x); }
  const rows = [...by.entries()].sort((a, b) => a[0] - b[0]).map(([n, xs]) => {
    const recs = xs.filter((x) => x.record), errors = xs.filter((x) => x.error);
    let text;
    if (recs.length) {
      const best = recs.sort((a, b) => a.gap - b.gap)[0];
      text = `<span class="star">★</span> ${plain(-best.gap)} smaller than the best known${xs.length > 1 ? ` (on ${recs.length} of ${xs.length} seeds)` : ""}`;
    } else if (errors.length === xs.length) text = `<span class="err">failed: ${esc(lastLine(errors[0].error))}</span>`;
    else {
      const near = xs.filter((x) => x.runner_up_gap > 0).map((x) => x.runner_up_gap).sort((a, b) => a - b)[0];
      text = near ? `held; closest other packing within ${plain(near)}` : "held";
      if (errors.length) text += ` <span class="err">(${errors.length} failed)</span>`;
    }
    return `<tr><td class="n">${n}</td><td>${text}</td></tr>`;
  }).join("");
  return `<table>${rows}</table>`;
}

function ideaView() {
  const m = model(S.sel.lab), r = m && m.ideas.get(S.sel.idea);
  if (!r) return "";
  const o = outcome(r, m), it = idea(r.strategy), s = r.strategy || {};
  const kind = { new: "new idea", refine: "refinement", combine: "combination" }[s.decision];
  const ses = m.sessions[r.session] || {};
  const who = ses.kind === "apply" ? "Strategy" : `Researcher ${r.chain + 1} · round ${r.round}${kind ? ` · ${kind}` : ""}`;
  return `<div class="pane">
    <div class="eyebrow">${who}</div>
    <h2>${esc(it.name || "Thinking…")}</h2>${it.field ? `<div class="from">from ${esc(it.field)}</div>` : ""}
    <div class="outcome">${markHTML(o.kind)}<span>${o.html || esc(o.text)}</span></div>
    ${s.mapping ? `<div class="section"><div class="section-label">Why the researcher expected it to work</div><div class="prose">${esc(s.mapping)}</div></div>` : ""}
    ${s.strategy ? `<div class="section"><div class="section-label">What it does</div><div class="prose">${esc(s.strategy)}</div></div>` : ""}
    ${r.results.length ? `<details><summary>Results on each size</summary>${resultsTable(r, m)}</details>` : ""}
    ${s.code ? `<details><summary>Code</summary><pre class="code"><code class="language-python">${esc(s.code)}</code></pre></details>` : ""}
    ${r.prompt ? `<details><summary>What the researcher was told</summary><pre class="code plain">${esc(r.prompt.prompt)}</pre></details>` : ""}
  </div>`;
}

function instanceView() {
  const m = S.books[S.sel.lab]?.model;  // the whole notebook, even mid-replay
  if (!m) return "";
  const n = S.sel.n, domain = S.sel.problem || m.problem, st = instanceState(m, n, domain);
  const what = `${n} squares in a square`;
  const by = (x) => {
    if (!x) return "";
    const key = x.key || ideaKey(x), r = m.ideas.get(key);
    const it = r ? idea(r.strategy) : idea({ source: m.lab.source });
    const ses = m.sessions[r?.session ?? 0] || {};
    const later = x.session !== undefined && r && x.session !== r.session ? ", when it was run on more instances" : "";
    return ses.kind === "apply" ? `${esc(it.name)}${later}` : `<a data-act="idea" data-idea="${key}">Researcher ${r.chain + 1}, round ${r.round}</a>: ${esc(it.name)}${later}`;
  };
  if (domain !== "squares") return otherInstance(m, n, st, domain, by);
  if (st.record) return discoveryView(st.record, what, by(st.record));
  const ref = S.refs[n];
  if (!ref) reference(n, domain);
  return `<div class="pane"><div class="eyebrow">Instance</div><h2>${what}</h2>
    ${ref && ref !== "loading" && ref.poses ? `<div class="figure">${figure(ref.poses, ref.side)}</div>` : ""}
    <div class="numbers">${st.tried ? `No improvement: the best known packing (side <span class="mono">${side6(ref?.side || b?.best_known || 0)}</span>) held.` : "Not tried yet."}</div>
    ${b && b.runner_up_gap > 0 ? `<div class="section">The closest other packing came within ${plain(b.runner_up_gap)} of it.</div>` : ""}</div>`;
}

// Any problem other than squares: its best solution (drawn as points on a sphere, or by the problem's own harness), and
// how it compares with the published value, if there is one.
const onSphere = (d) => d === "thomson" || d.startsWith("riesz-");
const value10 = (v) => `<span class="mono">${Number(v).toPrecision(10)}</span>`;
const maximized = (p) => p === "circle-radii" || p === "riesz-inf";  // stored as minus the quantity: shown as the quantity
function otherInstance(m, n, st, domain, by) {
  const b = st.best, rec = st.record, sgn = maximized(domain) ? -1 : 1, word = maximized(domain) ? ["below", "above"] : ["above", "below"];
  const shown = (v) => value10(sgn * v);
  const what = domain === "circle-radii" ? `${n} circles in a square, largest sum of radii` : domain === "riesz-inf" ? `${n} points on a sphere, farthest apart (Tammes)` : domain === "thomson" ? `${n} charges on a sphere (Thomson)` : domain === "riesz-0" ? `${n} points on a sphere, logarithmic energy`
    : domain.startsWith("riesz-") ? `${n} points on a sphere, Riesz ${domain.slice(6)}-energy` : `${m.lab.title}, n = ${n}`;
  const picture = !b?.best ? "" : onSphere(domain) ? `<div class="figure sphere">${sphere(b.best.x)}</div>`
    : `<div class="figure"><img alt="" src="/api/svg?lab=${encodeURIComponent(S.sel.lab)}&n=${n}&problem=${encodeURIComponent(domain)}&v=${b.polished}"></div>`;
  const numbers = !b ? "Not tried yet."
    : rec ? `${shown(rec.value)}, ${plain(rec.improvement)} ${word[1]} the best known ${shown(rec.reference_side)}.`
    : b.best_known == null ? `Best found ${shown(b.polished)}. There is no published value for this instance: ideas are compared with each other.`
    : b.gap <= 1e-6 ? `Reached the best known value ${shown(b.best_known)}.`
    : `Best found ${shown(b.polished)}, ${plain(b.gap)} ${word[0]} the best known ${shown(b.best_known)}.`;
  return `<div class="pane"><div class="eyebrow">${rec ? "Discovery" : "Instance"}</div><h2>${esc(what)}</h2>${picture}
    <div class="numbers">${numbers}</div>
    ${rec ? `<div class="section"><div class="verified">${ICON.check} Verified by the problem's independent checker</div></div>` : ""}
    ${b ? `<div class="section"><div class="section-label">${rec ? "Found by" : "Best found by"}</div>${by(rec || b)}</div>` : ""}</div>`;
}

function discoveryView(d, what, by) {
  const ref = S.refs[d.n];
  if (!ref) reference(d.n, "squares");
  const ready = ref && ref !== "loading";
  const view = ready ? S.view : "after";
  const pct = (100 * d.improvement / d.reference_side).toPrecision(2);
  const info = ready ? ref.info : null;
  S.download = d;
  return `<div class="pane">
    <div class="eyebrow">Discovery</div>
    <h2>${what}</h2>
    <div class="toggle">${[["after", "Mosa"], ["before", "Previous best"]].map(([v, label]) => `<button class="${view === v ? "on" : ""}" data-act="view" data-v="${v}">${label}</button>`).join("")}</div>
    <div class="figure">${view === "before" ? figure(ref.poses, ref.side) : figure(d.poses, d.side)}</div>
    <div class="numbers">Side <span class="mono">${side6(d.side)}</span>, ${plain(d.improvement)} smaller than the best known <span class="mono">${side6(d.reference_side)}</span> (${pct}%).</div>
    <div class="section"><div class="verified">${ICON.check} Verified</div>
      <ul class="checks"><li>No overlap at zero tolerance</li><li>Confirmed at 80 and 160 digits of precision</li><li>Every gap between squares, and to the walls, is at least ${Number(d.min_pair_clearance).toExponential(0)}</li></ul></div>
    <div class="section"><div class="section-label">Found by</div>${by}</div>
    ${info?.notes ? `<details><summary>Previous record</summary><div class="prose" style="color:var(--muted)">${info.official ? `Catalogue value ${side6(info.official)}. ` : ""}${esc(info.notes)}</div></details>` : ""}
    <div class="section" style="display:flex;gap:8px"><button class="btn" data-act="svg">${ICON.download} square-${d.n}.svg</button><button class="btn quiet" data-act="json">JSON</button></div>
  </div>`;
}

// Charges on the sphere, seen from slightly above: near side filled, far side hollow.
function sphere(points) {
  const c = Math.cos(0.4), s = Math.sin(0.4);
  const ps = points.map(([x, y, z]) => { const r = Math.hypot(x, y, z); return [x / r, (y * c - z * s) / r, (y * s + z * c) / r]; }).sort((a, b) => a[2] - b[2]);
  return `<svg viewBox="-1.08 -1.08 2.16 2.16" xmlns="http://www.w3.org/2000/svg"><circle r="1" style="fill:var(--paper);stroke:var(--sq-edge)" stroke-width="1" vector-effect="non-scaling-stroke"/>` +
    ps.map(([x, y, z]) => `<circle cx="${x.toFixed(4)}" cy="${(-y).toFixed(4)}" r="0.028" style="fill:${z > 0 ? "var(--strong)" : "none"};stroke:${z > 0 ? "var(--strong)" : "var(--faint)"}" stroke-width="1" vector-effect="non-scaling-stroke"/>`).join("") + "</svg>";
}

// The workspace's conversation: your messages, the agent's replies and plans, and a note when a session finishes.
function messagesHTML() {
  const book = S.books[S.lab];
  if (!book) return "";
  const items = [];
  let waiting = false;
  for (const e of book.events) {
    if (e.type === "request") { items.push(`<div class="msg user">${contextHTML(book, e.context)}${esc(e.request)}</div>`); waiting = true; }
    else if (e.type === "reply") { items.push(`<div class="msg agent">${esc(e.reply)}</div>`); waiting = e.drafting ? "Writing the harness and testing it" : false; }
    else if (e.type === "harness") { items.push(harnessHTML(e)); waiting = e.report?.passed ? "Planning the session" : "Writing the harness again"; }
    else if (e.type === "plan" && e.action === "apply") {
      items.push(`<div class="msg agent">${esc(e.reply || "")}<div class="plan">Running it on n = ${esc(span(e.targets))}${e.seeds > 1 ? `, ${e.seeds} seeds each` : ""}</div></div>`);
      waiting = false;
    } else if (e.type === "plan") {
      items.push(`<div class="msg agent">${esc(e.reply || e.reasoning || "")}<div class="plan">${e.researchers} researcher${e.researchers > 1 ? "s" : ""} × ${e.rounds} round${e.rounds > 1 ? "s" : ""} on n = ${esc(span(e.targets))}${e.seeds > 1 ? `, ${e.seeds} seeds each` : ""}</div></div>`);
      waiting = false;
    } else if (e.type === "done") {
      const s = e.session ?? 0, recs = [...new Set(book.events.filter((x) => x.type === "record" && x.record && (x.session ?? 0) === s).map((x) => x.n))].sort((a, b) => a - b);
      const results = book.events.filter((x) => x.type === "result" && (x.session ?? 0) === s && !x.error && x.gap != null);
      const reached = (book.model?.lab?.domain || "squares") !== "squares" ? [...new Set(results.filter((x) => x.gap <= 1e-6).map((x) => x.n))].sort((a, b) => a - b) : [];
      const unpublished = results.length === 0 && book.events.some((x) => x.type === "result" && (x.session ?? 0) === s && !x.error && x.polished != null);
      const found = [...new Set(book.events.filter((x) => x.type === "result" && (x.session ?? 0) === s && !x.error && x.polished != null).map((x) => x.n))].sort((a, b) => a - b);
      const note = recs.length ? `★ New best-known for n = ${listN(recs.map((n) => `<a data-act="instance" data-n="${n}">${n}</a>`))}.`
        : unpublished ? `Best packings found for n = ${listN(found.map((n) => `<a data-act="instance" data-n="${n}">${n}</a>`))}; there are no published values to compare with.`
        : reached.length ? `Reached the best known on n = ${listN(reached.map((n) => `<a data-act="instance" data-n="${n}">${n}</a>`))}.` : "No improvement this time.";
      items.push(`<div class="msg note">Session finished · ${note}</div>`);
    }
  }
  const draft = summary(S.lab)?.drafting;  // the drafting model's latest message, while it writes and tests a harness
  if (waiting) items.push(`<div class="msg agent thinking"><span class="ring spin"></span> ${typeof waiting === "string" ? waiting : "Thinking"}${draft
    ? ` <span class="elapsed">${Math.floor(draft.seconds / 60)} min</span>${draft.note ? `<div class="draft-note">${esc(draft.note)}</div>` : ""}` : ""}</div>`);
  if (!items.length) items.push(`<div class="msg note">Direct the research here: ask for more instances, a new focus, or why something failed.</div>`);
  return items.join("");
}

// What a message was about, as a link back to it.
function contextHTML(book, c) {
  if (!c) return "";
  if (c.idea) {
    const r = book.model?.ideas.get(c.idea);
    return `<a class="about" data-act="idea" data-idea="${esc(c.idea)}">${esc(r ? idea(r.strategy).name || "an idea" : "an idea")}</a>`;
  }
  return c.n ? `<a class="about" data-act="instance" data-n="${c.n}" data-p="${esc(c.problem || "")}">${c.problem ? `${esc(problemName(c.problem))}, ` : ""}n = ${c.n}</a>` : "";
}

// A harness drafted for a problem outside the library: what it is, how its self-test went, and its code.
function harnessHTML(e) {
  const r = e.report || {}, sizes = r.sizes || [];
  const rows = sizes.map((s) => `<li>n = ${s.n}: ${s.invalid ? `${s.invalid} of 4 solutions failed the checker` : "all 4 solutions passed the checker"}${s.best_known != null ? `, best ${Number(s.best_found).toPrecision(8)} against the published ${Number(s.best_known).toPrecision(8)}` : `, best ${Number(s.best_found).toPrecision(8)}`}</li>`).join("");
  const verdict = r.passed ? `${ICON.check} Passed its self-test` : `${ICON.fail} Failed its self-test`;
  return `<div class="msg agent"><div class="section-label">New problem</div><strong>${esc(e.title)}</strong>
    <div class="harness-about">${esc(e.about || "")}</div>
    <div class="harness-verdict ${r.passed ? "ok" : "bad"}">${verdict}</div>
    ${rows ? `<ul class="checks">${rows}${r.rejects_malformed === false ? "<li>does not reject malformed solutions</li>" : ""}</ul>` : ""}
    ${r.error ? `<pre class="code plain">${esc(lastLine(r.error))}</pre>` : ""}
    <details><summary>Harness code</summary><pre class="code"><code class="language-python">${esc(e.code || "")}</code></pre></details></div>`;
}

async function send() {
  const box = $("#chat-input"), text = box.value.trim();
  if (!text) return;
  const m = model(S.lab), backend = (m?.sessions.filter(Boolean).slice(-1)[0] || {}).backend || "modal";
  const context = S.sel?.type === "idea" ? { idea: S.sel.idea } : S.sel?.type === "instance" ? { n: S.sel.n, problem: S.sel.problem } : undefined;
  box.value = "";
  S.sel = null;  // back to the conversation, where the answer appears
  try { await api("/api/launch", { kind: "run", workspace: S.lab, prompt: text, backend, context }); await refresh(); render(); }
  catch (e) { box.value = text; alert(e.message); }
}

// ---------- new lab ----------
function composeView() {
  const c = S.compose;
  const here = c.workspace ? labTitle(summary(c.workspace)) : "";
  const examples = c.workspace ? ["Continue, and focus on the instances that are still open", "Try constructions from scratch instead of perturbing the best known"]
    : ["Beat the 2024 records for packing 85–90 unit squares in a square",
       "Points on a sphere for n = 30–33: Smale's logarithmic energy, Thomson's Coulomb energy and Tammes' largest smallest distance, side by side",
       "Beat AlphaEvolve and ShinkaEvolve on 26 circles in a square, maximizing the sum of radii",
       "Heilbronn's triangle problem: place 8–12 points in a unit square so that the smallest triangle is as large as possible"];
  return `<div class="compose">
    <h1>${c.workspace ? `Research in ${esc(here)}` : "New workspace"}</h1>
    <div class="sub">${c.workspace ? "Say what to do next. The research agent continues the same researchers; they see everything this workspace has found."
      : "Say what you want to research. The research agent picks the problem from the library, or writes and tests a harness for a new one, then chooses the instances, researchers and rounds."}</div>
    <div class="field-row"><textarea id="f-prompt" class="prompt">${esc(c.prompt || "")}</textarea>
      <div class="examples">${examples.map((x) => `<a data-act="example">${esc(x)}</a>`).join("")}</div></div>
    ${computeRow(c)}
    <div style="margin-top:18px"><button class="btn" data-act="start">${c.workspace ? "Start" : "Create and start"}</button><span class="note" id="f-note"></span></div>
  </div>`;
}
const computeRow = (c) => `<div class="field-row"><div class="choice compute"><span>Compute</span><label><input type="radio" name="f-compute" value="modal" ${c.backend === "modal" ? "checked" : ""}> Modal</label><label><input type="radio" name="f-compute" value="local" ${c.backend === "local" ? "checked" : ""}> This machine</label></div></div>`;

const parseSizes = (text) => String(text).split(/[\s,]+/).filter(Boolean).flatMap((p) => {
  const m = p.match(/^(\d+)[-–](\d+)$/);
  return m ? Array.from({ length: +m[2] - +m[1] + 1 }, (_, i) => +m[1] + i) : /^\d+$/.test(p) ? [+p] : [];
});

async function start() {
  const c = S.compose, note = $("#f-note");
  const backend = document.querySelector("input[name=f-compute]:checked")?.value || "modal";
  const spec = { kind: "run", workspace: c.workspace || undefined, prompt: $("#f-prompt").value.trim(), backend };
  if (!spec.prompt) { note.textContent = "Say what to research."; return; }
  note.textContent = "Starting…";
  try {
    const r = await api("/api/launch", spec);
    await refresh();
    S.compose = null;
    selectLab(r.id);
  } catch (e) { note.textContent = e.message; }
}

// ---------- status ----------

function render() { renderSide(); renderMain(); renderDetail(); }

// ---------- navigation ----------
function selectLab(id) {
  S.lab = id; S.compose = null;
  S.sel = null;
  if (!S.books[id]) loadBook(id).then(render);
  render();
}
function selectIdea(lab, key) {
  if (S.lab !== lab) { S.lab = lab; if (!S.books[lab]) loadBook(lab).then(render); }
  S.compose = null;
  S.sel = { type: "idea", lab, idea: key };
  render();
}
function move(dx, dy) {
  if (S.sel?.type !== "idea") return;
  const m = model(S.lab), all = threads(m), r = m.ideas.get(S.sel.idea);
  const i = all.findIndex((th) => th.session === r.session && th.chain === r.chain) + dy;
  if (i < 0 || i >= all.length) return;
  const ideas = all[i].ideas, j = Math.max(0, Math.min(ideas.length - 1, ideas.findIndex((x) => x.round === r.round) + dx));
  selectIdea(S.lab, (ideas[j] || ideas[ideas.length - 1]).key);
}

let timer = null;
function replayStart() {
  const m = S.books[S.lab]?.model;
  S.replay = { lab: S.lab, start: Math.floor(m.start), end: Math.ceil(m.end), t: Math.floor(m.start), playing: true };
  replayRun();
}
function replayRun() {
  clearInterval(timer);
  if (!S.replay?.playing) return render();
  const r = S.replay, step = Math.max(1, (r.end - r.start) / 400);  // a whole lab in about 40 seconds
  timer = setInterval(() => {
    r.t = Math.min(r.end, r.t + step);
    if (r.t >= r.end) { r.playing = false; clearInterval(timer); }
    renderMain(); renderDetail();
  }, 100);
  render();
}

document.addEventListener("click", (ev) => {
  const el = ev.target.closest("[data-act]");
  if (!el) return;
  const d = el.dataset;
  switch (d.act) {
    case "lab": selectLab(d.id); break;
    case "idea": selectIdea(S.lab, d.idea); break;
    case "instance": S.sel = { type: "instance", lab: S.lab, n: +d.n, problem: d.p || undefined }; S.view = "after"; S.compose = null; render(); break;
    case "unselect": S.sel = null; render(); break;
    case "view": S.view = d.v; renderDetail(); break;
    case "compose": S.compose = { kind: "run", backend: "modal" }; S.sel = null; render(); $("#f-prompt")?.focus(); break;
    case "send": send(); break;
    case "example": $("#f-prompt").value = el.textContent; $("#f-prompt").focus(); break;
    case "start": start(); break;
    case "theme": {
      const dark = (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")) === "dark";
      document.documentElement.dataset.theme = dark ? "light" : "dark";
      try { localStorage.setItem("mosa-theme", document.documentElement.dataset.theme); } catch (e) { /* no storage */ }
      render();
      break;
    }
    case "replay": replayStart(); break;
    case "replay-toggle": if (S.replay.t >= S.replay.end) S.replay.t = S.replay.start; S.replay.playing = !S.replay.playing; replayRun(); break;
    case "replay-stop": clearInterval(timer); S.replay = null; render(); break;
    case "svg": { const x = S.download; download(`square-${x.n}.svg`, catalogueSVG(x.poses, x.side, x.n), "image/svg+xml"); break; }
    case "json": { const x = S.download; download(`n${x.n}.json`, JSON.stringify({ n: x.n, side: x.side, previous_best_known: x.reference_side, squares: x.poses.map(([a, b, t]) => ({ x: a, y: b, angle_radians: t })) }, null, 1), "application/json"); break; }
  }
});
document.addEventListener("input", (ev) => {
  if (ev.target.id !== "scrub" || !S.replay) return;  // redraw the map only, so the slider keeps the drag
  S.replay.t = +ev.target.value; S.replay.playing = false; clearInterval(timer);
  $(".map").outerHTML = mapHTML(model(S.lab));
  $(".replay .time").textContent = clock(S.replay.t);
  $(".replay .icon-btn").innerHTML = ICON.play;
  renderDetail();
});
document.addEventListener("keydown", (ev) => {
  if (ev.target.id === "chat-input" && ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); send(); return; }
  if (ev.target.closest("input, textarea")) return;
  if (ev.key === "Escape") { S.sel = null; render(); }
  else if (ev.key === "ArrowRight") { move(1, 0); ev.preventDefault(); }
  else if (ev.key === "ArrowLeft") { move(-1, 0); ev.preventDefault(); }
  else if (ev.key === "ArrowDown") { move(0, 1); ev.preventDefault(); }
  else if (ev.key === "ArrowUp") { move(0, -1); ev.preventDefault(); }
});

// ---------- polling ----------
async function refresh() {
  const [labs, discoveries] = await Promise.all([api("/api/labs"), api("/api/records")]);
  let dirty = JSON.stringify(labs.map((l) => [l.id, l.events])) !== JSON.stringify(S.labs.map((l) => [l.id, l.events])) || discoveries.length !== S.discoveries.length;
  S.labs = labs;
  S.discoveries = discoveries;
  for (const l of labs) if (S.books[l.id] && S.books[l.id].next < l.events) dirty = (await loadBook(l.id)) || dirty;
  return dirty;
}

async function main() {
  try { const t = localStorage.getItem("mosa-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) { /* no storage */ }
  await refresh();
  const first = S.labs.find((l) => l.running) || [...S.labs].sort((a, b) => Object.keys(b.records).length - Object.keys(a.records).length || b.started - a.started)[0];
  await Promise.all(S.labs.filter((l) => l.running).map((l) => loadBook(l.id)));
  if (first) selectLab(first.id); else render();
  setInterval(async () => { if (S.replay) return; try { if (await refresh()) render(); } catch (e) { /* server restarting */ } }, 2500);
}
main();
