/* charts-a.js: capex wave, capex intensity, the illustrative 1 GW campus waterfall, and the debt dumbbell.
   Draws with D3 v7 into each figure's .chart, then calls HX.chartReady. Every lookup is guarded: a missing element or
   data key leaves the fallback table in place. Reduced motion draws the final state with no tweens. */
(function () {
  "use strict";
  var HX = window.HX;
  var d3 = null;
  if (!HX || typeof HX.ready !== "function" || typeof HX.get !== "function") return;

  var DUR = HX.reduced ? 0 : 350;

  /* ---------- small helpers ---------- */
  function byId(id) { return document.getElementById(id); }
  function num(v) { return typeof v === "number" && isFinite(v) ? v : null; }
  function mk(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }
  function clear(node) { while (node && node.firstChild) node.removeChild(node.firstChild); }
  function width(host) {
    var w = host ? (host.clientWidth || (host.getBoundingClientRect ? host.getBoundingClientRect().width : 0)) : 0;
    return Math.max(260, Math.floor(w || 320));
  }
  function money(v) { return HX.fmt(v, "b1"); }
  function axisMoney(v) { return v === 0 ? "$0" : HX.fmt(v, "b0"); }
  function pct(v) { return HX.fmt(v, "p0"); }
  function svgIn(host, w, h) {
    return d3.select(host).append("svg")
      .attr("viewBox", "0 0 " + w + " " + h).attr("width", w).attr("height", h)
      .attr("focusable", "false").attr("aria-hidden", "true");
  }
  function text(parent, cls, x, y, s, anchor) {
    var t = parent.append("text").attr("class", cls).attr("x", x).attr("y", y).text(s);
    if (anchor) t.attr("text-anchor", anchor);
    return t;
  }
  function run(fn) { try { fn(); } catch (e) { /* leave the fallback table visible */ } }
  function qLabel(s) {
    var m = /^Q([1-4]) (\d\d)$/.exec(String(s));
    return m ? "Q" + m[1] + " 20" + m[2] : String(s);
  }
  function cap1(s) { s = String(s); return s.charAt(0).toUpperCase() + s.slice(1); }

  /* =====================================================================
     fig-capex-wave: stacked columns of quarterly capex
     ===================================================================== */
  function waveData() {
    var labels = HX.get("capex_wave.labels"), series = HX.get("capex_wave.series");
    if (!Array.isArray(labels) || !Array.isArray(series) || !labels.length) return null;
    var ser = [];
    series.forEach(function (s) {
      if (s && Array.isArray(s.values)) {
        ser.push({ ticker: String(s.ticker || "x"), name: String(s.name || s.ticker || ""), values: s.values });
      }
    });
    if (!ser.length) return null;
    var rows = labels.map(function (lab, i) {
      var cum = 0, five = 0;
      var parts = ser.map(function (s) {
        var v = num(s.values[i]);
        var p = { v: v, y0: cum, y1: cum };
        if (v != null && v > 0) { cum += v; p.y1 = cum; }
        if (v != null && s.ticker !== "CRWV") five += v;
        return p;
      });
      return { label: String(lab), parts: parts, total: cum, five: five };
    });
    var n = rows.length;
    var latest = num(HX.get("capex_wave.big5_latest"));
    if (latest != null) rows[n - 1].five = latest;
    var yi = -1, m = /^Q([1-4]) (\d\d)$/.exec(rows[n - 1].label);
    if (m) {
      var yy = parseInt(m[2], 10) - 1;
      var want = "Q" + m[1] + " " + (yy < 10 ? "0" + yy : String(yy));
      rows.forEach(function (r, i) { if (r.label === want) yi = i; });
    }
    var ago = num(HX.get("capex_wave.big5_year_ago"));
    if (yi >= 0 && ago != null) rows[yi].five = ago;
    return { rows: rows, ser: ser, yearAgo: yi };
  }

  function initWave() {
    var host = byId("fig-capex-wave-chart"), D = waveData();
    if (!host || !D) return;
    var uiEl = byId("fig-capex-wave-ui"), CW = "fig-capex-wave-";
    var n = D.rows.length, sel = n - 1, first = true, W = 320;
    var geo = { left: 0, step: 1 }, band = null;
    var readEl = null, slider = null, outEl = null;

    if (uiEl) {
      clear(uiEl);
      var pick = mk("div", CW + "pick range");
      var lab = mk("label", "", "Quarter");
      lab.setAttribute("for", CW + "q");
      slider = document.createElement("input");
      slider.type = "range"; slider.id = CW + "q";
      slider.min = "0"; slider.max = String(n - 1); slider.step = "1"; slider.value = String(sel);
      outEl = document.createElement("output");
      outEl.setAttribute("for", CW + "q");
      pick.appendChild(lab); pick.appendChild(slider); pick.appendChild(outEl);
      readEl = mk("div", CW + "read");
      readEl.setAttribute("aria-live", "polite");
      uiEl.appendChild(pick); uiEl.appendChild(readEl);
      slider.addEventListener("input", function () { select(parseInt(slider.value, 10), true); });
    }

    function readout(i) {
      if (!readEl) return;
      var r = D.rows[i];
      clear(readEl);
      var h = mk("p", CW + "read-h");
      h.appendChild(mk("strong", "", qLabel(r.label)));
      h.appendChild(document.createTextNode(" Five companies: " + money(r.five)));
      readEl.appendChild(h);
      var ul = mk("ul", CW + "read-list");
      D.ser.forEach(function (s, j) {
        var v = r.parts[j].v, li = mk("li");
        li.appendChild(mk("span", CW + "sw " + CW + "s-" + s.ticker.toLowerCase()));
        li.appendChild(mk("span", CW + "read-n", s.name));
        li.appendChild(mk("b", "", v != null ? money(v) : "not reported"));
        ul.appendChild(li);
      });
      readEl.appendChild(ul);
    }

    function select(i, fromSlider) {
      if (!(i >= 0)) i = 0;
      if (i > n - 1) i = n - 1;
      sel = i;
      if (band) band.attr("x", i * geo.step).attr("width", geo.step);
      readout(i);
      if (slider) {
        if (!fromSlider) slider.value = String(i);
        var r = D.rows[i];
        if (outEl) outEl.textContent = qLabel(r.label);
        slider.setAttribute("aria-valuetext", qLabel(r.label) + ": " + money(r.five) + " from the five companies");
      }
    }

    function draw() {
      W = width(host);
      var narrow = W < 480;
      var m = { top: 32, right: narrow ? 128 : 158, bottom: 28, left: 4 };
      var H = narrow ? 292 : 336;
      var iw = Math.max(80, W - m.left - m.right), ih = H - m.top - m.bottom;
      var step = iw / n, bw = Math.max(3, Math.min(step * 0.78, 22));
      var maxT = d3.max(D.rows, function (r) { return r.total; }) || 1;
      var yMax = Math.max(50, Math.ceil(maxT / 50) * 50);
      var y = d3.scaleLinear().domain([0, yMax]).range([ih, 0]);
      function cx(i) { return (i + 0.5) * step; }
      geo = { left: m.left, step: step };

      clear(host);
      var svg = svgIn(host, W, H);
      var g = svg.append("g").attr("transform", "translate(" + m.left + "," + m.top + ")");
      band = g.append("rect").attr("class", CW + "band").attr("x", 0).attr("y", -6).attr("width", step).attr("height", ih + 6);

      var ticks = d3.range(100, yMax, 100);
      if (!ticks.length) ticks = [Math.round(yMax / 2)];
      ticks.forEach(function (t) {
        g.append("line").attr("class", CW + "grid").attr("x1", 0).attr("x2", iw).attr("y1", y(t)).attr("y2", y(t));
        text(g, CW + "ylab", 0, y(t) + 15, HX.fmt(t, "b0"));
      });
      g.append("line").attr("class", CW + "base").attr("x1", 0).attr("x2", iw).attr("y1", ih).attr("y2", ih);

      D.rows.forEach(function (r, i) {
        var q = /^Q([1-4]) (\d\d)$/.exec(r.label);
        if (!q || q[1] !== "1") return;
        if (narrow && parseInt(q[2], 10) % 2 !== 0) return;
        g.append("line").attr("class", CW + "tick").attr("x1", cx(i)).attr("x2", cx(i)).attr("y1", ih).attr("y2", ih + 4);
        text(g, CW + "xlab", cx(i), ih + 19, "20" + q[2], "middle");
      });

      var colNodes = [];
      D.rows.forEach(function (r, i) {
        var cg = g.append("g").attr("class", CW + "col");
        r.parts.forEach(function (p, j) {
          if (p.v == null || p.v <= 0) return;
          cg.append("rect")
            .attr("class", CW + "seg " + CW + "s-" + D.ser[j].ticker.toLowerCase())
            .attr("x", cx(i) - bw / 2).attr("y", y(p.y1)).attr("width", bw)
            .attr("height", Math.max(0, y(p.y0) - y(p.y1)));
        });
        colNodes.push(cg.node());
      });

      /* direct labels for the latest quarter, a total above it, and the year-ago marker */
      var lg = g.append("g").attr("class", CW + "labels");
      var last = D.rows[n - 1], right = cx(n - 1) + bw / 2;
      var items = [];
      last.parts.forEach(function (p, j) {
        if (p.v != null && p.v > 0) {
          var mid = y((p.y0 + p.y1) / 2);
          items.push({ j: j, v: p.v, mid: mid, ly: mid, top: y(p.y1), bot: y(p.y0) });
        }
      });
      items.sort(function (a, b) { return a.mid - b.mid; });
      for (var k = 1; k < items.length; k++) {
        if (items[k].ly < items[k - 1].ly + 16) items[k].ly = items[k - 1].ly + 16;
      }
      items.forEach(function (it) {
        var s = D.ser[it.j], tk = s.ticker.toLowerCase();
        lg.append("rect").attr("class", CW + "brk " + CW + "s-" + tk)
          .attr("x", right + 3).attr("y", it.top).attr("width", 3).attr("height", Math.max(2, it.bot - it.top));
        var t = lg.append("text").attr("class", CW + "lab").attr("x", right + 11).attr("y", it.ly).attr("dy", "0.35em");
        t.append("tspan").text(s.name + " ");
        t.append("tspan").attr("class", CW + "val").text(money(it.v));
      });
      text(lg, CW + "total", right, y(last.total) - 8, money(last.five), "end");
      if (D.yearAgo >= 0) {
        var yr = D.rows[D.yearAgo], yx = cx(D.yearAgo) + bw / 2;
        lg.append("circle").attr("class", CW + "dot").attr("cx", cx(D.yearAgo)).attr("cy", y(yr.total) - 4).attr("r", 2.5);
        text(lg, CW + "yago", yx, y(yr.total) - 11, money(yr.five) + " a year earlier", "end");
      }

      /* tap, hover and drag: the overlay picks a quarter */
      function pickAt(ev) {
        var node = svg.node(), r = node.getBoundingClientRect();
        if (!r.width) return;
        var x = (ev.clientX - r.left) * (W / r.width);
        select(Math.floor((x - m.left) / step), false);
      }
      g.append("rect").attr("class", CW + "hit").attr("x", -m.left).attr("y", -m.top).attr("width", W).attr("height", H)
        .on("pointerdown", pickAt).on("pointermove", pickAt);

      if (first) {
        first = false;
        HX.reveal(host, function (tl) {
          tl.from(colNodes, { opacity: 0, y: 18, duration: 0.6, stagger: { amount: 0.9 } });
          tl.from(lg.node(), { opacity: 0, duration: 0.5 }, "-=0.3");
        });
      }
      host.setAttribute("aria-label", "Stacked columns of quarterly capex by company, from " + qLabel(D.rows[0].label) +
        " to " + qLabel(last.label) + ". In the latest quarter the five companies spent " + money(last.five) +
        ", against " + (D.yearAgo >= 0 ? money(D.rows[D.yearAgo].five) : "a lower amount") + " a year earlier.");
    }

    draw();
    select(sel, false);
    HX.chartReady(host);
    HX.onResize(function () { run(function () { draw(); select(sel, false); }); });
  }

  /* =====================================================================
     fig-capex-intensity: capex as a share of revenue (bar) and of operating cash flow (dot)
     ===================================================================== */
  function initIntensity() {
    var host = byId("fig-capex-intensity-chart"), raw = HX.get("intensity.rows");
    if (!host || !Array.isArray(raw)) return;
    var IP = "fig-capex-intensity-", rows = [], first = true;
    raw.forEach(function (r) {
      if (r && num(r.capex_to_revenue) != null) {
        rows.push({ name: String(r.name || r.ticker || ""), rev: r.capex_to_revenue, ocf: num(r.capex_to_ocf) });
      }
    });
    if (!rows.length) return;
    rows.sort(function (a, b) { return b.rev - a.rev; });

    function draw() {
      var W = width(host), px = 8, rowH = 44, y0 = 90, nR = rows.length;
      var maxV = d3.max(rows, function (r) { return Math.max(r.rev, r.ocf == null ? 0 : r.ocf); }) || 100;
      var cap = Math.min(175, Math.max(125, Math.ceil(maxV / 25) * 25));
      var ay = y0 + nR * rowH - 2, H = ay + 30;
      var xs = d3.scaleLinear().domain([0, cap]).range([px, W - px]);
      var x100 = xs(100);
      clear(host);
      var svg = svgIn(host, W, H);

      svg.append("rect").attr("class", IP + "lg-bar").attr("x", px).attr("y", 6).attr("width", 12).attr("height", 12).attr("rx", 3);
      text(svg, IP + "lg", px + 20, 17, "Capex as a share of revenue");
      svg.append("circle").attr("class", IP + "lg-dot").attr("cx", px + 6).attr("cy", 33).attr("r", 6);
      text(svg, IP + "lg", px + 20, 38, "Capex as a share of cash from operations");

      svg.append("line").attr("class", IP + "axis").attr("x1", px).attr("x2", W - px).attr("y1", ay).attr("y2", ay);
      d3.range(0, cap + 1, 50).forEach(function (t) {
        svg.append("line").attr("class", IP + "axis").attr("x1", xs(t)).attr("x2", xs(t)).attr("y1", ay).attr("y2", ay + 4);
        text(svg, IP + "tick", xs(t), ay + 19, pct(t), t === 0 ? "start" : "middle");
      });

      var bars = [], dots = [], links = [];
      rows.forEach(function (r, i) {
        var yy = y0 + i * rowH, cy = yy + 26;
        text(svg, IP + "name", px, yy + 13, r.name);
        var vt = svg.append("text").attr("class", IP + "vals").attr("x", W - px).attr("y", yy + 13).attr("text-anchor", "end");
        vt.append("tspan").attr("class", IP + "g-bar").text("■ ");
        vt.append("tspan").attr("class", r.rev > 100 ? IP + "over" : IP + "ok").text(pct(r.rev));
        vt.append("tspan").attr("class", IP + "g-dot").attr("dx", 12).text("● ");
        vt.append("tspan").attr("class", r.ocf != null && r.ocf > 100 ? IP + "over" : IP + "ok").text(r.ocf != null ? pct(r.ocf) : "n/a");

        var barEnd = xs(Math.min(r.rev, cap));
        var bar = svg.append("rect").attr("class", IP + "bar").attr("x", px).attr("y", yy + 20).attr("height", 12).attr("rx", 3)
          .attr("width", Math.max(2, barEnd - px));
        bars.push(bar.node());
        var dotX = null;
        if (r.ocf != null) dotX = r.ocf > cap ? xs(cap) - 7 : xs(r.ocf);
        if (r.rev > cap) {
          var bx = (dotX != null && dotX > xs(cap) - 12) ? xs(cap) - 26 : xs(cap) - 10;
          svg.append("path").attr("class", IP + "cut")
            .attr("d", "M" + bx + "," + (yy + 17) + " l-4,18 M" + (bx + 5) + "," + (yy + 17) + " l-4,18");
        }
        if (dotX != null) {
          if (dotX - barEnd > 8) {
            links.push(svg.append("line").attr("class", IP + "link").attr("x1", barEnd).attr("x2", dotX).attr("y1", cy).attr("y2", cy).node());
          }
          dots.push(svg.append("circle").attr("class", IP + "dot").attr("cx", dotX).attr("cy", cy).attr("r", 6.5).node());
        }
      });

      svg.append("line").attr("class", IP + "ref").attr("x1", x100).attr("x2", x100).attr("y1", 48).attr("y2", ay);
      var leftSide = x100 + 6 + 118 > W - 4;
      var rx = leftSide ? x100 - 6 : x100 + 6, ra = leftSide ? "end" : "start";
      text(svg, IP + "reftxt", rx, 63, "spends more than", ra);
      text(svg, IP + "reftxt", rx, 79, "it brings in", ra);

      if (first) {
        first = false;
        HX.reveal(host, function (tl) {
          tl.from(bars, { attr: { width: 0 }, duration: 0.7, stagger: 0.1 });
          tl.from(links.concat(dots), { opacity: 0, duration: 0.5, stagger: 0.05 }, "-=0.4");
        });
      }
      host.setAttribute("aria-label", "Capex as a share of revenue and of cash from operations over the last 12 months, highest first. " +
        rows.map(function (r) {
          return r.name + ": " + pct(r.rev) + " of revenue, " + (r.ocf != null ? pct(r.ocf) + " of cash from operations" : "no cash figure");
        }).join("; ") + ".");
    }

    draw();
    HX.chartReady(host);
    HX.onResize(function () { run(draw); });
  }

  /* =====================================================================
     fig-debt: dumbbell of long-term debt, Dec 31 2025 versus latest
     ===================================================================== */
  function initDebt() {
    var host = byId("fig-debt-chart"), raw = HX.get("debt.rows");
    if (!host || !Array.isArray(raw)) return;
    var DP = "fig-debt-", rows = [], first = true;
    raw.forEach(function (r) {
      if (r && num(r.before_b) != null && num(r.now_b) != null) {
        rows.push({ name: String(r.name || r.ticker || ""), a: r.before_b, b: r.now_b,
                    d: Math.round((r.now_b - r.before_b) * 10) / 10 });
      }
    });
    if (!rows.length) return;
    rows.sort(function (p, q) { return q.d - p.d; });

    function draw() {
      var W = width(host), px = 8, top = 40, pitch = 62, n = rows.length;
      var maxV = d3.max(rows, function (r) { return Math.max(r.a, r.b); }) || 100;
      var cap = Math.max(40, Math.ceil(maxV / 20) * 20);
      var ay = top + n * pitch, H = ay + 30;
      var xs = d3.scaleLinear().domain([0, cap]).range([px, W - px]);
      clear(host);
      var svg = svgIn(host, W, H);

      svg.append("circle").attr("class", DP + "lg-a").attr("cx", px + 6).attr("cy", 11).attr("r", 6);
      text(svg, DP + "lg", px + 18, 16, "Dec 31 2025");
      svg.append("circle").attr("class", DP + "lg-b").attr("cx", px + 134).attr("cy", 11).attr("r", 6);
      text(svg, DP + "lg", px + 146, 16, "Latest quarter");

      svg.append("line").attr("class", DP + "axis").attr("x1", px).attr("x2", W - px).attr("y1", ay).attr("y2", ay);
      d3.range(0, cap + 1, 50).forEach(function (t) {
        if (t > 0) svg.append("line").attr("class", DP + "grid").attr("x1", xs(t)).attr("x2", xs(t)).attr("y1", top - 4).attr("y2", ay);
        text(svg, DP + "tick", xs(t), ay + 19, axisMoney(t), t === 0 ? "start" : "middle");
      });

      var parts = [];
      rows.forEach(function (r, i) {
        var yy = top + i * pitch, cy = yy + 32, xa = xs(r.a), xb = xs(r.b);
        text(svg, DP + "name", px, yy + 14, r.name);
        text(svg, DP + "chg", W - px, yy + 14, (r.d >= 0 ? "+" : "") + money(r.d), "end");
        svg.append("line").attr("class", DP + "track").attr("x1", px).attr("x2", W - px).attr("y1", cy).attr("y2", cy);
        var link = svg.append("line").attr("class", DP + "link").attr("x1", xa).attr("x2", xb).attr("y1", cy).attr("y2", cy);
        var dotA = svg.append("circle").attr("class", DP + "dot-a").attr("cx", xa).attr("cy", cy).attr("r", 6);
        var dotB = svg.append("circle").attr("class", DP + "dot-b").attr("cx", xb).attr("cy", cy).attr("r", 6.5);
        var label = money(r.a) + " to " + money(r.b), half = label.length * 3.7;
        var mid = Math.min(W - px - half, Math.max(px + half, (xa + xb) / 2));
        var val = text(svg, DP + "val", mid, yy + 56, label, "middle");
        parts.push({ link: link.node(), a: dotA.node(), b: dotB.node(), val: val.node(), xa: xa });
      });

      if (first) {
        first = false;
        HX.reveal(host, function (tl) {
          parts.forEach(function (p, i) {
            var at = i * 0.1;
            tl.from(p.link, { attr: { x2: p.xa }, duration: 0.7 }, at);
            tl.from(p.b, { attr: { cx: p.xa }, duration: 0.7 }, at);
            tl.from(p.val, { opacity: 0, duration: 0.5 }, at + 0.3);
          });
        });
      }
      host.setAttribute("aria-label", "Long-term debt from Dec 31 2025 to the latest quarter, largest increase first. " +
        rows.map(function (r) { return r.name + " from " + money(r.a) + " to " + money(r.b) + ", up " + money(r.d); }).join("; ") + ".");
    }

    draw();
    HX.chartReady(host);
    HX.onResize(function () { run(draw); });
  }

  /* =====================================================================
     fig-campus: interactive waterfall for the illustrative 1 GW campus
     ===================================================================== */
  function initCampus() {
    var host = byId("fig-campus-chart"), ctlEl = byId("fig-campus-controls"), statEl = byId("fig-campus-stats");
    if (!host) return;
    var P = HX.get("campus.params"), cases = HX.get("campus.cases"), fins = HX.get("campus.financing");
    var capIT = num(HX.get("campus.capex_it_b")), capFac = num(HX.get("campus.capex_facility_b"));
    var capAll = num(HX.get("campus.capex_b")), powerB = num(HX.get("campus.power_b"));
    if (!P || !cases || !fins || capIT == null || capFac == null || capAll == null || powerB == null) return;
    var opexShare = num(P.opex_share), lifeFac = num(P.life_fac), lifeDef = num(P.life_it);
    if (opexShare == null || lifeFac == null || lifeDef == null || lifeFac <= 0 || opexShare >= 1) return;

    var CC = "fig-campus-", LIFE_MIN = 3, LIFE_MAX = 6;
    var caseKeys = ["low", "base", "high"].filter(function (k) { return cases[k] && num(cases[k].revenue_b) != null; });
    var finKeys = ["hyperscaler", "neocloud"].filter(function (k) {
      return fins[k] && num(fins[k].debt_share) != null && num(fins[k].rate) != null;
    });
    if (!caseKeys.length || !finKeys.length) return;
    var state = {
      c: caseKeys.indexOf("base") >= 0 ? "base" : caseKeys[0],
      f: finKeys.indexOf("hyperscaler") >= 0 ? "hyperscaler" : finKeys[0],
      life: Math.min(LIFE_MAX, Math.max(LIFE_MIN, Math.round(lifeDef)))
    };
    var maxRev = d3.max(caseKeys, function (k) { return cases[k].revenue_b; }) || 10;
    var dMax = Math.ceil(maxRev / 5) * 5;
    var first = true, W = 320, x = null, rowsRef = [], connRef = [], gridG = null;
    var geo = { top: 8, rowH: 36, px: 8, ay: 0 };
    var ctl = {}, stat = {};

    /* the recompute: depreciation = capex_it / life + capex_facility / life_fac; running costs = revenue x opex_share;
       interest = capex x debt_share x rate. At the model's own chip life the published numbers are used so the
       defaults match site_data exactly. */
    function calc(c, f, life) {
      var rev = cases[c].revenue_b, fin = fins[f];
      var dep = capIT / life + capFac / lifeFac;
      var opex = rev * opexShare;
      var ebitda = rev - powerB - opex;
      var ebit = ebitda - dep;
      var interest = capAll * fin.debt_share * fin.rate;
      var r = { revenue: rev, power: powerB, opex: opex, ebitda: ebitda, depreciation: dep, ebit: ebit,
                interest: interest, pretax: ebit - interest, payback: ebitda > 0 ? capAll / ebitda : null };
      var pub = life === lifeDef && cases[c]["pnl_" + f] ? cases[c]["pnl_" + f] : null;
      if (pub) {
        ["revenue", "power", "opex", "ebitda", "depreciation", "ebit", "interest", "pretax", "payback"].forEach(function (k) {
          if (num(pub[k]) != null) r[k] = pub[k];
        });
      }
      return r;
    }

    function breakeven(life, f, withInterest) {
      var den = 1 - opexShare;
      if (den <= 0) return null;
      var dep = capIT / life + capFac / lifeFac;
      var intr = withInterest ? capAll * fins[f].debt_share * fins[f].rate : 0;
      if (life === lifeDef) {
        var pub = withInterest ? (f === "neocloud" ? num(HX.get("campus.breakeven_revenue_neocloud_b")) : null)
                               : num(HX.get("campus.breakeven_revenue_b"));
        if (pub != null) return pub;
      }
      return (powerB + dep + intr) / den;
    }

    function steps(r) {
      return [
        { label: "Revenue", v: r.revenue, total: true, c: "compute" },
        { label: "Electricity", v: -r.power, total: false, c: "power" },
        { label: "Running costs", v: -r.opex, total: false, c: "buildings" },
        { label: "Cash profit (EBITDA)", v: r.ebitda, total: true, c: r.ebitda >= 0 ? "cash" : "cost" },
        { label: "Depreciation", v: -r.depreciation, total: false, c: "cost" },
        { label: "Operating profit", v: r.ebit, total: true, c: r.ebit >= 0 ? "cash" : "cost" },
        { label: "Interest", v: -r.interest, total: false, c: "cost" },
        { label: "Profit before tax", v: r.pretax, total: true, c: r.pretax >= 0 ? "cash" : "cost" }
      ];
    }

    /* ---------- controls ---------- */
    function group(parent, id, title) {
      var g = mk("div", CC + "group");
      g.setAttribute("role", "group"); g.setAttribute("aria-labelledby", id);
      var p = mk("p", CC + "gl", title); p.id = id;
      g.appendChild(p); parent.appendChild(g);
      return g;
    }
    function button(top, sub) {
      var b = document.createElement("button");
      b.type = "button"; b.setAttribute("aria-pressed", "false");
      b.appendChild(mk("span", CC + "b1", top));
      b.appendChild(mk("span", CC + "b2", sub));
      return b;
    }
    function buildControls() {
      if (!ctlEl) return;
      clear(ctlEl);
      ctl.cb = {}; ctl.fb = {};
      var g1 = group(ctlEl, CC + "g1", "Revenue case");
      var s1 = mk("div", "seg " + CC + "seg");
      caseKeys.forEach(function (k) {
        var b = button(cap1(k), money(cases[k].revenue_b) + " a year");
        b.addEventListener("click", function () { state.c = k; render(true); });
        ctl.cb[k] = b; s1.appendChild(b);
      });
      g1.appendChild(s1);
      ctl.cd = mk("p", CC + "desc"); g1.appendChild(ctl.cd);

      var g2 = group(ctlEl, CC + "g2", "How the build is paid for");
      var s2 = mk("div", "seg " + CC + "seg " + CC + "seg2");
      finKeys.forEach(function (k) {
        var nm = String(fins[k].label || k).split(":")[0];
        var b = button(nm, pct(fins[k].debt_share * 100) + " debt, " + pct(fins[k].rate * 100) + " interest");
        b.addEventListener("click", function () { state.f = k; render(true); });
        ctl.fb[k] = b; s2.appendChild(b);
      });
      g2.appendChild(s2);
      ctl.fd = mk("p", CC + "desc"); g2.appendChild(ctl.fd);
      g2.appendChild(mk("p", CC + "hint", "Hyperscalers are the biggest cloud companies. A neocloud is a newer company that rents out AI chips, such as CoreWeave or Nebius. Interest is charged on the share of the build paid for with debt."));

      var g3 = group(ctlEl, CC + "g3", "How long the chips last");
      var rg = mk("div", "range " + CC + "range");
      var lab = mk("label", "", "Chip life");
      lab.setAttribute("for", CC + "life");
      var inp = document.createElement("input");
      inp.type = "range"; inp.id = CC + "life"; inp.min = String(LIFE_MIN); inp.max = String(LIFE_MAX); inp.step = "1";
      inp.value = String(state.life);
      var out = document.createElement("output");
      out.setAttribute("for", CC + "life");
      inp.addEventListener("input", function () {
        var v = parseInt(inp.value, 10);
        if (v >= LIFE_MIN && v <= LIFE_MAX) { state.life = v; render(true); }
      });
      rg.appendChild(lab); rg.appendChild(inp); rg.appendChild(out);
      g3.appendChild(rg);
      g3.appendChild(mk("p", CC + "hint", "Shorter chip life means the cost of the chips is spread over fewer years, so the yearly depreciation charge is bigger."));
      ctl.li = inp; ctl.lo = out;
    }
    function syncControls() {
      if (!ctlEl || !ctl.cb) return;
      caseKeys.forEach(function (k) { ctl.cb[k].setAttribute("aria-pressed", k === state.c ? "true" : "false"); });
      finKeys.forEach(function (k) { ctl.fb[k].setAttribute("aria-pressed", k === state.f ? "true" : "false"); });
      var cs = cases[state.c];
      ctl.cd.textContent = String(cs.label || cap1(state.c)) + (cs.how ? ". " + cs.how + "." : ".");
      ctl.fd.textContent = String(fins[state.f].label || state.f) + ".";
      ctl.lo.textContent = state.life + " years";
      ctl.li.setAttribute("aria-valuetext", state.life + " years");
      ctl.li.value = String(state.life);
    }

    /* ---------- stats under the chart ---------- */
    function tile(parent, title) {
      var t = mk("div", CC + "stat");
      t.appendChild(mk("p", CC + "sk", title));
      var v = mk("p", CC + "sv"), d = mk("p", CC + "sd");
      t.appendChild(v); t.appendChild(d); parent.appendChild(t);
      return { v: v, d: d };
    }
    function buildStats() {
      if (!statEl) return;
      clear(statEl);
      var row = mk("div", CC + "tiles");
      stat.pay = tile(row, "Payback");
      stat.be = tile(row, "Breakeven revenue");
      stat.bi = tile(row, "Breakeven after interest");
      statEl.appendChild(row);
      stat.verdict = mk("p", CC + "verdict");
      stat.verdict.setAttribute("aria-live", "polite");
      statEl.appendChild(stat.verdict);
    }
    function syncStats(r) {
      if (!statEl || !stat.pay) return;
      stat.pay.v.textContent = r.payback != null ? HX.fmt(r.payback, "y1") : "Not paid back";
      stat.pay.d.textContent = r.payback != null
        ? "Years of cash profit needed to earn back the " + money(capAll) + " build cost."
        : "Cash profit is not positive, so the build cost is not earned back.";
      var be = breakeven(state.life, state.f, false), bi = breakeven(state.life, state.f, true);
      stat.be.v.textContent = be != null ? HX.fmt(be, "b2") + " a year" : "n/a";
      stat.be.d.textContent = "Revenue at which operating profit is zero, with chips lasting " + state.life + " years.";
      stat.bi.v.textContent = bi != null ? HX.fmt(bi, "b2") + " a year" : "n/a";
      stat.bi.d.textContent = "Revenue at which profit before tax is zero with " +
        String(fins[state.f].label || state.f).split(":")[0].toLowerCase() + " financing.";
      stat.verdict.textContent = "At " + HX.fmt(r.revenue, "b2") + " of revenue a year, this campus would make " +
        (r.ebit >= 0 ? "an operating profit of " : "an operating loss of ") + HX.fmt(Math.abs(r.ebit), "b2") +
        " and " + (r.pretax >= 0 ? "a profit of " : "a loss of ") + HX.fmt(Math.abs(r.pretax), "b2") +
        " before tax, after interest. Illustrative, not a forecast.";
    }

    /* ---------- chart ---------- */
    function draw() {
      W = width(host);
      var st = steps(calc(state.c, state.f, state.life));
      var px = geo.px, top = geo.top, rowH = geo.rowH;
      geo.ay = top + st.length * rowH + 2;
      var H = geo.ay + 28;
      x = d3.scaleLinear().range([px, W - px]);
      clear(host);
      var svg = svgIn(host, W, H);
      gridG = svg.append("g");
      var conG = svg.append("g");
      connRef = []; rowsRef = [];
      for (var i = 0; i < st.length - 1; i++) {
        connRef.push(conG.append("line").attr("class", CC + "conn"));
      }
      st.forEach(function (s, i2) {
        var yy = top + i2 * rowH;
        var rg = svg.append("g").attr("class", CC + "row");
        text(rg, CC + "lbl" + (s.total ? " " + CC + "tot" : ""), px, yy + 13, s.label);
        var val = text(rg, CC + "val", W - px, yy + 13, "", "end");
        var bar = rg.append("rect").attr("rx", 3).attr("x", px).attr("y", yy + 19).attr("height", 12).attr("width", 0);
        rowsRef.push({ g: rg, bar: bar, val: val, y: yy });
      });
    }

    function update(r, animate) {
      var st = steps(r), lvl = 0, lo = 0, i;
      for (i = 0; i < st.length; i++) {
        var s = st[i];
        if (s.total) { s.x0 = 0; s.x1 = s.v; lvl = s.v; }
        else { s.x0 = lvl; s.x1 = lvl + s.v; lvl = s.x1; }
        s.lvl = lvl;
        lo = Math.min(lo, s.x0, s.x1);
      }
      var dMin = lo >= -2 ? -2 : lo >= -5 ? -5 : lo >= -8 ? -8 : lo >= -12 ? -12 : Math.floor(lo);
      x.domain([dMin, dMax]);
      gridG.selectAll("*").remove();
      var px = geo.px, top = geo.top, ay = geo.ay;
      d3.range(Math.ceil(dMin / 5) * 5, dMax + 0.001, 5).forEach(function (t) {
        if (t !== 0) gridG.append("line").attr("class", CC + "grid").attr("x1", x(t)).attr("x2", x(t)).attr("y1", top).attr("y2", ay);
        var anchor = x(t) < px + 14 ? "start" : (x(t) > W - px - 14 ? "end" : "middle");
        text(gridG, CC + "tick", x(t), ay + 20, axisMoney(t), anchor);
      });
      gridG.append("line").attr("class", CC + "zero").attr("x1", x(0)).attr("x2", x(0)).attr("y1", top).attr("y2", ay);
      for (i = 0; i < st.length; i++) {
        var rr = rowsRef[i], t2 = st[i];
        if (!rr) continue;
        var xl = x(Math.min(t2.x0, t2.x1)), w = Math.abs(x(t2.x1) - x(t2.x0));
        if (w < 2 && Math.abs(t2.v) > 0) w = 2;
        rr.bar.attr("class", CC + "bar " + CC + "c-" + t2.c);
        var tgt = animate && DUR > 0 ? rr.bar.transition().duration(DUR) : rr.bar;
        tgt.attr("x", xl).attr("width", w);
        rr.val.text(HX.fmt(t2.v, "b2")).attr("class", CC + "val" + (t2.total && t2.v < 0 ? " " + CC + "neg" : ""));
        if (i < st.length - 1 && connRef[i] && rowsRef[i + 1]) {
          connRef[i].attr("x1", x(t2.lvl)).attr("x2", x(t2.lvl)).attr("y1", rr.y + 31).attr("y2", rowsRef[i + 1].y + 19);
        }
      }
      host.setAttribute("aria-label", "Illustrative waterfall for a 1 GW campus, " + state.c + " revenue case, " +
        state.f + " financing, chips lasting " + state.life + " years. " +
        st.map(function (q) { return q.label + " " + HX.fmt(q.v, "b2"); }).join(", ") + ".");
    }

    function render(user) {
      var r = calc(state.c, state.f, state.life);
      syncControls();
      update(r, !!user);
      syncStats(r);
    }

    buildControls();
    buildStats();
    draw();
    render(false);
    if (first) {
      first = false;
      HX.reveal(host, function (tl) {
        tl.from(rowsRef.map(function (q) { return q.g.node(); }), { opacity: 0, y: -8, duration: 0.5, stagger: 0.1 });
      });
    }
    HX.chartReady(host);
    HX.onResize(function () { run(function () { draw(); update(calc(state.c, state.f, state.life), false); }); });
  }

  /* ---------- start ---------- */
  HX.ready(function () {
    d3 = window.d3;
    if (!d3 || !d3.select || !d3.scaleLinear || !d3.range) return;
    run(initWave);
    run(initIntensity);
    run(initCampus);
    run(initDebt);
  });
})();
