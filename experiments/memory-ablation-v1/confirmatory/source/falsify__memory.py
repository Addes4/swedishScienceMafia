"""Memory sections for the closed-loop study. Only this text differs between arms.

none        no memory section
prose       verbal summaries of earlier proposals that were not promoted: idea, weights,
            aggregate scores, families where they lost, and a verbal account of how they
            first departed from best-fit on failing inputs (no concrete inputs)
executable  shrunk counterexample inputs from the same proposals, with both packings
            and the first different decision

prose and executable fill the same token budget, newest evidence first. Entries that do
not fit are skipped. The incumbent's own failures come first when it is not best-fit.
"""
import statistics

ARMS = ('none', 'prose', 'executable')
PROSE_HEADING = '## Earlier proposals that were not promoted (newest first)\n'
EXEC_HEADING = ('## Counterexamples from earlier proposals (newest first)\n'
                'Each input is a fresh instance on which that policy used more bins than best-fit, '
                'shrunk by deleting items while the policy still loses. Bins are listed with their '
                'items in arrival order.\n')
EMPTY = 'None yet.\n'


def _label(rec):
    return f'proposal {rec["call"] + 1} "{rec["name"]}"'


def _leftovers(cx):
    d = cx['divergence']
    return d['candidate_free'] - d['item'], d['reference_free'] - d['item']


def mechanism_sentence(counterexamples):
    """Verbal summary of first departures from best-fit; mentions no concrete input."""
    divs = [cx for cx in counterexamples if cx.get('divergence')]
    if not divs:
        return ''
    pairs = [_leftovers(cx) for cx in divs]
    roomier = sum(a > b for a, b in pairs)
    tighter = len(pairs) - roomier
    mine = statistics.median(a for a, _ in pairs)
    best = statistics.median(b for _, b in pairs)
    return (f' On {len(pairs)} shrunk failing input{"s" if len(pairs) > 1 else ""}, its first departure '
            f'from best-fit chose a roomier bin {roomier} time{"s" if roomier != 1 else ""} and a tighter bin '
            f'{tighter} time{"s" if tighter != 1 else ""} (median space left {mine:g} versus {best:g} for '
            f'best-fit), and it later needed an extra bin.')


def _family_clause(fixed):
    worst = sorted(((v, f) for f, v in fixed['by_family'].items() if v > 0), reverse=True)[:2]
    if not worst:
        return ''
    return '; largest excess in ' + ' and '.join(f'{f} ({v:+.3f})' for v, f in worst)


def prose_entry(rec, render, n_fixed, n_probe):
    f = rec['fixed']
    tie = ' It packed every fixed instance exactly like the incumbent.' if rec.get('same_as_incumbent') else ''
    hypothesis = ' '.join(rec['hypothesis'].split())[:240]
    return (f'- {_label(rec).capitalize()}, not promoted. Idea: {hypothesis} Weights: {render(rec["policy"])}. '
            f'Fixed suite: {f["mean_excess"]:+.4f} bins per instance versus best-fit ({f["losses"]} losses, '
            f'{f["wins"]} wins, {f["ties"]} ties of {n_fixed}){_family_clause(f)}. Fresh probes: more bins than '
            f'best-fit on {rec["probe"]["losses"]} of {n_probe}.{tie}{mechanism_sentence(rec["counterexamples"])}\n')


def prose_incumbent_entry(rec, n_fixed, n_probe):
    f = rec['fixed']
    return (f'- The current incumbent ({_label(rec)}) still uses more bins than best-fit on {f["losses"]} of '
            f'{n_fixed} fixed instances{_family_clause(f)}, and on {rec["probe"]["losses"]} of {n_probe} fresh '
            f'probes when it was tested.{mechanism_sentence(rec["counterexamples"])}\n')


def _bins(packing):
    return ' '.join('[' + ' '.join(map(str, b)) + ']' for b in packing)


def counterexample_lines(cx, letter):
    lines = [f'  Input {letter}: items in arrival order {cx["items"]}',
             f'    policy uses {cx["candidate_bins"]} bins: {_bins(cx["candidate_packing"])}',
             f'    best-fit uses {cx["reference_bins"]} bins: {_bins(cx["reference_packing"])}']
    d = cx.get('divergence')
    if d:
        a, b = _leftovers(cx)
        lines.append(f'    first different decision: item {d["index"] + 1} (size {d["item"]}) went into a bin with '
                     f'{d["candidate_free"]} free, leaving {a}; best-fit chose a bin with {d["reference_free"]} free, '
                     f'leaving {b}.')
    return '\n'.join(lines) + '\n'


