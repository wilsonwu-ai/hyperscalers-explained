#!/usr/bin/env python3
"""Generate per-scene narration with OpenAI gpt-4o-mini-tts (voice marin). Only the script text is sent."""
import json, os, sys, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
s = json.load(open(os.path.join(here, 'script.json')))
only = sys.argv[1:]
key = os.environ['OPENAI_API_KEY']
os.makedirs(os.path.join(here, 'build', 'audio'), exist_ok=True)
for sc in s['scenes']:
    if only and sc['id'] not in only: continue
    body = json.dumps({'model': s['model'], 'voice': s['voice'], 'input': sc['vo'],
                       'instructions': s['instructions'], 'response_format': 'wav', 'speed': s['speed']}).encode()
    req = urllib.request.Request('https://api.openai.com/v1/audio/speech', data=body,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    open(os.path.join(here, 'build', 'audio', sc['id'] + '.wav'), 'wb').write(data)
    print(sc['id'], len(data))
