#!/usr/bin/env python3
"""Generate the HyperFrames project (index.html + compositions/s1..s7.html) from script.json,
build/timing.json (scene lengths from the audio) and build/whisper.json (word cues).
Every number on screen is from brief/facts.md / model/site_data.json (see NUMBERS below)."""
import json, os, re, random
here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(here, 'script.json')))
T = json.load(open(os.path.join(here, 'build/timing.json')))
W = json.load(open(os.path.join(here, 'build/whisper.json')))
LEAD = 0.35
TIM = {x['id']: x for x in T['scenes']}

# NUMBERS (all from site_data.json, 7 Nov 2026): synergy_ttm 558, +55%; backlog.big4_total_b 2492.7;
# capex_wave.big5_latest 230.4 (latest-quarter segments AMZN 77.3 MSFT 39.4 GOOGL 51.4 META 33.9 ORCL 28.5);
# campus.capex_b 52.6; campus base case revenue 8.24, depreciation 6.71, opex 0.99, power 0.81, interest (neocloud) 3.68;
# chain NVIDIA 66.2%, AWS 38.7%, Google Cloud 36.2%, CoreWeave -1.9%, Nebius -30.2% ("zero or less"); life_it 6 years.

def nrm(w): return re.sub(r'[^a-z0-9]', '', w.lower())
def cue(sid, word, n=1, off=-0.10):
    k = 0
    for (w, s, e) in W[sid]['words']:
        if nrm(w) == nrm(word):
            k += 1
            if k == n: return round(max(0.05, LEAD + s + off), 3)
    raise SystemExit('cue not found %s %s %d' % (sid, word, n))
def cue_end(sid, word, n=1):
    k = 0
    for (w, s, e) in W[sid]['words']:
        if nrm(w) == nrm(word):
            k += 1
            if k == n: return round(LEAD + e, 3)
    raise SystemExit('cue_end not found %s %s' % (sid, word))

CSS = """
@font-face { font-family: 'Fraunces'; src: url('assets/fonts/fraunces-600.woff2') format('woff2'); font-weight: 600; }
#root { position:absolute; inset:0; background:#F6F3EC; font-family:'Inter',sans-serif; color:#10202F; overflow:hidden; }
#root .wrap { position:absolute; inset:0; }
#root .h { font-family:'Fraunces','EB Garamond',serif; font-weight:600; position:absolute; line-height:1.08; letter-spacing:-0.01em; white-space:nowrap; font-variant-numeric:tabular-nums; }
#root .t { position:absolute; font-weight:600; white-space:nowrap; line-height:1.1; font-variant-numeric:tabular-nums; }
#root .box { position:absolute; }
"""
def scene(sid, extra_css, body, js, dur, fin=True, fout=True):
    FIN = f"tl.fromTo('#{sid}-wrap', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: 'power2.out' }}, 0);" if fin else ''
    FOUT = f"tl.to('#{sid}-wrap', {{ opacity: 0, duration: 0.2, ease: 'power2.in' }}, D - 0.2);" if fout else ''
    return f"""<template>
<style>{CSS}{extra_css}</style>
<div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
<div class="wrap" id="{sid}-wrap">
{body}
</div>
</div>
<script>
(function() {{
const tl = gsap.timeline({{ paused: true }});
const D = {dur};
{FIN}
{FOUT}
{js}
window.__timelines['{sid}'] = tl;
}})();
</script>
</template>
"""
def pop(sel, t, dur=0.6, y=24, ease='power2.out'):
    return f"tl.fromTo('{sel}', {{ opacity: 0, y: {y} }}, {{ opacity: 1, y: 0, duration: {dur}, ease: '{ease}' }}, {t});\n"
def fade(sel, t, dur=0.4):
    return f"tl.to('{sel}', {{ opacity: 0, duration: {dur}, ease: 'power2.in' }}, {t});\n"
def count(sel, t, dur, end, fmt):
    return (f"(function(){{ const o = {{ v: 0 }}; const el = document.querySelector('{sel}');\n"
            f"tl.to(o, {{ v: {end}, duration: {dur}, ease: 'power2.out', onUpdate: function(){{ el.textContent = {fmt}; }} }}, {t}); }})();\n")

INK, MUTED, LINE = '#10202F', '#5B6672', '#E2DDD2'
COMPUTE, POWER, BUILD, CHIPS, CASH, COST = '#2F5DA8', '#C98A1B', '#8A7A66', '#6B4FA0', '#1E7F55', '#C2552D'
scenes = {}

