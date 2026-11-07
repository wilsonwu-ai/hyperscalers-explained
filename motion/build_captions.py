#!/usr/bin/env python3
"""WebVTT from the approved script text, timed by aligning script words to the local Whisper word timings."""
import json, os, re, difflib, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
S = json.load(open(os.path.join(here, 'script.json')))
T = {x['id']: x for x in json.load(open(os.path.join(here, 'build/timing.json')))['scenes']}
W = json.load(open(os.path.join(here, 'build/whisper.json')))
# reuse the normaliser from the Whisper check without loading a model
src = open(os.path.join(here, 'whisper_check.py')).read()
ns = {}
ns = {'re': re}; exec(src[src.index('ONES ='):src.index('res = {}')], ns)
norm = ns['norm']

def toks_with_owner(words):
    toks, own = [], []
    for i, w in enumerate(words):
        for t in norm(w):
            toks.append(t); own.append(i)
    return toks, own

def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return '%02d:%02d:%06.3f' % (h, m, s)

def chunks(words):
    """split into sentence-sized caption lines of at most ~64 characters"""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if re.search(r'[.?!]$', w):
            out.append(cur); cur = []
    if cur: out.append(cur)
    res = []
    for c in out:
        text = ' '.join(words[i] for i in c)
        if len(text) <= 64: res.append(c); continue
        # split at the comma nearest the middle, else at the middle word
        best, bi = None, None
        for j, i in enumerate(c[:-1]):
            if words[i].endswith(','):
                d = abs(len(' '.join(words[k] for k in c[:j + 1])) - len(text) / 2)
                if best is None or d < best: best, bi = d, j
        if bi is None: bi = len(c) // 2 - 1
        res += [c[:bi + 1], c[bi + 1:]]
    return res

cues = []
for sc in S['scenes']:
    words = sc['caption'].split()
    ct, co = toks_with_owner(words)
    wh = W[sc['id']]['words']
    ht, ho = toks_with_owner([w[0] for w in wh])
    sm = difflib.SequenceMatcher(a=ct, b=ht, autojunk=False)
    start = [None] * len(words); end = [None] * len(words)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            ci, hi = co[blk.a + k], ho[blk.b + k]
            if start[ci] is None: start[ci] = wh[hi][1]
            end[ci] = wh[hi][2]
    # fill gaps by interpolation
    last_t = 0.0
    for i in range(len(words)):
        if start[i] is None:
            j = i
            while j < len(words) and start[j] is None: j += 1
            nxt = start[j] if j < len(words) else wh[-1][2]
            start[i] = last_t; end[i] = last_t = (last_t + (nxt - last_t) / (j - i + 1)) if False else nxt
        last_t = end[i]
    base = T[sc['id']]['audio_start']
    for c in chunks(words):
        cues.append([base + start[c[0]], base + end[c[-1]] + 0.12, ' '.join(words[i] for i in c)])
for k in range(len(cues) - 1):   # clamp each end to the next start
    if cues[k][1] > cues[k + 1][0] - 0.02: cues[k][1] = cues[k + 1][0] - 0.02
    if cues[k][1] < cues[k][0] + 0.4: cues[k][1] = min(cues[k][0] + 0.4, cues[k + 1][0] - 0.02)
out = 'WEBVTT\n\n' + '\n'.join('%d\n%s --> %s\n%s\n' % (i + 1, fmt(a), fmt(b), t) for i, (a, b, t) in enumerate(cues))
assert '\u2014' not in out and '\u2013' not in out
dest = os.path.join(here, '..', 'docs', 'media', 'hyperscalers.vtt')
open(dest, 'w').write(out)
print(out)