def exec_entry(rec, render, incumbent=False):
    if incumbent:
        head = f'- Current incumbent ({_label(rec)}); fixed suite {rec["fixed"]["mean_excess"]:+.4f} bins per instance.'
    else:
        head = (f'- {_label(rec).capitalize()}, not promoted; fixed suite {rec["fixed"]["mean_excess"]:+.4f} bins '
                f'per instance versus best-fit.')
    body = ''.join(counterexample_lines(cx, 'ABCDEFGH'[i]) for i, cx in enumerate(rec['counterexamples']))
    return f'{head} Weights: {render(rec["policy"])}.\n{body}'


def failed(history):
    return [r for r in reversed(history) if r['status'] == 'ok' and not r['promoted']]


def build_entries(arm, history, incumbent_rec, render, n_fixed, n_probe, max_counterexamples):
    """Candidate entries in priority order; each is (text, counterexamples_in_entry)."""
    entries = []
    if arm == 'prose':
        if incumbent_rec is not None:
            entries.append((prose_incumbent_entry(incumbent_rec, n_fixed, n_probe), 0))
        entries += [(prose_entry(r, render, n_fixed, n_probe), 0) for r in failed(history)]
    elif arm == 'executable':
        if incumbent_rec is not None and incumbent_rec['counterexamples']:
            entries.append((exec_entry(incumbent_rec, render, incumbent=True), len(incumbent_rec['counterexamples'])))
        entries += [(exec_entry(r, render), len(r['counterexamples'])) for r in failed(history) if r['counterexamples']]
    elif arm != 'none':
        raise ValueError(arm)
    return entries


class TokenFitter:
    """Fills a token budget using exact counts when available (count_tokens), with a
    running characters-per-token estimate per arm to choose candidates cheaply."""

    def __init__(self, count, budget):
        self._count, self.budget = count, budget
        self.ratio = {'prose': 3.6, 'executable': 2.6}
        self.cache = {}

    def count(self, text, tag):
        if text not in self.cache:
            self.cache[text] = self._count(text, tag)
        return self.cache[text]

    def _estimate(self, arm, text):
        return len(text) / self.ratio[arm]

    def fit(self, arm, heading, entries, max_counterexamples, tag):
        """Add entries in priority order while the estimate fits, measure exactly, update
        the estimate and repeat until nothing more fits; drop the lowest-priority entries
        if the exact count is over budget. Output keeps priority order."""
        chosen = set()

        def render(ids):
            return heading + (''.join(entries[i][0] for i in sorted(ids)) or EMPTY)

        def measure(text):
            exact = self.count(text, tag)
            if exact is not None and len(text) > 200:
                self.ratio[arm] = len(text) / exact
            return exact, exact if exact is not None else round(self._estimate(arm, text))

        while True:
            added = False
            for i, (_, ncx) in enumerate(entries):
                shown = sum(entries[j][1] for j in chosen)
                if i in chosen or shown + ncx > max_counterexamples:
                    continue
                if self._estimate(arm, render(chosen | {i})) <= self.budget:
                    chosen.add(i)
                    added = True
            text = render(chosen)
            exact, tokens = measure(text)
            while tokens > self.budget and chosen:
                chosen.remove(max(chosen))
                text = render(chosen)
                exact, tokens = measure(text)
                added = False
            if not added:
                return {'text': text, 'tokens': tokens, 'tokens_exact': exact is not None,
                        'entries': len(chosen), 'counterexamples': sum(entries[i][1] for i in chosen),
                        'candidates': len(entries)}


def memory_section(arm, history, incumbent_rec, render, fitter, n_fixed, n_probe, max_counterexamples, tag):
    if arm == 'none':
        return {'text': '', 'tokens': 0, 'tokens_exact': True, 'entries': 0, 'counterexamples': 0, 'candidates': 0}
    entries = build_entries(arm, history, incumbent_rec, render, n_fixed, n_probe, max_counterexamples)
    heading = PROSE_HEADING if arm == 'prose' else EXEC_HEADING
    return fitter.fit(arm, heading, entries, max_counterexamples, tag)