# ---------------- S1 hook ----------------
def s1():
    sid = 's1'; d = TIM[sid]['dur']
    pills = [('Stream', 360, 'stream'), ('Search', 500, 'search'), ('Ask an AI', 640, 'ask')]
    css = f"""
#s1-pill {{ }}
#root .pill {{ position:absolute; left:192px; width:460px; height:104px; border-radius:52px; background:#fff; border:3px solid {LINE}; font-size:54px; font-weight:600; line-height:98px; padding-left:92px; box-sizing:border-box; }}
#root .pill i {{ position:absolute; left:34px; top:34px; width:30px; height:30px; border-radius:15px; background:{COMPUTE}; }}
#root .rack {{ position:absolute; width:100px; height:80px; border-radius:8px; background:{COMPUTE}; }}
"""
    body = '<div class="h" id="s1-h" style="left:192px;top:104px;font-size:80px;">You are renting a computer<br>in a giant building.</div>\n'
    for i, (txt, y, _) in enumerate(pills):
        body += f'<div class="pill" id="s1-p{i}" style="top:{y}px;"><i></i>{txt}</div>\n'
    # building
    body += f'<div class="box" id="s1-roof" style="left:1150px;top:390px;width:580px;height:44px;border-radius:10px;background:#6F6150;"></div>\n'
    body += f'<div class="box" id="s1-bld" style="left:1180px;top:434px;width:520px;height:430px;background:{BUILD};"></div>\n'
    body += f'<div class="box" id="s1-door" style="left:1400px;top:790px;width:80px;height:74px;background:#6F6150;border-radius:8px 8px 0 0;"></div>\n'
    rid = 0
    for r in range(3):
        for c in range(4):
            body += f'<div class="rack" id="s1-r{rid}" style="left:{1210 + c*125}px;top:{462 + r*108}px;"></div>\n'; rid += 1
    # packets
    for i, (_, y, _) in enumerate(pills):
        for k in range(3):
            body += f'<div class="box" id="s1-k{i}{k}" style="left:640px;top:{y+40}px;width:24px;height:24px;border-radius:12px;background:{COMPUTE};opacity:0;"></div>\n'
    js = pop('#s1-h', cue(sid, 'renting', 1, -0.3), 0.7)
    # racks off at start
    js += "tl.set('.rack', { opacity: 0.18 }, 0);\n"
    for i, (_, y, w) in enumerate(pills):
        t = cue(sid, w, 1, -0.15)
        js += pop(f'#s1-p{i}', t, 0.5, 30)
        for k in range(3):
            t0 = t + 0.35 + k * 0.75
            dx, dy = 1180 - 640 - 24, 600 - (y + 40) - 12
            js += (f"tl.fromTo('#s1-k{i}{k}', {{ x: 0, y: 0 }}, {{ x: {dx}, y: {dy}, duration: 1.0, ease: 'power1.inOut' }}, {t0:.3f});\n"
                   f"tl.fromTo('#s1-k{i}{k}', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12 }}, {t0:.3f});\n"
                   f"tl.to('#s1-k{i}{k}', {{ opacity: 0, duration: 0.12 }}, {t0+0.88:.3f});\n")
    rnd = random.Random(7)
    order = list(range(12)); rnd.shuffle(order)
    tr = cue(sid, 'renting', 1, 0.0)
    for j, rid in enumerate(order):
        t = tr + 0.12 * j
        js += f"tl.to('#s1-r{rid}', {{ opacity: 1, duration: 0.3, ease: 'power1.out' }}, {t:.3f});\n"
        for b in range(2):
            tb = t + 0.9 + b * 1.1 + rnd.random() * 0.4
            if tb > d - 1.0: continue
            js += f"tl.to('#s1-r{rid}', {{ opacity: 0.55, duration: 0.25, yoyo: true, repeat: 1, ease: 'sine.inOut' }}, {tb:.3f});\n"
    return scene(sid, css, body, js, d, False, True)

