"""Memory sections for the code regime (priority(item, bins) on 5,000-item Weibull streams).

Same three arms and the same token budget as falsify/memory.py; only the evidence differs:

prose       for earlier proposals that were not promoted (newest first): name, stated idea,
            fixed-suite result against the incumbent of the time and against best-fit,
            short-stream loss counts, and one sentence on how the policy first departed
            from the reference on its shrunk failing streams. No concrete input.
executable  for the same proposals: name, idea, fixed-suite result, and up to two shrunk
            short streams (at most 30 items, packed from empty bins) on which the policy
            used more bins than the reference, with both packings and the first different
            decision.

If the incumbent is not best-fit, its own evidence comes first: streams where it uses more
bins than the incumbent it replaced and than best-fit. Proposals that failed to run or were
rejected by the integrity gate get the same one-line note in both memory arms.
"""
import statistics

from .memory import EMPTY

PROSE_HEADING = '## Earlier proposals that were not promoted (newest first)\n'
EXEC_HEADING = ('## Counterexamples from earlier proposals (newest first)\n'
                'Each input is a short stream from the same item distribution, packed from empty bins '
                '(as many bins as items), on which that policy used more bins than the named reference. '
                'It was shrunk by deleting items while the policy still lost. Bins are listed with their '
                'items in arrival order.\n')
IDEA_CHARS = 200
# Statuses that appear in memory: evaluated, rejected by the gate, or failed at run time.
# Replies that could not be parsed (or API failures) carry no proposal and are left out.
SHOWN = ('ok', 'static', 'error')


def _label(rec):
    return f'proposal {rec["call"] + 1} "{rec["name"]}"'


def _idea(rec):
    return ' '.join(rec.get('hypothesis', '').split())[:IDEA_CHARS]


def _ref_name(rec, which):
    if which == 'best_fit' or rec['incumbent_before'] == 'best_fit':
        return 'best-fit'
    return f'the incumbent of the time ({rec["incumbent_before"]})'


def _departure(cx):
    d = cx['divergence']
    if d['candidate_new']:
        return 'new'
    if d['reference_new']:
        return 'reused'
    mine, ref = d['candidate_free'] - d['item'], d['reference_free'] - d['item']
    return 'roomier' if mine > ref else 'tighter'


def mechanism_sentence(counterexamples, ref):
    divs = [cx for cx in counterexamples if cx.get('divergence')]
    if not divs:
        return ''
    kinds = [_departure(cx) for cx in divs]
    words = {'new': 'opened a new bin although an open bin had room',
             'reused': 'used an open bin where the reference opened a new one',
             'roomier': 'chose a roomier open bin', 'tighter': 'chose a tighter open bin'}
    parts = [f'{words[k]} {kinds.count(k)} time{"s" if kinds.count(k) != 1 else ""}'
             for k in ('new', 'roomier', 'tighter', 'reused') if kinds.count(k)]
    lengths = statistics.median(len(cx['items']) for cx in divs)
    return (f' On {len(divs)} shrunk losing stream{"s" if len(divs) > 1 else ""} (median {lengths:g} items), '
            f'its first departure from {ref} ' + ', '.join(parts) + '.')


def _fixed_clause(rec):
    f = rec['fixed']
    vs_inc = f['mean_vs_incumbent']
    text = f'Fixed suite: {vs_inc:+.1f} bins per instance versus {_ref_name(rec, "incumbent")}'
    if rec['incumbent_before'] != 'best_fit':
        text += f' ({f["mean_vs_best_fit"]:+.1f} versus best-fit)'
    return text + f'; more bins on {f["losses_vs_incumbent"]} of {f["instances"]} instances.'


def _short_clause(rec, which, n_windows, window):
    m = rec['mining'][which]
    if m.get('stopped', '') and str(m['stopped']).startswith('program failed'):
        return ' On short streams it failed to run.'
    return (f' On {n_windows} short streams of {window} items packed from empty bins it used more bins than '
            f'{_ref_name(rec, which)} on {m["losses"]} and fewer on {m["wins"]}.')


def short_error(text):
    """Last line of a traceback (exception type and message), without file paths."""
    lines = [l.strip() for l in str(text or 'unknown error').splitlines() if l.strip()]
    return ' '.join(lines[-1].split())[:160] if lines else 'unknown error'


def _n_bins(n):
    return f'{n} bin{"s" if n != 1 else ""}'


def error_line(rec):
    if rec['status'] == 'static':
        why = 'was rejected by the integrity gate before running'
    else:
        why = f'could not be evaluated: {short_error(rec.get("error"))}'
    return f'- {_label(rec).capitalize()} {why}.\n'


