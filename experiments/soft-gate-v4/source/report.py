"""Generate a standalone interactive experiment report, with no server or dependencies."""
import html
import json
import statistics
from pathlib import Path
from .core import BEST_FIT, TRAIN_FAMILIES, SHIFT_FAMILIES, pack, read_json, suite

def main():
    root=Path('experiments')
    summaries={n:read_json(root/n/'summary.json') for n in ['local-v1','local-v2','local-firstfit']}
    pilot=read_json(root/'codex-pilot-v1/results.json')
    revision=read_json(root/'codex-pilot-v2/results.json')
    audit=read_json(root/'codex-pilot-v2/audit.json')
    examples=[]
    repaired=next(r for r in revision['results'] if r['name']=='tight_or_roomy_moderate')
    for c in pilot['results']:
        for example in c['counterexamples']:
            examples.append({'name':c['name'],'hypothesis':c['hypothesis'],**example,
                'revised_bins':pack(example['items'],repaired['weights']),
                'revised_assignments':pack(example['items'],repaired['weights'],True)[1]})
    examples.sort(key=lambda x:len(x['items']))
    curves={}
    for arm in ['random_replay','counterexample_replay','counterexample_tail']:
        seed_curves=[]
        for seed in range(50):
            r=read_json(root/'local-v2'/f'{arm}-{seed}.json')
            cases=suite(10000+seed,24)
            refs=[pack(x['items']) for x in cases]
            seed_curves.append([statistics.mean(pack(x['items'],h['weights'])-b for x,b in zip(cases,refs))
                                for h in r['history'][::20]])
        curves[arm]=[statistics.mean(v[i] for v in seed_curves) for i in range(len(seed_curves[0]))]
    firstfit_cases=read_json(root/'local-firstfit/audit_cases.json')
    firstfit_gap=statistics.mean(pack(x['items'],[0.]*12)-pack(x['items']) for x in firstfit_cases)
    data={'summaries':summaries,'examples':examples,'curves':curves,'pilot_audit':audit,'firstfit_initial_excess':firstfit_gap}
    payload=json.dumps(data).replace('<','\\u003c')
    page=PAGE.replace('__DATA__',payload)
    (root/'report.html').write_text(page)
    lines=['# Falsify: initial experiments','',
        'Counterexample replay reduced harmful drift in a bounded online bin-packing search. It did not produce an overall improvement over best-fit. This is a mechanistic evolutionary-search result; it does not establish an LLM memory benefit.','',
        '## Main follow-up: 50 paired seeds, 500 generations','',
        '| Arm | Mean excess bins over best-fit | Search executions per seed |',
        '|---|---:|---:|']
    for a in summaries['local-v2']['arms']:lines.append(f'| {a["arm"]} | {a["mean_excess_bins"]:.6f} | {a["executions_per_seed"]:,} |')
    lines+=['','Lower is better; zero matches best-fit on average. Each test instance contains 80 items. Each arm uses 96,000 packing executions (7,680,000 item steps) per seed, plus 32 reference initialization executions. Final audit uses 800 shared instances (100 per family) and is excluded from search cost.','']
    for c in summaries['local-v2']['paired_comparisons']:
        lo,hi=c['bootstrap_95_interval']
        lines.append(f'- {c["arm_minus_random"]} minus random: {c["mean"]:.6f} bins; paired seed bootstrap 95% interval [{lo:.6f}, {hi:.6f}].')
    lines+=['','Intervals quantify variation across search seeds, conditional on this shared audit suite. They do not capture uncertainty over all possible test distributions. The effect is small in absolute packing efficiency. V2 was designed after inspecting V1, and used a fresh audit seed. The follow-up remains exploratory.','',
        '## Codex-guided experiment','',
        'Codex proposed seven hypotheses, inspected measured failures, and proposed six revisions plus a best-fit control. The reserve-quarter heuristic uses 3 bins for [63,44,32,56], while best-fit uses 2. The revised moderate tight-or-roomy heuristic fixes this case.','',
        'Its exploratory selection result was one win and no losses on 1,000 cases. The independent 10,000-case audit found 3 wins, 14 losses, and 9,983 ties: mean excess 0.0011 bins. This rejects a broad improvement claim despite the attractive pilot result.','',
        '## Recovery from first-fit','',
        f'The initial first-fit policy averaged {firstfit_gap:.6f} excess bins over best-fit on its audit suite. After 200 generations / 20 paired seeds, final excess was '+', '.join(f'{a["arm"]}: {a["mean_excess_bins"]:.6f}' for a in summaries['local-firstfit']['arms'])+'. All arms improved the weak starting policy; none beat best-fit overall.','',
        '## Limitations and next experiment','',
        '- The candidate language is 12 weighted features, not arbitrary algorithm code. Its expressive power and best-fit warm start constrain discovery.',
        '- Counterexamples are prioritized by the largest historical observed regression, so archive relevance can become stale.',
        '- Changing the replay distribution is part of the treatment; this does not isolate explanatory memory in LLM prompts.',
        '- Audit instances are untouched during each named search but generated in the same researcher-controlled process; this is not a hardened adversarial sandbox.',
        '- Test cases are synthetic, fixed-length, one-dimensional integer packing tasks. External benchmarks and variable lengths remain untested.',
        '- Separate the search archive from a validation gate: candidates should demonstrate benefit on a fixed suite and pass archived regressions before promotion. Then compare no memory, prose memory, and executable counterexample memory with the same model and token budget.',
        '', '## Reproduction','', 'See README.md and PROTOCOL-v2.md. Raw traces are gzip-compressed JSON; summaries and independent audits are plain JSON. Source snapshots preserve the experiment implementations. Open report.html for the packing demonstration.','']
    (root/'RESULTS.md').write_text('\n'.join(lines))
    print('Generated experiments/report.html and experiments/RESULTS.md')