# ---------------- S2 the machine ----------------
def s2():
    sid = 's2'; d = TIM[sid]['dur']
    layers = [('Land and power', POWER, '#10202F', 'land'), ('A building', BUILD, '#fff', 'building'),
              ('Chips', CHIPS, '#fff', 'chips'), ('A network', COMPUTE, '#fff', 'network'), ('Software', '#4A78C4', '#fff', 'software')]
    css = f"#root .layer {{ position:absolute; left:192px; width:820px; height:116px; border-radius:14px; font-size:56px; font-weight:600; line-height:116px; padding-left:44px; box-sizing:border-box; }}\n"
    css += f"#root .card {{ position:absolute; left:1160px; top:256px; width:568px; height:644px; border-radius:24px; background:#fff; border:3px solid {LINE}; box-sizing:border-box; }}\n"
    body = '<div class="h" id="s2-h" style="left:192px;top:100px;font-size:76px;">What you are renting</div>\n'
    for k, (txt, bg, fg, w) in enumerate(layers):
        y = 784 - k * 132
        body += f'<div class="layer" id="s2-l{k}" style="top:{y}px;background:{bg};color:{fg};">{txt}</div>\n'
    body += '<div class="card" id="s2-card"></div>\n'
    # dial svg
    cx, cy, r = 1444, 560, 170
    body += f'<svg class="box" id="s2-dial" style="left:1160px;top:256px;" width="568" height="644" viewBox="1160 256 568 644">'
    import math
    body += f'<path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="{LINE}" stroke-width="26" stroke-linecap="round"/>'
    for i in range(11):
        a = math.pi - i * math.pi / 10
        x1, y1 = cx + (r - 30) * math.cos(a), cy - (r - 30) * math.sin(a)
        x2, y2 = cx + (r + 26) * math.cos(a), cy - (r + 26) * math.sin(a)
        body += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{MUTED}" stroke-width="5" stroke-linecap="round"/>'
    body += f'<g id="s2-needle"><line x1="{cx}" y1="{cy}" x2="{cx - r + 22}" y2="{cy}" stroke="{COMPUTE}" stroke-width="12" stroke-linecap="round"/></g>'
    body += f'<circle cx="{cx}" cy="{cy}" r="22" fill="{INK}"/></svg>\n'
    body += f'<div class="t" id="s2-hour" style="left:1200px;top:660px;font-size:56px;">Rented by the hour</div>\n'
    body += f'<div class="t" id="s2-contract" style="left:1200px;top:760px;font-size:56px;color:{COMPUTE};">or by contract</div>\n'
    js = pop('#s2-h', 0.25, 0.6)
    for k, (_, _, _, w) in enumerate(layers):
        js += pop(f'#s2-l{k}', cue(sid, w, 1, -0.12), 0.55, 40)
    th = cue(sid, 'rented', 1, -0.12)
    js += f"tl.fromTo('#s2-card,#s2-dial', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }}, {th});\n"
    js += pop('#s2-hour', cue(sid, 'hour', 1, -0.5), 0.5, 20)
    js += pop('#s2-contract', cue(sid, 'contract', 1, -0.3), 0.5, 20)
    # needle ticks in steps across the rental words (rotation of an SVG group about its own centre)
    js += f"tl.fromTo('#s2-needle', {{ rotation: 0, svgOrigin: '{cx} {cy}' }}, {{ rotation: 168, svgOrigin: '{cx} {cy}', duration: {d - th - 0.7:.2f}, ease: 'steps(14)' }}, {th + 0.3:.3f});\n"
    return scene(sid, css, body, js, d)

