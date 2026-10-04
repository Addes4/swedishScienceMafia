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

async function reference(n) {
  if (!S.refs[n]) { S.refs[n] = "loading"; S.refs[n] = await api(`/api/reference?n=${n}`); render(); }
  return S.refs[n];
}

function buildModel(events, until = Infinity) {
  const m = { lab: null, chains: new Map(), start: null, end: null, done: false };
  const round = (e) => {
    const c = e.chain ?? 0, k = e.round ?? 1;
    if (!m.chains.has(c)) m.chains.set(c, new Map());
    const rounds = m.chains.get(c);
    if (!rounds.has(k)) rounds.set(k, { chain: c, round: k, results: [], records: [], progress: {}, prompt: null, strategy: null, done: false, error: null });
    return rounds.get(k);
  };
  for (const e of events) {
    if (e.time > until) continue;
    m.start = m.start === null ? e.time : Math.min(m.start, e.time);
    m.end = m.end === null ? e.time : Math.max(m.end, e.time);
    if (e.type === "lab") m.lab = e;
    else if (e.type === "prompt") round(e).prompt = e;
    else if (e.type === "strategy") round(e).strategy = e;
    else if (e.type === "progress") round(e).progress[`${e.n}/${e.seed}`] = e;
    else if (e.type === "result") { const r = round(e); r.results.push(e); delete r.progress[`${e.n}/${e.seed}`]; }
    else if (e.type === "record" && e.record) round(e).records.push(e);
    else if (e.type === "round") round(e).done = true;
    else if (e.type === "error" && e.chain !== undefined) round(e).error = e;
    else if (e.type === "done") m.done = true;
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
  const sizes = `n = ${span(l.targets || [])}`;
  return sizes;
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
  const sizes = (m.lab?.targets || []).length, expected = sizes * seeds(m.lab);
  if (r.error) return { kind: "fail", text: "The model call failed." };
  if (!r.strategy) return { kind: "wait", text: "Writing a strategy…" };
  if (!r.done && r.results.length < expected) {
    return { kind: "live", text: `Testing on ${seeds(m.lab) > 1 ? `${expected} runs` : sizesWord(sizes)}: ${r.results.length} finished.`, short: `testing · ${r.results.length} of ${expected}` };
  }
  const found = recordSizes(r);
  const errors = r.results.filter((x) => x.error);
  if (found.length) {
    const held = sizes - found.length;
    const rest = held > 0 ? ` The best known held on the other ${sizesWord(held)}.` : "";
    const links = listN(found.map((n) => `<a data-act="discovery" data-n="${n}">${n}</a>`));
    return { kind: "star", text: `New best-known packing${found.length > 1 ? "s" : ""} for n = ${listN(found)}.${rest}`,
      html: `New best-known packing${found.length > 1 ? "s" : ""} for n = ${links}.${rest}`, short: `n = ${found.join(", ")}` };
  }
  if (r.results.length && errors.length === r.results.length) {
    return { kind: "fail", text: `The code failed on every size: ${lastLine(errors[0].error)}`, short: "code failed" };
  }
  const near = r.results.filter((x) => x.runner_up_gap > 0).sort((a, b) => a.runner_up_gap - b.runner_up_gap)[0];
  let text = near ? `No improvement. The closest other packing came within ${plain(near.runner_up_gap)} of the best known (n = ${near.n}).`
    : `No improvement on any of the ${sizesWord(sizes)}.`;
  if (errors.length) text += ` The code failed on ${errors.length} of ${r.results.length} runs.`;
  return { kind: "none", text };
}
const lastLine = (e) => String(e || "").split("\n").map((s) => s.trim()).filter(Boolean).slice(-1)[0] || "";
const markHTML = (kind) => (kind === "star" ? ICON.star : kind === "fail" ? ICON.fail : `<span class="ring ${kind === "live" ? "spin" : kind === "wait" ? "wait" : ""}"></span>`);

// ---------- packings ----------
function figure(poses, side, marked) {
  let out = `<svg viewBox="-0.05 -0.05 ${side + 0.1} ${side + 0.1}" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="${side}" height="${side}" style="fill:var(--paper);stroke:var(--sq-edge)" stroke-width="1" vector-effect="non-scaling-stroke"/>`;
  poses.forEach(([x, y, a], i) => {
    out += `<rect x="-0.5" y="-0.5" width="1" height="1" transform="translate(${x} ${side - y}) rotate(${(-a * 180) / Math.PI})" style="fill:var(${marked && marked[i] ? "--sq-new" : "--sq"});stroke:var(--sq-edge)" stroke-width="0.75" vector-effect="non-scaling-stroke"/>`;
  });
  return out + "</svg>";
}

// Squares of `after` with no counterpart in `before`, under the best of the 8 symmetries of the square.
function changed(after, sa, before, sb) {
  let best = null;
  for (let k = 0; k < 8; k++) {
    const flags = after.map(([x, y]) => {
      let u = x - sa / 2, v = y - sa / 2;
      if (k & 4) u = -u;
      for (let r = 0; r < (k & 3); r++) [u, v] = [-v, u];
      return !before.some(([p, q]) => (p - u - sb / 2) ** 2 + (q - v - sb / 2) ** 2 < 0.0025);
    });
    const count = flags.filter(Boolean).length;
    if (!best || count < best.count) best = { flags, count };
  }
  return best;
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
  const found = S.discoveries.map((d) => `<button class="item ${S.sel?.type === "discovery" && S.sel.n === d.n ? "on" : ""}" data-act="discovery" data-n="${d.n}">
      <span class="star">★</span><span class="name">n = ${d.n}</span><span class="aside">−${plain(d.improvement)}</span></button>`).join("");
  const dark = (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark")) === "dark";
  $("#side").innerHTML = `<div class="brand">${LOGO} Mosa</div>
    <button class="new" data-act="compose">${ICON.plus} New lab</button>
    <div class="list"><div class="heading">Labs</div>${labs}${found ? `<div class="heading">Discoveries</div>${found}` : ""}</div>
    <div class="side-foot"><button class="icon-btn" data-act="theme" title="${dark ? "Light" : "Dark"} theme">${dark ? ICON.sun : ICON.moon}</button></div>`;
}

// ---------- main: the lab ----------
function renderMain() {
  const el = $("#main");
  if (S.compose) { el.innerHTML = composeView(); return; }
  const m = model(S.lab), l = summary(S.lab);
  if (!m || !m.lab) { el.innerHTML = `<div class="empty">${S.labs.length ? "Loading…" : "No labs yet. Start one with New lab."}</div>`; return; }
  const L = m.lab;
  const parts = [];
  if (L.kind === "apply") parts.push(`rerun of “${esc(idea({ source: L.source }).name)}”`, ...(L.seeds ? [`${seeds(L)} seed${seeds(L) > 1 ? "s" : ""} per size`] : []));
  else parts.push(`${L.chains} researcher${L.chains > 1 ? "s" : ""} × ${L.rounds} round${L.rounds > 1 ? "s" : ""}`,
    `each idea tested on ${sizesWord((L.targets || []).length)}${seeds(L) > 1 ? ` × ${seeds(L)} seeds` : ""}`);
  parts.push(`started ${clock(m.start)}`);
  if (m.done) parts.push(`took ${duration(m.end - m.start)}`);
  else if (l?.running) parts.push("running");
  if (L.brief) parts.push(`<a data-act="brief">brief</a>`);
  const replay = S.replay && S.replay.lab === S.lab
    ? `<div class="replay"><button class="icon-btn" data-act="replay-toggle">${S.replay.playing ? ICON.pause : ICON.play}</button>
        <input type="range" id="scrub" min="${S.replay.start}" max="${S.replay.end}" value="${S.replay.t}"><span class="time">${clock(S.replay.t)}</span>
        <button class="icon-btn" data-act="replay-stop" title="Stop replay">${ICON.close}</button></div>`
    : m.done ? `<button class="text-btn" data-act="replay">${ICON.replay} Replay</button>` : "";
  el.innerHTML = `<div class="lab-head"><div class="head-text"><h1>${esc(labTitle(l || L))}</h1><div class="sub">${parts.join(" · ")}</div></div>${replay}</div>${mapHTML(m)}`;
}

function mapHTML(m) {
  const L = m.lab;
  const rows = [...m.chains.entries()].sort((a, b) => a[0] - b[0]).map(([c, rounds]) => {
    const ideas = [...rounds.values()].sort((a, b) => a.round - b.round).map((r) => {
      const o = outcome(r, m), it = idea(r.strategy);
      const on = S.sel?.type === "idea" && S.sel.lab === S.lab && S.sel.chain === c && S.sel.round === r.round;
      return `<button class="idea ${o.kind} ${on ? "on" : ""}" data-act="idea" data-chain="${c}" data-round="${r.round}">
        <span class="mark">${markHTML(o.kind)}</span>
        <div class="title">${esc(it.name || (o.kind === "wait" ? "Thinking…" : "—"))}</div>
        ${it.field ? `<div class="field">${esc(it.field)}</div>` : ""}
        ${o.kind === "star" ? `<div class="found">★ ${esc(o.short)}</div>` : o.short && o.kind !== "none" ? `<div class="state">${esc(o.short)}</div>` : ""}</button>`;
    }).join("");
    return `<div class="lane"><div class="who">${L.kind === "apply" ? "Strategy" : `Researcher ${c + 1}`}</div><div class="thread">${ideas}</div></div>`;
  }).join("");
  return `<div class="map">${rows}</div>`;
}

// ---------- detail: the selection ----------
function renderDetail() {
  const el = $("#detail");
  const html = S.sel ? (S.sel.type === "idea" ? ideaView() : S.sel.type === "discovery" ? discoveryView() : briefView()) : "";
  el.hidden = !html;
  if (!html) return;
  const top = el.scrollTop, open = [...el.querySelectorAll("details[open] > summary")].map((s) => s.textContent);
  el.innerHTML = `<button class="icon-btn close" data-act="unselect" title="Close (Esc)">${ICON.close}</button>${html}`;
  el.querySelectorAll("details > summary").forEach((s) => { if (open.includes(s.textContent)) s.parentElement.open = true; });
  if (window.hljs) el.querySelectorAll("code.language-python").forEach((c) => window.hljs.highlightElement(c));
  el.scrollTop = top;
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
  const m = model(S.sel.lab), r = m && m.chains.get(S.sel.chain)?.get(S.sel.round);
  if (!r) return "";
  const o = outcome(r, m), it = idea(r.strategy), s = r.strategy || {};
  const kind = { new: "new idea", refine: "refinement", combine: "combination" }[s.decision];
  const who = m.lab.kind === "apply" ? "Strategy" : `Researcher ${r.chain + 1} · round ${r.round}${kind ? ` · ${kind}` : ""}`;
  return `<div class="pane">
    <div class="eyebrow">${who}</div>
    <h2>${esc(it.name || "Thinking…")}</h2>${it.field ? `<div class="from">from ${esc(it.field)}</div>` : ""}
    <div class="outcome">${markHTML(o.kind)}<span>${o.html || esc(o.text)}</span></div>
    ${s.mapping ? `<div class="section"><div class="section-label">Why the researcher expected it to work</div><div class="prose">${esc(s.mapping)}</div></div>` : ""}
    ${s.strategy ? `<div class="section"><div class="section-label">What it does</div><div class="prose">${esc(s.strategy)}</div></div>` : ""}
    ${r.results.length ? `<details><summary>Results on each size</summary>${resultsTable(r, m)}</details>` : ""}
    ${s.code ? `<details><summary>Code</summary><pre class="code"><code class="language-python">${esc(s.code)}</code></pre></details>` : ""}
    ${r.prompt ? `<details><summary>What the researcher was told</summary><pre class="code plain">${esc(r.prompt.prompt)}</pre></details>` : ""}
    ${s.code ? `<div class="section"><button class="btn quiet" data-act="apply">Run on more sizes</button></div>` : ""}
  </div>`;
}

function discoveryView() {
  const d = S.discoveries.find((x) => x.n === S.sel.n);
  if (!d) return "";
  const ref = S.refs[d.n];
  if (!ref) reference(d.n);
  const ready = ref && ref !== "loading";
  const marks = ready ? changed(d.poses, d.side, ref.poses, ref.side) : null;
  const before = S.view === "before" && ready;
  const m = S.books[d.lab]?.model, r = m && m.chains.get(d.chain ?? 0)?.get(d.round ?? 1);  // provenance from the whole notebook, even mid-replay
  const lab = summary(d.lab), it = r ? idea(r.strategy) : idea({ source: m?.lab?.source || lab?.source });
  const by = lab?.kind === "lab" && r ? `<a data-act="idea-in" data-lab="${esc(d.lab)}" data-chain="${d.chain}" data-round="${d.round}">Researcher ${d.chain + 1}, round ${d.round}</a>: ${esc(it.name)}`
    : `A rerun of “${esc(it.name)}” on <a data-act="lab" data-id="${esc(d.lab)}">${esc(labTitle(lab))}</a>`;
  const pct = (100 * d.improvement / d.reference_side).toPrecision(2);
  const info = ready ? ref.info : null;
  return `<div class="pane">
    <div class="eyebrow">Discovery</div>
    <h2>${d.n} squares in a square</h2>
    <div class="toggle"><button class="${before ? "" : "on"}" data-act="view" data-v="after">Mosa</button><button class="${before ? "on" : ""}" data-act="view" data-v="before">Best known before</button></div>
    <div class="figure">${before ? figure(ref.poses, ref.side) : figure(d.poses, d.side, marks?.flags)}</div>
    <div class="numbers">Side <span class="mono">${side6(d.side)}</span>, ${plain(d.improvement)} smaller than the best known <span class="mono">${side6(d.reference_side)}</span> (${pct}%).${marks && !before ? ` ${marks.count} squares are arranged differently (highlighted).` : ""}</div>
    <div class="section"><div class="verified">${ICON.check} Verified</div>
      <ul class="checks"><li>No overlap at zero tolerance</li><li>Confirmed at 80 and 160 digits of precision</li><li>Every gap between squares, and to the walls, is at least ${Number(d.min_pair_clearance).toExponential(0)}</li></ul></div>
    <div class="section"><div class="section-label">Found by</div>${by}</div>
    ${info?.notes ? `<details><summary>Previous record</summary><div class="prose" style="color:var(--muted)">${info.official ? `Catalogue value ${side6(info.official)}. ` : ""}${esc(info.notes)}</div></details>` : ""}
    <div class="section" style="display:flex;gap:8px"><button class="btn" data-act="svg">${ICON.download} square-${d.n}.svg</button><button class="btn quiet" data-act="json">JSON</button></div>
  </div>`;
}

function briefView() {
  const m = model(S.sel.lab);
  return `<div class="pane"><div class="eyebrow">Brief</div><h2>What the researchers were told about these sizes</h2>
    <div class="section"><pre class="code plain">${esc(m?.lab?.brief || "")}</pre></div></div>`;
}

// ---------- new lab ----------
function composeView() {
  const c = S.compose;
  const apply = c.kind === "apply";
  const stepper = (key, label) => `<div class="field-row"><label>${label}</label><div class="stepper"><button data-act="step" data-k="${key}" data-d="-1">−</button><span>${c[key]}</span><button data-act="step" data-k="${key}" data-d="1">+</button></div></div>`;
  return `<div class="compose">
    <h1>${apply ? `Run “${esc(c.name)}” on more sizes` : "New lab"}</h1>
    <div class="sub">${apply ? "The same strategy, without a researcher, on the sizes and seeds you choose." : "Researchers write search strategies for these sizes, test them, and learn from the results."}</div>
    <div class="field-row"><label for="f-sizes">Sizes</label><input id="f-sizes" value="${esc(c.sizes)}"><div class="hint">For example 67, or 101–110, 122–132.</div></div>
    ${apply ? "" : `<div class="pair">${stepper("chains", "Researchers")}${stepper("rounds", "Rounds")}</div>
      <div class="field-row"><label for="f-brief">Brief <span style="color:var(--muted);font-weight:400">(optional)</span></label><textarea id="f-brief" placeholder="Anything the researchers should know about these sizes.">${esc(c.brief)}</textarea></div>`}
    <details ${apply ? "open" : ""}><summary>More options</summary>
      <div class="field-row" style="margin-top:12px"><label for="f-seeds">Seeds per size</label><input id="f-seeds" value="${esc(c.seeds)}" style="width:160px"><div class="hint">Each seed is an independent run. One run is a noisy sample.</div></div>
      <div class="field-row"><label>Compute</label><div class="choice"><label><input type="radio" name="f-compute" value="modal" ${c.backend === "modal" ? "checked" : ""}> Modal</label><label><input type="radio" name="f-compute" value="local" ${c.backend === "local" ? "checked" : ""}> This machine</label></div></div>
      <div class="field-row"><label for="f-refs">Reference sizes</label><input id="f-refs" value="${esc(c.refs)}" style="width:160px"><div class="hint">Best packings of other sizes that the strategies may borrow from.</div></div>
    </details>
    <div style="margin-top:22px"><button class="btn" data-act="start">${apply ? "Run" : "Start lab"}</button><span class="note" id="f-note"></span></div>
  </div>`;
}

const parseSizes = (text) => String(text).split(/[\s,]+/).filter(Boolean).flatMap((p) => {
  const m = p.match(/^(\d+)[-–](\d+)$/);
  return m ? Array.from({ length: +m[2] - +m[1] + 1 }, (_, i) => +m[1] + i) : /^\d+$/.test(p) ? [+p] : [];
});

async function start() {
  const c = S.compose, note = $("#f-note");
  const spec = { kind: c.kind, targets: parseSizes($("#f-sizes").value), seeds: parseSizes($("#f-seeds").value),
    backend: document.querySelector("input[name=f-compute]:checked")?.value || "modal", references: parseSizes($("#f-refs").value) };
  if (c.kind === "lab") Object.assign(spec, { chains: c.chains, rounds: c.rounds, brief: $("#f-brief").value });
  else Object.assign(spec, { code: c.code, name: c.name });
  if (!spec.targets.length) { note.textContent = "Give at least one size."; return; }
  note.textContent = "Starting…";
  try {
    const r = await api("/api/launch", spec);
    await refresh();
    S.compose = null;
    selectLab(r.id);
  } catch (e) { note.textContent = e.message; }
}

// ---------- status ----------
function renderStatus() {
  if (S.replay) { $("#status").innerHTML = `Replaying ${esc(labTitle(summary(S.replay.lab)))} · ${clock(S.replay.t)}`; return; }
  const live = [];
  for (const l of S.labs.filter((x) => x.running)) {
    const m = S.books[l.id]?.model;
    const r = m && [...m.chains.values()].flatMap((rs) => [...rs.values()]).find((x) => !x.done && !x.error);
    const o = r && outcome(r, m);
    live.push(`${labTitle(l)}${r ? ` · Researcher ${r.chain + 1} ${o.kind === "wait" ? "is writing a strategy" : `is testing “${idea(r.strategy).name}” (${o.short?.replace("testing · ", "")})`}` : ""}`);
  }
  $("#status").innerHTML = live.length ? `<span class="live-dot"></span>${esc(live[0])}${live.length > 1 ? ` · and ${live.length - 1} more` : ""}` : "No labs running";
}

function render() { renderSide(); renderMain(); renderDetail(); renderStatus(); }

// ---------- navigation ----------
function selectLab(id) {
  S.lab = id; S.compose = null;
  if (S.sel && S.sel.type !== "discovery") S.sel = null;
  if (!S.books[id]) loadBook(id).then(render);
  render();
}
function selectIdea(lab, chain, round) {
  if (S.lab !== lab) { S.lab = lab; if (!S.books[lab]) loadBook(lab).then(render); }
  S.compose = null;
  S.sel = { type: "idea", lab, chain, round };
  render();
}
function move(dx, dy) {
  if (S.sel?.type !== "idea") return;
  const m = model(S.lab);
  const chains = [...m.chains.keys()].sort((a, b) => a - b);
  const ci = chains.indexOf(S.sel.chain) + dy;
  if (ci < 0 || ci >= chains.length) return;
  const rounds = m.chains.get(chains[ci]);
  const round = Math.max(1, Math.min(Math.max(...rounds.keys()), S.sel.round + dx));
  if (rounds.has(round)) selectIdea(S.lab, chains[ci], round);
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
    renderMain(); renderDetail(); renderStatus();
  }, 100);
  render();
}