def prose_entry(rec, n_windows, window):
    if rec['status'] != 'ok':
        return error_line(rec)
    m = rec['mining']['incumbent']
    tie = ' It packed every fixed instance exactly like the incumbent.' if rec.get('no_op') else ''
    return (f'- {_label(rec).capitalize()}, not promoted. Idea: {_idea(rec)} {_fixed_clause(rec)}'
            f'{_short_clause(rec, "incumbent", n_windows, window)}{tie}'
            f'{mechanism_sentence(m["counterexamples"], _ref_name(rec, "incumbent"))}\n')


def prose_incumbent_entry(rec, n_windows, window):
    f = rec['fixed']
    text = (f'- The current incumbent ({_label(rec)}) uses {f["mean_vs_best_fit"]:+.1f} bins per instance versus '
            f'best-fit on the fixed suite')
    if rec['incumbent_before'] != 'best_fit':
        text += f' and {f["mean_vs_incumbent"]:+.1f} versus the incumbent it replaced ({rec["incumbent_before"]})'
    text += '.'
    for which in (['incumbent', 'best_fit'] if rec['incumbent_before'] != 'best_fit' else ['best_fit']):
        m = rec['mining'][which]
        text += _short_clause(rec, which, n_windows, window)
        text += mechanism_sentence(m['counterexamples'], _ref_name(rec, which))
    return text + '\n'


def _bins(packing):
    return ' '.join('[' + ' '.join(map(str, b)) + ']' for b in packing)


def counterexample_lines(cx, letter, ref):
    lines = [f'  Input {letter} ({len(cx["items"])} items): {cx["items"]}',
             f'    policy uses {_n_bins(cx["candidate_bins"])}: {_bins(cx["candidate_packing"])}',
             f'    {ref} uses {_n_bins(cx["reference_bins"])}: {_bins(cx["reference_packing"])}']
    d = cx.get('divergence')
    if d:
        if d['candidate_new']:
            mine = 'the policy opened a new bin'
        else:
            mine = f'the policy chose a bin with {d["candidate_free"]} free, leaving {d["candidate_free"] - d["item"]}'
        if d['reference_new']:
            theirs = f'{ref} opened a new bin'
        else:
            theirs = f'{ref} chose a bin with {d["reference_free"]} free, leaving {d["reference_free"] - d["item"]}'
        lines.append(f'    first different decision: item {d["index"] + 1} (size {d["item"]}): {mine}; {theirs}.')
    return '\n'.join(lines) + '\n'


def _cx_block(rec, which, letters):
    ref = _ref_name(rec, which)
    return ''.join(counterexample_lines(cx, next(letters), ref) for cx in rec['mining'][which]['counterexamples'])


def exec_entry(rec):
    if rec['status'] != 'ok':
        return error_line(rec), 0
    cxs = rec['mining']['incumbent']['counterexamples']
    if not cxs:
        return None, 0
    head = f'- {_label(rec).capitalize()}, not promoted. Idea: {_idea(rec)} {_fixed_clause(rec)}\n'
    return head + _cx_block(rec, 'incumbent', iter('ABCDEFGH')), len(cxs)


def exec_incumbent_entry(rec):
    whichs = ['incumbent', 'best_fit'] if rec['incumbent_before'] != 'best_fit' else ['best_fit']
    n = sum(len(rec['mining'][w]['counterexamples']) for w in whichs)
    if not n:
        return None, 0
    f = rec['fixed']
    head = f'- Current incumbent ({_label(rec)}); fixed suite {f["mean_vs_best_fit"]:+.1f} bins per instance versus best-fit.\n'
    letters = iter('ABCDEFGH')
    return head + ''.join(_cx_block(rec, w, letters) for w in whichs), n


def failed(history):
    return [r for r in reversed(history) if not r.get('promoted')]


def build_entries(arm, history, incumbent_rec, n_windows, window):
    entries = []
    if arm == 'prose':
        if incumbent_rec is not None:
            entries.append((prose_incumbent_entry(incumbent_rec, n_windows, window), 0))
        entries += [(prose_entry(r, n_windows, window), 0) for r in failed(history) if r['status'] in SHOWN]
    elif arm == 'executable':
        if incumbent_rec is not None:
            text, n = exec_incumbent_entry(incumbent_rec)
            if text:
                entries.append((text, n))
        for r in failed(history):
            if r['status'] not in SHOWN:
                continue
            text, n = exec_entry(r)
            if text:
                entries.append((text, n))
    elif arm != 'none':
        raise ValueError(arm)
    return entries


def memory_section(arm, history, incumbent_rec, fitter, n_windows, window, max_counterexamples, tag):
    if arm == 'none':
        return {'text': '', 'tokens': 0, 'tokens_exact': True, 'entries': 0, 'counterexamples': 0, 'candidates': 0}
    entries = build_entries(arm, history, incumbent_rec, n_windows, window)
    heading = PROSE_HEADING if arm == 'prose' else EXEC_HEADING
    return fitter.fit(arm, heading, entries, max_counterexamples, tag)


__all__ = ['memory_section', 'build_entries', 'EMPTY']