# ---------------- S3 money ----------------
def s3():
    sid = 's3'; d = TIM[sid]['dur']
    css = f"""
#root .bar1 {{ position:absolute; left:192px; top:370px; height:92px; width:336px; background:{CASH}; border-radius:12px; transform-origin:0 50%; }}
#root .bar2 {{ position:absolute; left:192px; top:700px; height:92px; width:1500px; border-radius:12px; transform-origin:0 50%;
  background: repeating-linear-gradient(135deg, {CASH} 0 18px, #3F9A71 18px 36px); }}
#root .chip {{ position:absolute; left:760px; top:206px; height:96px; padding:0 36px; border-radius:48px; border:4px solid {CASH}; color:{CASH}; font-size:56px; font-weight:600; line-height:88px; box-sizing:border-box; }}
"""
    body = f'<div class="h" id="s3-n1" style="left:192px;top:210px;font-size:104px;color:{CASH};">$0B</div>\n'
    body += f'<div class="t" id="s3-u1" style="left:600px;top:244px;font-size:54px;">a year of cloud rental</div>\n'
    body += '<div class="bar1" id="s3-b1"></div>\n'
    body += '<div class="chip" id="s3-chip" style="left:1180px;top:340px;">&#8593; up 55%</div>\n'
    body += f'<div class="h" id="s3-n2" style="left:192px;top:540px;font-size:104px;color:{CASH};">$0T</div>\n'
    body += f'<div class="t" id="s3-u2" style="left:660px;top:574px;font-size:54px;">already signed, called backlog</div>\n'
    body += '<div class="bar2" id="s3-b2"></div>\n'
    body += f'<div class="t" id="s3-src" style="left:192px;top:940px;font-size:44px;color:{MUTED};">Synergy Research Group; company filings, unaudited</div>\n'
    t1 = cue(sid, 'cloud', 1, -0.2); t2 = cue(sid, 'about', 1, -0.15); tg = cue(sid, 'growing', 1, -0.1)
    js = pop('#s3-n1', t1, 0.5, 20) + pop('#s3-u1', t1 + 0.2, 0.5, 20)
    js += f"tl.fromTo('#s3-b1', {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.4, ease: 'power2.out' }}, {t1 + 0.1:.3f});\n"
    js += count('#s3-n1', t1 + 0.1, 1.4, 558, "'$' + Math.round(o.v) + 'B'")
    js += f"tl.fromTo('#s3-chip', {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.6, ease: 'power2.out' }}, {tg:.3f});\n"
    js += pop('#s3-n2', t2, 0.5, 20) + pop('#s3-u2', t2 + 0.2, 0.5, 20)
    js += f"tl.fromTo('#s3-b2', {{ scaleX: 0 }}, {{ scaleX: 1, duration: 2.4, ease: 'power2.out' }}, {t2 + 0.1:.3f});\n"
    js += pop('#s3-src', t2 + 0.6, 0.6, 8)
    js += count('#s3-n2', t2 + 0.1, 2.4, 2.49, "'$' + o.v.toFixed(2) + 'T'")
    # gentle drift on the striped backlog bar so the held end state is never dead
    js += f"tl.to('#s3-b2', {{ backgroundPosition: '72px 0px', duration: {d - t2 - 2.6:.2f}, ease: 'none' }}, {t2 + 2.5:.3f});\n"
    return scene(sid, css, body, js, d)

# ---------------- S4 the bill ----------------
def s4():
    sid = 's4'; d = TIM[sid]['dur']
    vals = [77.3, 39.4, 51.4, 33.9, 28.5]; total = sum(vals); H = 600.0; base = 900
    css = f"""
#root .seg {{ position:absolute; left:200px; width:170px; background:{COST}; transform-origin:50% 100%; border-top:4px solid #F6F3EC; box-sizing:border-box; }}
#root .rk {{ position:absolute; width:70px; height:50px; border-radius:6px; background:{CHIPS}; opacity:0; }}
#root .tag {{ position:absolute; height:76px; padding:0 30px; border-radius:38px; border:4px solid {COST}; color:{COST}; font-size:48px; font-weight:600; line-height:68px; box-sizing:border-box; }}
"""
    body = ''; cum = 0
    for i, v in enumerate(vals):
        h = H * v / total; y = base - H * (cum + v) / total; cum += v
        shade = '1' if i % 2 == 0 else '0.78'
        body += f'<div class="seg" id="s4-g{i}" style="top:{y:.1f}px;height:{h:.1f}px;opacity:{shade};"></div>\n'
    body += f'<div class="h" id="s4-n1" style="left:430px;top:300px;font-size:100px;color:{COST};">$0B</div>\n'
    body += f'<div class="t" id="s4-u1" style="left:430px;top:430px;font-size:52px;">five companies,<br>one quarter</div>\n'
    # campus building at right
    body += f'<div class="box" id="s4-roof" style="left:1030px;top:350px;width:340px;height:36px;border-radius:8px;background:#6F6150;"></div>\n'
    body += f'<div class="box" id="s4-bld" style="left:1050px;top:386px;width:300px;height:514px;background:{BUILD};"></div>\n'
    rid = 0
    for r in range(6):
        for c in range(3):
            body += f'<div class="rk" id="s4-r{rid}" style="left:{1070 + c*92}px;top:{{y}}px;"></div>\n'.replace('{y}', str(838 - r * 78)); rid += 1
    body += f'<div class="h" id="s4-n2" style="left:1400px;top:420px;font-size:100px;color:{COST};">$0B</div>\n'
    body += f'<div class="t" id="s4-u2" style="left:1400px;top:560px;font-size:52px;">1 GW campus</div>\n'
    body += f'<div class="t" id="s4-u2b" style="left:1400px;top:624px;font-size:44px;color:{MUTED};">a gigawatt of power</div>\n'
    body += '<div class="tag" id="s4-tag" style="left:1400px;top:710px;">Illustrative</div>\n'
    body += f'<div class="t" id="s4-src" style="left:192px;top:950px;font-size:44px;color:{MUTED};">SEC filings, unaudited. Campus: model estimate.</div>\n'
    tf = cue(sid, 'five', 1, -0.1); tq_end = cue_end(sid, 'quarter', 1); tg = cue(sid, 'gigawatt', 1, -0.3)
    seg_dur = (tq_end - tf) / 5.0
    js = ''
    for i in range(5):
        js += f"tl.fromTo('#s4-g{i}', {{ scaleY: 0 }}, {{ scaleY: 1, duration: {seg_dur*0.9:.2f}, ease: 'power1.out' }}, {tf + i*seg_dur:.3f});\n"
    js += pop('#s4-n1', tf, 0.4, 16) + pop('#s4-u1', tf + 0.5, 0.5, 16)
    js += count('#s4-n1', tf, tq_end - tf, 230.4, "'$' + o.v.toFixed(1) + 'B'")
    js += "tl.set('#s4-roof,#s4-bld', { opacity: 0 }, 0);\n"
    js += f"tl.fromTo('#s4-roof,#s4-bld', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: 'power2.out', stagger: 0.1 }}, {tg:.3f});\n"
    tc = cue(sid, 'costs', 1, -0.1); te = cue_end(sid, 'about', 1) ; tend = cue_end(sid, 'illustration', 1)
    fill_end = tend - 0.2
    for r in range(6):
        for c in range(3):
            rid = r * 3 + c
            t = tg + 0.5 + (fill_end - tg - 0.5) * (r * 3 + c) / 18.0
            js += f"tl.fromTo('#s4-r{rid}', {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: 'back.out(1.6)' }}, {t:.3f});\n"
    js += pop('#s4-n2', tc, 0.4, 16) + pop('#s4-u2', tc + 0.4, 0.5, 16)
    js += count('#s4-n2', tc, fill_end - tc, 52.6, "'$' + o.v.toFixed(1) + 'B'")
    js += pop('#s4-tag', cue(sid, 'illustration', 1, -0.5), 0.5, 16) + pop('#s4-u2b', tc + 0.6, 0.5, 8) + pop('#s4-src', tf + 0.8, 0.6, 8)
    return scene(sid, css, body, js, d)