document.addEventListener("click", (ev) => {
  const el = ev.target.closest("[data-act]");
  if (!el) return;
  const d = el.dataset;
  switch (d.act) {
    case "lab": selectLab(d.id); break;
    case "idea": selectIdea(S.lab, +d.chain, +d.round); break;
    case "idea-in": selectIdea(d.lab, +d.chain, +d.round); break;
    case "discovery": {
      const disc = S.discoveries.find((x) => x.n === +d.n);
      S.sel = { type: "discovery", n: +d.n }; S.view = "after"; S.compose = null;
      if (disc && S.lab !== disc.lab) { S.lab = disc.lab; if (!S.books[disc.lab]) loadBook(disc.lab).then(render); }
      render();
      break;
    }
    case "brief": S.sel = { type: "brief", lab: S.lab }; render(); break;
    case "unselect": S.sel = null; render(); break;
    case "view": S.view = d.v; renderDetail(); break;
    case "compose": S.compose = { kind: "lab", sizes: "101–110, 122–132", chains: 4, rounds: 3, brief: "", seeds: "0", backend: "modal", refs: "" }; S.sel = null; render(); break;
    case "apply": {
      const r = model(S.sel.lab).chains.get(S.sel.chain).get(S.sel.round);
      S.compose = { kind: "apply", name: idea(r.strategy).name, code: r.strategy.code, sizes: "", seeds: "1 2 3 4", backend: "modal", refs: "" };
      S.sel = null; render(); $("#f-sizes")?.focus();
      break;
    }
    case "step": { const c = S.compose; c[d.k] = Math.max(1, Math.min(d.k === "chains" ? 8 : 10, c[d.k] + +d.d)); c.sizes = $("#f-sizes").value; c.brief = $("#f-brief")?.value ?? c.brief; renderMain(); break; }
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
    case "svg": { const x = S.discoveries.find((y) => y.n === S.sel.n); download(`square-${x.n}.svg`, catalogueSVG(x.poses, x.side, x.n), "image/svg+xml"); break; }
    case "json": { const x = S.discoveries.find((y) => y.n === S.sel.n); download(`n${x.n}.json`, JSON.stringify({ n: x.n, side: x.side, previous_best_known: x.reference_side, squares: x.poses.map(([a, b, t]) => ({ x: a, y: b, angle_radians: t })) }, null, 1), "application/json"); break; }
  }
});
document.addEventListener("input", (ev) => {
  if (ev.target.id !== "scrub" || !S.replay) return;  // redraw the map only, so the slider keeps the drag
  S.replay.t = +ev.target.value; S.replay.playing = false; clearInterval(timer);
  $(".map").outerHTML = mapHTML(model(S.lab));
  $(".replay .time").textContent = clock(S.replay.t);
  $(".replay .icon-btn").innerHTML = ICON.play;
  renderDetail(); renderStatus();
});
document.addEventListener("keydown", (ev) => {
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
