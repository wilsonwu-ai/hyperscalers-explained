#!/usr/bin/env python3
"""Cut each scene out of the FINAL mp4's audio track, transcribe locally with Whisper, and score vs the spoken script."""
import json, os, re, subprocess, sys, difflib, whisper
here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(here, 'script.json')))
T = {x['id']: x for x in json.load(open(os.path.join(here, 'build/timing.json')))['scenes']}
src = open(os.path.join(here, 'whisper_check.py')).read()
ns = {'re': re}; exec(src[src.index('ONES ='):src.index('res = {}')], ns); norm = ns['norm']
model = whisper.load_model(sys.argv[1])
mp4 = os.path.join(here, '..', 'docs', 'media', 'hyperscalers.mp4')
os.makedirs(os.path.join(here, 'build/final'), exist_ok=True)
tot_ref = tot_ok = 0
for sc in S['scenes']:
    t = T[sc['id']]; out = os.path.join(here, 'build/final', sc['id'] + '.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t['start']), '-t', str(t['dur']), '-i', mp4, '-vn', '-ac', '1', '-ar', '16000', out], check=True)
    r = model.transcribe(out, language='en', condition_on_previous_text=False, initial_prompt='NVIDIA, GPU, gigawatt, backlog, hyperscalers.')
    ref, hyp = norm(sc['vo']), norm(r['text'])
    m = sum(b.size for b in difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False).get_matching_blocks())
    tot_ref += len(ref); tot_ok += m
    print(sc['id'], round(100 * m / len(ref), 1), '|', r['text'].strip())
print('overall', round(100 * tot_ok / tot_ref, 1))