# ---------------- S5 the catch ----------------
def s5():
    sid = 's5'; d = TIM[sid]['dur']; sc = 40.0; base = 900
    css = f"""
#root .tile {{ position:absolute; top:400px; width:220px; height:220px; border-radius:20px; background:{CHIPS}; color:#fff; font-family:'Fraunces',serif; font-weight:600; font-size:96px; text-align:center; line-height:220px; }}
#root .col {{ position:absolute; box-sizing:border-box; transform-origin:50% 100%; }}
"""
    body = '<div class="h" id="s5-h" style="left:192px;top:100px;font-size:80px;">The catch</div>\n'
    for i in range(6):
        body += f'<div class="tile" id="s5-t{i}" style="left:{192 + i*256}px;">{i+1}</div>\n'
    body += f'<div class="h" id="s5-yrs" style="left:192px;top:690px;font-size:92px;color:{COST};">about 6 years</div>\n'
    # part B columns
    rev_h = 8.24 * sc; dep = 6.71 * sc; opx = 0.99 * sc; pw = 0.81 * sc; intr = 3.68 * sc
    body += f'<div class="col" id="s5-rev" style="left:260px;width:280px;top:{base-rev_h:.1f}px;height:{rev_h:.1f}px;background:{CASH};border-radius:10px 10px 0 0;"></div>\n'
    body += f'<div class="col" id="s5-dep" style="left:660px;width:280px;top:{base-dep:.1f}px;height:{dep:.1f}px;background:{COST};"></div>\n'
    body += f'<div class="col" id="s5-opx" style="left:660px;width:280px;top:{base-dep-opx:.1f}px;height:{opx:.1f}px;background:{BUILD};border-top:3px solid #F6F3EC;"></div>\n'
    body += f'<div class="col" id="s5-pw" style="left:660px;width:280px;top:{base-dep-opx-pw:.1f}px;height:{pw:.1f}px;background:{POWER};border-top:3px solid #F6F3EC;"></div>\n'
    top_costs = base - dep - opx - pw
    body += (f'<div class="col" id="s5-int" style="left:660px;width:280px;top:{top_costs-intr:.1f}px;height:{intr:.1f}px;border:5px dashed {COST};'
             f'background: repeating-linear-gradient(135deg, rgba(194,85,45,0.28) 0 14px, rgba(194,85,45,0.08) 14px 28px);border-radius:10px 10px 0 0;"></div>\n')
    body += f'<div class="box" id="s5-ref" style="left:200px;width:800px;top:{base-rev_h:.1f}px;height:0;border-top:4px dashed {MUTED};"></div>\n'
    body += f'<div class="t" id="s5-lr" style="left:260px;top:916px;font-size:52px;width:280px;text-align:center;">Revenue</div>\n'
    body += f'<div class="t" id="s5-lc" style="left:660px;top:916px;font-size:52px;width:280px;text-align:center;">Costs</div>\n'
    body += f'<div class="h" id="s5-m1" style="left:1090px;top:330px;font-size:76px;color:{INK};">Roughly even.</div>\n'
    body += f'<div class="h" id="s5-m2" style="left:1090px;top:470px;font-size:76px;color:{COST};">Borrowing tips<br>it into a loss.</div>\n'
    body += f'<div class="t" id="s5-il" style="left:1090px;top:780px;font-size:44px;color:{MUTED};">Illustrative 1 GW campus<br>Model estimate, not a forecast</div>\n'
    ta = cue(sid, 'wear', 1, -0.3); ty = cue_end(sid, 'years', 1); tt = cue(sid, 'todays', 1, -0.05)
    tb = cue(sid, 'breaks', 1, -0.3); tbo = cue(sid, 'borrowing', 1, -0.2)
    js = pop('#s5-h', cue(sid, 'catch', 1, -0.5), 0.5, 20)
    js += f"tl.fromTo('.tile', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: 'power2.out', stagger: 0.08 }}, {ta - 0.3:.3f});\n"
    step = (ty - ta - 0.2) / 6.0
    for i in range(6):
        js += f"tl.to('#s5-t{i}', {{ backgroundColor: '{COST}', duration: 0.25, ease: 'power1.out' }}, {ta + 0.35 + i*step:.3f});\n"
    js += pop('#s5-yrs', cue(sid, 'about', 1, -0.2), 0.45, 20)
    js += fade('#s5-h,.tile,#s5-yrs', tt - 0.1, 0.4)
    js += "tl.set('#s5-rev,#s5-dep,#s5-opx,#s5-pw,#s5-int,#s5-ref,#s5-lr,#s5-lc,#s5-m1,#s5-m2,#s5-il', { opacity: 0 }, 0);\n"
    js += f"tl.fromTo('#s5-rev', {{ opacity: 1, scaleY: 0 }}, {{ opacity: 1, scaleY: 1, duration: 0.9, ease: 'power2.out' }}, {tt:.3f});\n"
    for j, n in enumerate(['dep', 'opx', 'pw']):
        js += f"tl.fromTo('#s5-{n}', {{ opacity: 1, scaleY: 0 }}, {{ opacity: 1, scaleY: 1, duration: 0.5, ease: 'power2.out' }}, {tt + 0.15 + j*0.35:.3f});\n"
    js += pop('#s5-lr', tt + 0.4, 0.4, 12) + pop('#s5-lc', tt + 0.5, 0.4, 12)
    js += f"tl.fromTo('#s5-ref', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {tb:.3f});\n"
    js += pop('#s5-m1', tb, 0.5, 16)
    js += f"tl.fromTo('#s5-int', {{ opacity: 1, scaleY: 0 }}, {{ opacity: 1, scaleY: 1, duration: 0.8, ease: 'power2.out' }}, {tbo:.3f});\n"
    js += pop('#s5-m2', tbo + 0.1, 0.6, 16) + pop('#s5-il', tt + 0.2, 0.5, 8)
    return scene(sid, css, body, js, d)

