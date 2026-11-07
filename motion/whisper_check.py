#!/usr/bin/env python3
"""Local Whisper (openai-whisper, medium) over each trimmed scene clip; word match vs the spoken script text."""
import json, os, re, sys, difflib, whisper
here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(here, 'script.json')))
model = whisper.load_model(sys.argv[1] if len(sys.argv) > 1 else 'medium')

ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = {2:'twenty',3:'thirty',4:'forty',5:'fifty',6:'sixty',7:'seventy',8:'eighty',9:'ninety'}
def int_words(n):
    if n < 20: return [ONES[n]]
    if n < 100: return [TENS[n//10]] + ([ONES[n%10]] if n%10 else [])
    if n < 1000:
        return [ONES[n//100], 'hundred'] + (int_words(n%100) if n%100 else [])
    return [str(n)]
def num_tokens(tok):
    m = re.fullmatch(r'(\d+)(?:\.(\d+))?', tok)
    if not m: return [tok]
    out = int_words(int(m.group(1)))
    if m.group(2): out += ['point'] + [ONES[int(c)] for c in m.group(2)]
    return out
def norm(text):
    text = text.lower().replace('%', ' percent ').replace('$', ' ')
    text = re.sub(r'(\d),(\d)', r'\1\2', text)
    text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1 to \2', text)
    text = re.sub(r'[^a-z0-9. ]', ' ', text.replace('-', ' '))
    text = re.sub(r'\.(?!\d)', ' ', text)
    toks = []
    for t in text.split():
        t = t.strip('.')
        if t: toks += num_tokens(t)
    # canonical equivalences
    toks = [x for x in toks if x != 'dollars']
    s = ' '.join(toks).replace('chip makers', 'chipmakers'); toks = s.split()
    out = []
    for t in toks:
        t = {'gw': 'gigawatt', 'gigawatts': 'gigawatt'}.get(t, t)
        out.append(t)
    return out

res = {}
for sc in S['scenes']:
    p = os.path.join(here, 'build/audio/trim', sc['id'] + '.wav')
    r = model.transcribe(p, language='en', word_timestamps=True, condition_on_previous_text=False,
                         initial_prompt='NVIDIA, GPU, gigawatt, backlog, hyperscalers.')
    words = [(w['word'].strip(), w['start'], w['end']) for seg in r['segments'] for w in seg['words']]
    hyp = norm(r['text']); ref = norm(sc['vo'])
    sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    pct = 100.0 * matched / max(1, len(ref))
    res[sc['id']] = {'match_pct': round(pct, 1), 'whisper': r['text'].strip(), 'words': words,
                     'ref_tokens': len(ref), 'hyp_tokens': len(hyp)}
    print(sc['id'], round(pct, 1), '|', r['text'].strip())
json.dump(res, open(os.path.join(here, 'build/whisper.json'), 'w'), indent=1)