PAGE='''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Falsify · Counterexamples as research evidence</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f5f1;color:#182a30;font:16px/1.6 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:42px 24px}h1{font-size:44px;line-height:1.15;margin:12px 0}h2{font-size:24px;margin-top:34px}.eyebrow{color:#287b6a;font-weight:750;letter-spacing:.1em;font-size:12px}p{max-width:850px}.notice{border-left:4px solid #b07526;background:#fff4df;padding:16px 20px}.card{background:white;border:1px solid #d8dfdc;border-radius:12px;padding:24px;margin:20px 0}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:10px 8px;border-bottom:1px solid #e1e6e3}th{font-size:13px;color:#53706b}select,button{font:inherit;padding:8px 12px;border:1px solid #ccd5d1;background:#fff;border-radius:6px}.bins{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.bin{height:38px;display:flex;background:#edf1ee;margin:8px 0;border:1px solid #d8dfdc}.item{display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;font-weight:600;border-right:2px solid white;color:white}.caption{font-size:13px;color:#536863}.pass{color:#177864}.fail{color:#a95132}canvas{width:100%;height:230px}.foot{margin-top:40px;font-size:13px;color:#536863}code{font-size:13px}ul{padding-left:24px}@media(max-width:720px){h1{font-size:32px}.bins{grid-template-columns:1fr}.card{padding:16px}td,th{font-size:12px}}
</style><main>
<div class="eyebrow">SWEDISH SCIENCE MAFIA / RESEARCH PROTOTYPE</div>
<h1>Let failures shape the next discovery.</h1>
<p>Falsify turns an algorithm's regressions into executable counterexamples. A fixed evaluator checks each heuristic, an archive retains difficult inputs, and the search revisits them before accepting new ideas.</p>
<div class="notice"><strong>What the evidence supports:</strong> Counterexample replay reduced harmful drift in this experiment. The evolved policies did not beat best-fit overall. The repeated-run comparison uses stochastic mutations; the Codex-guided pilot is a separate exploratory experiment.</div>
<h2>A concrete failure, and a revision</h2>
<div class="card"><label for="example">Counterexample </label><select id="example"></select><p id="hypothesis"></p><p><strong>Incoming items:</strong> <span id="items"></span></p><label for="step">Reveal items: </label><input id="step" type="range" min="1" value="4096"><span id="stepLabel"></span><div class="bins" id="bins"></div><p class="caption">Capacity = 100. Items arrive in the displayed order. Candidate policies cannot reorder items or inspect future items. A correction on this example is evidence about this case, not a general performance guarantee.</p></div>
<h2>Same evaluation budget, different memory</h2>
<div class="card"><p>50 paired runs, 500 generations, 800 independent audit instances across eight distributions. Lower excess bins is better; zero matches best-fit.</p><table><thead><tr><th>Search arm</th><th>Mean excess bins</th><th>Executions / run</th></tr></thead><tbody id="results"></tbody></table><p id="interval" class="caption"></p><p class="caption">Every arm uses 7.68 million item steps per run, plus identical reference initialization. Bootstrap intervals quantify search-seed variability on the shared audit set. The absolute efficiency difference is small.</p></div>
<h2>Does the tempting pilot improvement survive?</h2>
<div class="card"><p>The revised heuristic won once and lost zero times on 1,000 exploratory cases. On 10,000 independent cases, it won <strong>3</strong> times, lost <strong>14</strong> times, and tied <strong>9,983</strong> times. Its average excess was <strong>0.0011 bins</strong>.</p><p class="fail">The independent audit does not support a broad improvement claim.</p></div>
<h2>Training behaviour over time</h2><div class="card"><canvas id="chart" aria-label="Mean excess bins on the fixed training suite over generations" role="img"></canvas><p class="caption">Mean excess bins on each run's fixed 24-case training suite, sampled every 20 generations. This plot excludes changing replay cases so its y-axis remains comparable over time.</p><p class="caption"><span style="color:#ac6245">■ Random replay</span> · <span style="color:#217866">■ Counterexample replay</span> · <span style="color:#46649c">■ Counterexample + tail risk</span></p></div>
<h2>What to build next</h2><ul><li>Use counterexamples as an explicit promotion gate, while measuring improvements on a fixed suite.</li><li>Expand beyond weighted features to context-aware algorithm proposals.</li><li>Compare no memory, prose summaries, and executable counterexamples with identical model and token budgets.</li><li>Refresh stale failures and track which lesson each counterexample actually supports.</li></ul>
<div class="foot">Recorded experiments: local-v1, local-v2, local-firstfit, codex-pilot-v1, codex-pilot-v2. See RESULTS.md for limitations and README.md for reproducible commands. No sponsor compute or external LLM API was used for these runs.</div>
</main><script id="data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('data').textContent);const names={random_replay:'Random replay',counterexample_replay:'Counterexample replay',counterexample_tail:'Counterexamples + tail risk'};
const example=document.getElementById('example'),step=document.getElementById('step');data.examples.forEach((x,i)=>{let o=document.createElement('option');o.value=i;o.textContent=x.name+' · '+x.items.length+' items';example.append(o)});
function render(){const x=data.examples[+example.value];step.max=x.items.length;step.value=Math.min(+step.value,x.items.length);const n=+step.value;document.getElementById('hypothesis').textContent=x.hypothesis;document.getElementById('items').textContent=x.items.join(', ');document.getElementById('stepLabel').textContent=n+' / '+x.items.length;const area=document.getElementById('bins');area.replaceChildren();const specs=[['Original hypothesis','candidate_assignments'],['Best-fit reference','reference_assignments'],['Codex revision','revised_assignments']];specs.forEach(([name,key])=>{const wrap=document.createElement('div');const title=document.createElement('strong');title.textContent=name;wrap.append(title);const count=Math.max(...x[key].slice(0,n))+1;const caption=document.createElement('div');caption.className='caption';caption.textContent=count+' bins';wrap.append(caption);for(let b=0;b<count;b++){const bin=document.createElement('div');bin.className='bin';for(let i=0;i<n;i++){if(x[key][i]!==b)continue;const item=document.createElement('div');item.className='item';item.style.width=x.items[i]+'%';item.style.background=['#287b6a','#436ba1','#ba7444','#8162a4'][i%4];item.textContent=x.items[i];item.title='Item '+(i+1)+': '+x.items[i];bin.append(item)}wrap.append(bin)}area.append(wrap)})}
example.onchange=()=>{step.value=1;render()};step.oninput=render;render();
for(const a of data.summaries['local-v2'].arms){const tr=document.createElement('tr');for(const v of [names[a.arm],a.mean_excess_bins.toFixed(6),a.executions_per_seed.toLocaleString()]){const td=document.createElement('td');td.textContent=v;tr.append(td)}document.getElementById('results').append(tr)}const ci=data.summaries['local-v2'].paired_comparisons[0];document.getElementById('interval').textContent='Counterexample minus random: '+ci.mean.toFixed(6)+' bins; paired bootstrap 95% interval ['+ci.bootstrap_95_interval.map(v=>v.toFixed(6)).join(', ')+'].';
function draw(){const c=document.getElementById('chart');const dpr=window.devicePixelRatio||1;const w=c.clientWidth,h=230;c.width=w*dpr;c.height=h*dpr;const ctx=c.getContext('2d');ctx.scale(dpr,dpr);const values=Object.values(data.curves).flat();const lo=Math.min(-.01,...values),hi=Math.max(.05,...values);const px=i=>48+i*(w-70)/24,py=v=>190-(v-lo)*160/(hi-lo);ctx.font='11px system-ui';ctx.fillStyle='#536863';ctx.strokeStyle='#dbe1dd';for(let j=0;j<=4;j++){let v=lo+(hi-lo)*j/4;ctx.beginPath();ctx.moveTo(45,py(v));ctx.lineTo(w-15,py(v));ctx.stroke();ctx.fillText(v.toFixed(2),0,py(v)+4)}for(let i=0;i<=24;i+=6)ctx.fillText(i*20,px(i)-8,213);const colors=['#ac6245','#217866','#46649c'];Object.entries(data.curves).forEach(([name,vals],j)=>{ctx.strokeStyle=colors[j];ctx.lineWidth=2;ctx.beginPath();vals.forEach((v,i)=>i?ctx.lineTo(px(i),py(v)):ctx.moveTo(px(i),py(v)));ctx.stroke()})}window.onresize=draw;draw();
</script></html>'''

if __name__=='__main__':main()