# ---------------- S6 who keeps the money ----------------
def s6():
    sid = 's6'; d = TIM[sid]['dur']; x0 = 660; k = 1060 / 70.0
    rows = [('Chip makers', 360, 66.2, CHIPS, '66%'), ('Big clouds', 540, 36.2, COMPUTE, '36% to 39%'), ('GPU clouds', 720, 0, COST, 'zero or less')]
    css = f"#root .bar {{ position:absolute; height:104px; border-radius:0 12px 12px 0; transform-origin:0 50%; }}\n"
    body = '<div class="h" id="s6-h" style="left:192px;top:100px;font-size:80px;">Who keeps the money?</div>\n'
    for i, (lab, y, v, col, txt) in enumerate(rows):
        body += f'<div class="t" id="s6-l{i}" style="left:192px;top:{y+22}px;font-size:54px;">{lab}</div>\n'
        if v:
            body += f'<div class="bar" id="s6-b{i}" style="left:{x0}px;top:{y}px;width:{v*k:.1f}px;background:{col};"></div>\n'
        else:
            body += f'<div class="bar" id="s6-b{i}" style="left:{x0}px;top:{y}px;width:12px;background:{col};"></div>\n'
    body += f'<div class="bar" id="s6-b1x" style="left:{x0 + 36.2*k:.1f}px;top:540px;width:{2.5*k:.1f}px;background:#4A78C4;border-radius:0 12px 12px 0;opacity:0;"></div>\n'
    body += f'<div class="h" id="s6-v0" style="left:{x0 + 66.2*k - 20:.1f}px;top:{360+10}px;font-size:80px;color:#fff;transform:translateX(-100%);">66%</div>\n'
    body += f'<div class="h" id="s6-v1" style="left:{x0 + 38.7*k + 30:.1f}px;top:{540+10}px;font-size:80px;color:{COMPUTE};">36% to 39%</div>\n'
    body += f'<div class="h" id="s6-v2" style="left:{x0 + 12 + 30}px;top:{720+10}px;font-size:80px;color:{COST};">zero or less</div>\n'
    body += f'<div class="t" id="s6-f" style="left:192px;top:900px;font-size:46px;color:{MUTED};">Operating margin: profit kept from each $1 of sales</div>\n'
    body += f'<div class="t" id="s6-src" style="left:192px;top:960px;font-size:44px;color:{MUTED};">Latest quarters, company filings, unaudited</div>\n'
    js = pop('#s6-h', 0.25, 0.5, 16)
    cues = [cue(sid, 'chipmakers', 1, -0.2) if any(nrm(w[0]) == 'chipmakers' for w in W[sid]['words']) else cue(sid, 'chip', 1, -0.2),
            cue(sid, 'big', 1, -0.2), cue(sid, 'clouds', 2, -0.3)]
    for i in range(3):
        t = cues[i]
        js += pop(f'#s6-l{i}', t, 0.4, 12)
        js += f"tl.fromTo('#s6-b{i}', {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.0, ease: 'power2.out' }}, {t + 0.1:.3f});\n"
    js += "tl.set('#s6-v0,#s6-v1,#s6-v2', { opacity: 0 }, 0);\n"
    tn = cue(sid, 'nvidias', 1, -0.1) if any(nrm(w[0]) == 'nvidias' for w in W[sid]['words']) else cue(sid, 'margin', 1, -0.1)
    js += f"tl.fromTo('#s6-v0', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {cues[0] + 0.9:.3f});\n"
    js += f"tl.fromTo('#s6-b1x', {{ opacity: 0, scaleX: 0 }}, {{ opacity: 1, scaleX: 1, duration: 0.6, ease: 'power2.out' }}, {cue(sid, 'thirty', 1, -0.1) if False else cues[1] + 1.4:.3f});\n"
    js += f"tl.fromTo('#s6-v1', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {cues[1] + 1.1:.3f});\n"
    js += f"tl.fromTo('#s6-v2', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {cue(sid, 'zero', 1, -0.3):.3f});\n"
    js += pop('#s6-f', tn, 0.5, 12) + pop('#s6-src', tn + 0.4, 0.5, 8)
    return scene(sid, css, body, js, d)

# ---------------- S7 close ----------------
def s7():
    sid = 's7'; d = TIM[sid]['dur']
    tq = cue(sid, 'whether', 2, -0.1); tr = cue(sid, 'revenue', 1, -0.2); tend = cue_end(sid, 'interest', 1)
    tt = tend + 0.5
    css = f"""
#root .ttl {{ position:absolute; left:0; width:1920px; text-align:center; }}
#root .seg6 {{ position:absolute; top:640px; width:150px; height:18px; border-radius:9px; }}
"""
    body = '<div id="s7-chart">\n'
    body += '<svg class="box" style="left:0;top:0;" width="1920" height="1080" viewBox="0 0 1920 1080">'
    body += f'<line x1="200" y1="860" x2="1240" y2="860" stroke="{MUTED}" stroke-width="4"/><line x1="200" y1="860" x2="200" y2="260" stroke="{MUTED}" stroke-width="4"/>'
    body += f'<path id="s7-pg" d="M 200 800 C 520 800 780 600 1180 360" fill="none" stroke="{CASH}" stroke-width="14" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000 1200" stroke-dashoffset="1100"/>'
    body += f'<path id="s7-pc" d="M 200 800 C 460 690 840 580 1180 360" fill="none" stroke="{COST}" stroke-width="14" stroke-linecap="round" pathLength="1000" stroke-dasharray="1000 1200" stroke-dashoffset="1100"/>'
    body += f'<circle id="s7-dot" cx="200" cy="800" r="16" fill="{INK}"/>'
    body += '</svg>\n'
    body += f'<div class="t" id="s7-lg" style="left:1290px;top:250px;font-size:52px;color:{CASH};line-height:1.15;">Revenue per<br>gigawatt</div>\n'
    body += f'<div class="t" id="s7-lc" style="left:1290px;top:420px;font-size:52px;color:{COST};line-height:1.15;">Depreciation<br>and interest</div>\n'
    body += f'<div class="h" id="s7-qm" style="left:1205px;top:272px;font-size:120px;color:{INK};opacity:0;">?</div>\n'
    body += f'<div class="h" id="s7-q" style="left:190px;top:100px;font-size:84px;">Which one runs ahead?</div>\n'
    body += '</div>\n'
    body += f'<div class="h ttl" id="s7-title" style="top:370px;font-size:150px;opacity:0;">Hyperscalers, explained</div>\n'
    cols = [COMPUTE, POWER, BUILD, CHIPS, CASH, COST]
    for i, c in enumerate(cols):
        body += f'<div class="seg6" id="s7-c{i}" style="left:{510 + i*160}px;background:{c};opacity:0;"></div>\n'
    js = pop('#s7-q', 0.3, 0.6, 16)
    js += f"tl.fromTo('#s7-pc', {{ strokeDashoffset: 1100 }}, {{ strokeDashoffset: 0, duration: {tend - tr + 0.2:.2f}, ease: 'power1.inOut' }}, {tr:.3f});\n"
    js += f"tl.fromTo('#s7-pg', {{ strokeDashoffset: 1100 }}, {{ strokeDashoffset: 0, duration: {tend - tr + 0.2:.2f}, ease: 'power1.inOut' }}, {tr + 0.1:.3f});\n"
    js += "tl.set('#s7-lg,#s7-lc', { opacity: 0 }, 0);\n"
    js += f"tl.fromTo('#s7-qm', {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: 'back.out(1.8)' }}, {tend:.3f});\n"
    js += f"tl.fromTo('#s7-dot', {{ scale: 1, svgOrigin: '200 800' }}, {{ scale: 1.9, svgOrigin: '200 800', duration: 0.7, yoyo: true, repeat: {max(1, int((tr - 0.9) / 0.7))}, ease: 'sine.inOut' }}, 0.8);\n"
    js += f"tl.fromTo('#s7-lg', {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {tr + 0.9:.3f});\n"
    js += f"tl.fromTo('#s7-lc', {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {tr + 1.5:.3f});\n"
    js += f"tl.to('#s7-chart', {{ opacity: 0, duration: 0.5, ease: 'power2.in' }}, {tt - 0.1:.3f});\n"
    js += f"tl.fromTo('#s7-title', {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }}, {tt + 0.3:.3f});\n"
    for i in range(6):
        js += f"tl.fromTo('#s7-c{i}', {{ opacity: 0, scaleX: 0 }}, {{ opacity: 1, scaleX: 1, duration: 0.45, ease: 'power2.out' }}, {tt + 0.8 + i*0.1:.3f});\n"
    # the title card never fades out at the end of the film (only the shared scene fade)
    return scene(sid, css, body, js, d, True, False), tt

for fn, key in [(s1, 's1'), (s2, 's2'), (s3, 's3'), (s4, 's4'), (s5, 's5'), (s6, 's6')]:
    scenes[key] = fn()
scenes['s7'], title_t = s7()
os.makedirs(os.path.join(here, 'compositions'), exist_ok=True)
for k, v in scenes.items():
    open(os.path.join(here, 'compositions', k + '.html'), 'w').write(v)

total = T['total']
hosts = ''
for i, sc in enumerate(S['scenes']):
    t = TIM[sc['id']]
    hosts += (f'<div id="{sc["id"]}" data-composition-id="{sc["id"]}" data-composition-src="compositions/{sc["id"]}.html" '
              f'data-start="{t["start"]}" data-duration="{t["dur"]}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>\n')
index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="assets/gsap.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1920px; height:1080px; overflow:hidden; background:#F6F3EC; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
{hosts}<audio id="narration" src="assets/narration.wav" data-start="0" data-duration="{total}" data-track-index="2" data-volume="1"></audio>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
window.__timelines['main'] = tl;
</script>
</body>
</html>
"""
open(os.path.join(here, 'index.html'), 'w').write(index)
json.dump({'title_card_start': round(title_t + 0.3, 3), 'total': total}, open(os.path.join(here, 'build/cards.json'), 'w'))
print('ok', total, 'title at', title_t)
