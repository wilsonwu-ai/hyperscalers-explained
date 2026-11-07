/* Hyperscalers, explained: charts-b. Draws fig-backlog, fig-depreciation, fig-chain and fig-growth-margin with D3 v7.
   Colors come from CSS classes (docs/assets/css/charts-b.css) so dark mode needs no redraw.
   Every lookup is guarded; if anything fails the chart is removed and the fallback table stays visible. */
(function () {
  "use strict";
  if (!window.HX) { return; }
  var HX = window.HX;

  HX.ready(function () {
    var d3 = window.d3;
    if (!d3 || !d3.select || !d3.scaleLinear || !d3.ticks) { return; }

    /* ---------- helpers ---------- */
    function isNum(v) { return typeof v === "number" && isFinite(v); }
    function arr(path) { var v = HX.get(path); return Array.isArray(v) ? v : []; }
    function cw(node) {
      var w = node.clientWidth;
      if (!w && node.parentNode) { w = node.parentNode.clientWidth; }
      return Math.floor(w || 0);
    }
    /* rough text width in px for the sans font; errs on the wide side */
    function tw(s, px) { return String(s == null ? "" : s).length * px * 0.56; }
    function clear(node) { while (node.firstChild) { node.removeChild(node.firstChild); } }
    function mk(tag, cls, text, parent) {
      var n = document.createElement(tag);
      if (cls) { n.className = cls; }
      if (text != null) { n.textContent = text; }
      if (parent) { parent.appendChild(n); }
      return n;
    }
    function mkSvg(host, W, H) {
      return d3.select(host).append("svg")
        .attr("viewBox", "0 0 " + W + " " + H)
        .attr("width", W).attr("height", H)
        .attr("aria-hidden", "true").attr("focusable", "false");
    }
    function txt(g, x, y, s, cls, anchor) {
      var t = g.append("text").attr("x", x).attr("y", y).attr("class", cls).text(s);
      if (anchor) { t.attr("text-anchor", anchor); }
      return t;
    }
    function ln(g, x1, y1, x2, y2, cls) {
      return g.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2).attr("class", cls);
    }
    function mkLegend(parent, prefix, items) {
      var ul = mk("ul", "legend " + prefix + "-legend", null, parent);
      items.forEach(function (it) {
        var li = mk("li", null, null, ul);
        mk("span", "sw " + prefix + "-sw " + it.cls, null, li);
        li.appendChild(document.createTextNode(it.label));
      });
      return ul;
    }
    /* keeps a label of width w centred on x but inside [2, W - 2] */
    function fitAnchor(x, w, W) {
      if (x - w / 2 < 2) { return { x: 2, a: "start" }; }
      if (x + w / 2 > W - 2) { return { x: W - 2, a: "end" }; }
      return { x: x, a: "middle" };
    }
    function runDraw(host, fn) {
      try {
        clear(host);
        var ok = fn();
        if (ok === false) { clear(host); host.classList.remove("is-ready"); return false; }
        HX.chartReady(host);
        return true;
      } catch (e) {
        clear(host);
        host.classList.remove("is-ready");
        return false;
      }
    }
    /* draws now, animates once on first successful draw, redraws (final state, no tween) when the width changes */
    function setup(host, figSel, draw, animate) {
      var first = true;
      function go() {
        var ok = runDraw(host, draw);
        if (ok && first) {
          first = false;
          HX.reveal(figSel, function (tl, f) { try { animate(tl, f); } catch (e) { /* static state stays */ } });
        }
      }
      go();
      HX.onResize(go);
    }
    function pick(f, sel, tl, vars, at) {
      var list = f.querySelectorAll(sel);
      if (list.length) { tl.from(list, vars, at); }
    }

    /* ---------- fig-backlog ---------- */
    function backlog() {
      var host = document.getElementById("fig-backlog-chart");
      if (!host) { return; }
      var rows = arr("backlog.rows").filter(function (r) { return r && isNum(r.rpo_b) && r.rpo_b > 0; });
      if (!rows.length) { return; }

      function valText(v) { return Math.abs(v - Math.round(v)) < 1e-9 ? HX.fmt(v, "b0") : HX.fmt(v, "b1"); }
      function yearsText(r) {
        if (!isNum(r.years_of_revenue)) { return ""; }
        var basis = (r.run_rate_basis && r.run_rate_basis !== "company") ? r.run_rate_basis + " revenue" : "current revenue";
        return HX.fmt(r.years_of_revenue, "y1") + " of " + basis;
      }

      function draw() {
        var W = cw(host);
        if (W < 200) { return false; }
        var maxName = 0, maxYrs = 0;
        rows.forEach(function (r) {
          maxName = Math.max(maxName, tw(r.name, 14));
          maxYrs = Math.max(maxYrs, tw(yearsText(r), 13));
        });
        var stacked = maxName + maxYrs + 18 > W;
        var rowH = stacked ? 68 : 52;
        var gap = 36, top = 2;
        var xs = d3.scaleLinear()
          .domain([0, d3.max(rows, function (r) { return r.rpo_b; })])
          .range([0, Math.max(40, W - 66)]);

        var sepDone = false, y = top, pos = [];
        rows.forEach(function (r, i) {
          var neo = r.ticker === "CRWV" || r.ticker === "NBIS";
          var sep = false;
          if (neo && !sepDone && i > 0) { sepDone = true; sep = true; y += gap; }
          pos.push({ r: r, y: y, neo: neo, sep: sep });
          y += rowH;
        });
        var H = y + 4;
        var svg = mkSvg(host, W, H);
        var g = svg.append("g");
        ln(g, 0.5, 0, 0.5, H, "fig-backlog-axis");

        pos.forEach(function (p) {
          var r = p.r;
          if (p.sep) {
            ln(g, 0, p.y - gap + 8, W, p.y - gap + 8, "fig-backlog-rule");
            txt(g, 0, p.y - gap + 27, "Newer firms that rent out AI chips", "fig-backlog-muted");
          }
          var rg = g.append("g").attr("transform", "translate(0," + p.y + ")");
          txt(rg, 0, 14, r.name || "", "fig-backlog-name");
          var yr = yearsText(r);
          if (yr) {
            if (stacked) { txt(rg, 0, 55, yr, "fig-backlog-muted"); }
            else { txt(rg, W, 14, yr, "fig-backlog-muted", "end"); }
          }
          var bw = Math.max(2, xs(r.rpo_b));
          rg.append("rect")
            .attr("class", "fig-backlog-bar" + (p.neo ? " is-neo" : ""))
            .attr("x", 0).attr("y", 22).attr("width", bw).attr("height", 16).attr("rx", 2);
          txt(rg, bw + 6, 34.5, valText(r.rpo_b), "fig-backlog-val");
        });

        var parts = rows.map(function (r) { return r.name + " " + valText(r.rpo_b); });
        var big4 = HX.get("backlog.big4_total_b");
        host.setAttribute("aria-label",
          "Horizontal bar chart of signed backlog: " + parts.join(", ") + "." +
          (isNum(big4) ? " The four largest add up to " + HX.fmt(big4, "t2") + "." : ""));
        return true;
      }

      setup(host, "#fig-backlog", draw, function (tl, f) {
        pick(f, ".fig-backlog-bar", tl, { attr: { width: 0 }, duration: 0.8, stagger: 0.1 });
        pick(f, ".fig-backlog-val", tl, { opacity: 0, duration: 0.5, stagger: 0.1 }, 0.3);
      });
    }

    /* ---------- fig-depreciation ---------- */
    function depreciation() {
      var host = document.getElementById("fig-depreciation-chart");
      if (!host) { return; }
      var cols = arr("campus.life_sensitivity").filter(function (c) { return c && isNum(c.years) && isNum(c.it_depreciation); });
      var comps = arr("lives.rows").filter(function (r) { return r && isNum(r.low) && isNum(r.high); });
      if (!cols.length && !comps.length) { return; }

      function part1(W) {
        mk("p", "fig-depreciation-h", "The same campus under different chip lives", host);
        mkLegend(host, "fig-depreciation", [
          { cls: "is-bar", label: "Yearly chip cost (depreciation)" },
          { cls: "is-base", label: "Profit after all costs: today's GPU-cloud revenue" },
          { cls: "is-high", label: "Profit after all costs: busy and well priced" }
        ]);
        var gL = 46, gR = 2, padT = 8, plotH = 240;
        var band = (W - gL - gR) / cols.length;
        var bw = Math.max(16, Math.min(34, band * 0.5));
        var vals = [0];
        cols.forEach(function (c) {
          vals.push(c.it_depreciation);
          if (isNum(c.base_ebit)) { vals.push(c.base_ebit); }
          if (isNum(c.high_ebit)) { vals.push(c.high_ebit); }
        });
        var lo = d3.min(vals) - 0.9, hi = d3.max(vals) + 2.4;
        var ys = d3.scaleLinear().domain([lo, hi]).range([padT + plotH, padT]);
        var rowLife = padT + plotH + 20, rowBase = padT + plotH + 41, rowHigh = padT + plotH + 60;
        var H = padT + plotH + 70;
        var svg = mkSvg(host, W, H);
        var g = svg.append("g");

        d3.ticks(lo, hi, 4).forEach(function (t) {
          if (t === 0) { return; }
          var yy = ys(t);
          ln(g, gL, yy, W - gR, yy, "fig-depreciation-grid");
          txt(g, gL - 8, yy, HX.fmt(t, "b0"), "fig-depreciation-tick", "end").attr("dy", ".32em");
        });

        cols.forEach(function (c, i) {
          var cx = gL + band * (i + 0.5);
          var top = ys(c.it_depreciation), y0 = ys(0);
          g.append("rect").attr("class", "fig-depreciation-bar")
            .attr("x", cx - bw / 2).attr("y", top).attr("width", bw).attr("height", Math.max(1, y0 - top)).attr("rx", 2);
          txt(g, cx, top - 6, HX.fmt(c.it_depreciation, "b1"), "fig-depreciation-val", "middle");
        });

        ln(g, gL, ys(0), W - gR, ys(0), "fig-depreciation-zero");
        txt(g, gL - 8, ys(0), "$0", "fig-depreciation-tick", "end").attr("dy", ".32em");

        cols.forEach(function (c, i) {
          var cx = gL + band * (i + 0.5);
          if (isNum(c.base_ebit)) {
            g.append("circle").attr("class", "fig-depreciation-dot-base").attr("cx", cx).attr("cy", ys(c.base_ebit)).attr("r", 6);
          }
          if (isNum(c.high_ebit)) {
            g.append("circle").attr("class", "fig-depreciation-dot-high").attr("cx", cx).attr("cy", ys(c.high_ebit)).attr("r", 6);
          }
          txt(g, cx, rowLife, c.years + " years", "fig-depreciation-life", "middle");
          if (isNum(c.base_ebit)) { txt(g, cx, rowBase, HX.fmt(c.base_ebit, "b1"), "fig-depreciation-v-base", "middle"); }
          if (isNum(c.high_ebit)) { txt(g, cx, rowHigh, HX.fmt(c.high_ebit, "b1"), "fig-depreciation-v-high", "middle"); }
        });

        txt(g, 0, rowLife, "Life", "fig-depreciation-muted");
        g.append("circle").attr("class", "fig-depreciation-dot-base").attr("cx", 6).attr("cy", rowBase - 4).attr("r", 4.5);
        txt(g, 15, rowBase, "Base", "fig-depreciation-muted");
        g.append("circle").attr("class", "fig-depreciation-dot-high").attr("cx", 6).attr("cy", rowHigh - 4).attr("r", 4.5);
        txt(g, 15, rowHigh, "Busy", "fig-depreciation-muted");
      }

      function part2(W) {
        mk("p", "fig-depreciation-h", "How long companies say their servers last", host);
        var dLo = Math.floor(d3.min(comps, function (c) { return c.low; }));
        var dHi = Math.ceil(d3.max(comps, function (c) { return c.high; })) + 0.5;
        var xs = d3.scaleLinear().domain([dLo, dHi]).range([10, W - 10]);
        var maxName = 0, maxYrs = 0;
        comps.forEach(function (c) {
          maxName = Math.max(maxName, tw(c.name, 14));
          maxYrs = Math.max(maxYrs, tw(c.years, 13));
        });
        var stacked = maxName + maxYrs + 18 > W;
        var rowH = stacked ? 62 : 46, top = 24;
        var H = top + comps.length * rowH + 4;
        var svg = mkSvg(host, W, H);
        var g = svg.append("g");
        var ticks = d3.range(dLo, Math.floor(dHi) + 1);
        ticks.forEach(function (t, i) {
          var xx = xs(t);
          ln(g, xx, 18, xx, H - 2, "fig-depreciation-grid");
          txt(g, xx, 12, i === ticks.length - 1 ? t + " years" : String(t), "fig-depreciation-tick", "middle");
        });
        comps.forEach(function (c, i) {
          var ry = top + i * rowH, yy = ry + 30;
          txt(g, 0, ry + 14, c.name || "", "fig-depreciation-name");
          if (c.years) {
            if (stacked) { txt(g, 0, ry + 52, String(c.years), "fig-depreciation-muted fig-depreciation-halo"); }
            else { txt(g, W, ry + 14, String(c.years), "fig-depreciation-muted fig-depreciation-halo", "end"); }
          }
          if (c.high > c.low) { ln(g, xs(c.low), yy, xs(c.high), yy, "fig-depreciation-range"); }
          g.append("circle").attr("class", "fig-depreciation-pdot").attr("cx", xs(c.low)).attr("cy", yy).attr("r", 5.5);
          if (c.high > c.low) {
            g.append("circle").attr("class", "fig-depreciation-pdot").attr("cx", xs(c.high)).attr("cy", yy).attr("r", 5.5);
          }
        });
        var meta = comps.filter(function (c) { return c.name === "Meta"; })[0];
        var saving = HX.get("lives.meta_2025_saving_b");
        if (meta && isNum(saving)) {
          mk("p", "fig-depreciation-note",
            "Longer lives lower the expense: Meta's move to " + meta.low + " years cut its 2025 depreciation by " +
            HX.fmt(saving, "b2") + " (Meta's 10-K for 2025).", host);
        }
      }

      function draw() {
        var W = cw(host);
        if (W < 220) { return false; }
        if (cols.length) { part1(W); }
        if (comps.length) { part2(W); }

        var a = [];
        if (cols.length) {
          var f = cols[0], l = cols[cols.length - 1];
          a.push("Chart one: if chips are written off over " + f.years + " years, the yearly chip cost is " +
            HX.fmt(f.it_depreciation, "b1") +
            (isNum(f.high_ebit) ? " and even a busy, well-priced campus has an operating profit of " + HX.fmt(f.high_ebit, "b1") : "") +
            "; over " + l.years + " years the cost falls to " + HX.fmt(l.it_depreciation, "b1") +
            (isNum(l.high_ebit) ? " and the busy campus earns " + HX.fmt(l.high_ebit, "b1") : "") + ".");
        }
        if (comps.length) {
          a.push("Chart two: assumed server life in years: " +
            comps.map(function (c) { return c.name + " " + c.years; }).join(", ") + ".");
        }
        host.setAttribute("aria-label", a.join(" "));
        return true;
      }

      setup(host, "#fig-depreciation", draw, function (tl, f) {
        pick(f, ".fig-depreciation-bar", tl, { opacity: 0, y: 14, duration: 0.7, stagger: 0.1 });
        pick(f, ".fig-depreciation-dot-base, .fig-depreciation-dot-high", tl, { opacity: 0, duration: 0.5, stagger: 0.08 }, 0.5);
        pick(f, ".fig-depreciation-range, .fig-depreciation-pdot", tl, { opacity: 0, duration: 0.5, stagger: 0.08 }, 0.9);
      });
    }

    /* ---------- fig-chain ---------- */
    function chain() {
      var host = document.getElementById("fig-chain-chart");
      if (!host) { return; }
      var rows = arr("chain.rows")
        .filter(function (r) { return r && isNum(r.op_margin); })
        .slice()
        .sort(function (a, b) { return b.op_margin - a.op_margin; });
      if (!rows.length) { return; }
      var LAYERS = [["chips", "Chips"], ["compute", "Cloud"], ["power", "Power and cooling gear"], ["buildings", "Data center landlords"]];

      function splitName(n) {
        var m = /^(.*?)\s*\((.*)\)\s*$/.exec(n || "");
        return m ? { main: m[1], desc: m[2] } : { main: n || "", desc: "" };
      }

      function draw() {
        var W = cw(host);
        if (W < 220) { return false; }
        var present = {};
        rows.forEach(function (r) { if (r.layer) { present[r.layer] = true; } });
        var items = [];
        LAYERS.forEach(function (l) { if (present[l[0]]) { items.push({ cls: "is-" + l[0], label: l[1] }); } });
        if (rows.some(function (r) { return r.op_margin < 0; })) { items.push({ cls: "is-loss", label: "Loss-making" }); }
        mkLegend(host, "fig-chain", items);

        var twoLine = rows.some(function (r) { return tw(r.name, 14) > W - 8; });
        var rowH = twoLine ? 68 : 52, barY = twoLine ? 40 : 22;
        var padR = 54, plotW = Math.max(60, W - padR);
        var vmin = Math.min(0, d3.min(rows, function (r) { return r.op_margin; }));
        var vmax = Math.max(0, d3.max(rows, function (r) { return r.op_margin; }));
        var xs = d3.scaleLinear().domain([vmin, vmax === vmin ? vmin + 1 : vmax]).range([0, plotW]);
        var x0 = xs(0);
        var H = rows.length * rowH + 6;
        var svg = mkSvg(host, W, H);
        var g = svg.append("g");

        rows.forEach(function (r, i) {
          var rg = g.append("g").attr("transform", "translate(0," + (i * rowH + 2) + ")");
          var nm = splitName(r.name);
          var t = rg.append("text").attr("x", 0).attr("y", 14).attr("class", "fig-chain-name");
          t.append("tspan").attr("class", "fig-chain-main").text(nm.main);
          if (nm.desc) {
            if (twoLine) { txt(rg, 0, 31, nm.desc, "fig-chain-muted"); }
            else { t.append("tspan").attr("class", "fig-chain-muted").attr("dx", 6).text("(" + nm.desc + ")"); }
          }
          var v = r.op_margin, neg = v < 0;
          var layer = String(r.layer || "").replace(/[^a-z]/g, "");
          var bx = Math.min(x0, xs(v)), bw = Math.max(2, Math.abs(xs(v) - x0));
          rg.append("rect")
            .attr("class", "fig-chain-bar " + (neg ? "is-loss" : "is-" + layer) + (neg ? " is-neg" : ""))
            .attr("x", bx).attr("y", barY).attr("width", bw).attr("height", 16).attr("rx", 2);
          txt(rg, neg ? x0 + 6 : xs(v) + 6, barY + 12.5, HX.fmt(v, "p1"), "fig-chain-val" + (neg ? " is-loss" : ""));
        });
        ln(g, x0 + 0.5, 0, x0 + 0.5, H, "fig-chain-zero");

        mk("p", "fig-chain-note",
          "Read down the chart: the further a business sits from the chips, the thinner its margin, " +
          "except the full-service clouds (AWS and Google Cloud), which sell software and services on top.", host);

        host.setAttribute("aria-label",
          "Horizontal bar chart of operating margin, highest first: " +
          rows.map(function (r) { return splitName(r.name).main + " " + HX.fmt(r.op_margin, "p1"); }).join(", ") + ".");
        return true;
      }

      setup(host, "#fig-chain", draw, function (tl, f) {
        pick(f, ".fig-chain-bar:not(.is-neg)", tl, { attr: { width: 0 }, duration: 0.8, stagger: 0.1 });
        pick(f, ".fig-chain-bar.is-neg", tl, { opacity: 0, duration: 0.6, stagger: 0.1 }, 0.3);
        pick(f, ".fig-chain-val", tl, { opacity: 0, duration: 0.5, stagger: 0.1 }, 0.3);
      });
    }

    /* ---------- fig-growth-margin ---------- */
    function growthMargin() {
      var host = document.getElementById("fig-growth-margin-chart");
      if (!host) { return; }
      var pts = arr("growth_margin.points").filter(function (p) { return p && isNum(p.growth_pct) && isNum(p.op_margin_pct); });
      var nom = arr("growth_margin.no_margin").filter(function (p) { return p && isNum(p.growth_pct); });
      if (!pts.length) { return; }
      var CAP = 200;

      function draw() {
        var W = cw(host);
        if (W < 220) { return false; }
        var L = 44, R = 18, T = 26, plotW = W - L - R;
        var plotH = Math.round(Math.max(240, Math.min(320, W * 0.85)));
        var yv = pts.map(function (p) { return p.op_margin_pct; });
        var yLo = Math.min(-35, d3.min(yv) - 8), yHi = Math.max(70, d3.max(yv) + 8);
        var xs = d3.scaleLinear().domain([0, CAP]).range([L, L + plotW]);
        var ys = d3.scaleLinear().domain([yLo, yHi]).range([T + plotH, T]);
        var bottom = T + plotH;
        var stripTop = bottom + 56;
        var H = stripTop + (nom.length ? 78 : 0);
        var svg = mkSvg(host, W, H);
        var g = svg.append("g");

        txt(g, 0, 12, "Operating margin", "fig-growth-margin-muted");
        d3.ticks(yLo, yHi, 4).forEach(function (t) {
          var yy = ys(t);
          ln(g, L, yy, L + plotW, yy, t === 0 ? "fig-growth-margin-zero" : "fig-growth-margin-grid");
          txt(g, L - 8, yy, HX.fmt(t, "p0"), "fig-growth-margin-tick", "end").attr("dy", ".32em");
        });
        txt(g, L + 6, ys(0) - 6, "Profit", "fig-growth-margin-muted");
        txt(g, L + 6, ys(0) + 17, "Loss", "fig-growth-margin-muted");

        [0, 50, 100, 150, 200].forEach(function (t) {
          var xx = xs(t);
          ln(g, xx, bottom, xx, bottom + 5, "fig-growth-margin-zero");
          txt(g, xx, bottom + 21, t + (t === CAP ? "%+" : "%"), "fig-growth-margin-tick", "middle");
        });
        ln(g, xs(CAP), T, xs(CAP), bottom, "fig-growth-margin-edge");
        txt(g, L + plotW / 2, bottom + 40, "Revenue growth, year on year", "fig-growth-margin-muted", "middle");

        pts.forEach(function (p) {
          var clipped = p.growth_pct > CAP;
          var px = xs(Math.min(p.growth_pct, CAP)), py = ys(p.op_margin_pct);
          var supplier = p.kind === "supplier";
          var kindCls = supplier ? "is-supplier" : (p.op_margin_pct < 0 ? "is-loss" : "is-cloud");
          var m;
          if (supplier) { m = g.append("path").attr("d", "M0,-9 L9,0 L0,9 L-9,0 Z"); }
          else if (clipped) { m = g.append("path").attr("d", "M-7,-7 L8,0 L-7,7 Z"); }
          else { m = g.append("circle").attr("r", 7); }
          m.attr("class", "fig-growth-margin-pt " + kindCls).attr("transform", "translate(" + px + "," + py + ")");

          var line1 = (p.name || "") + (clipped ? " " + HX.fmt(p.growth_pct, "p0") : "");
          var w = tw(line1, 14);
          var off = supplier ? 14 : 12;
          var left = clipped || (px + off + w > W - 2);
          var lx = left ? px - off : px + off, anchor = left ? "end" : "start";
          if (clipped) {
            txt(g, lx, py - 1, line1, "fig-growth-margin-lbl", anchor);
            txt(g, lx, py + 15, "axis stops at " + CAP + "%", "fig-growth-margin-lbl is-note", anchor);
          } else {
            txt(g, lx, py + 5, line1, "fig-growth-margin-lbl", anchor);
          }
        });

        if (nom.length) {
          txt(g, 0, stripTop, "No margin reported for these cloud units", "fig-growth-margin-muted");
          var lineY = stripTop + 44;
          ln(g, L, lineY, L + plotW, lineY, "fig-growth-margin-grid");
          nom.forEach(function (p, i) {
            var px = xs(Math.min(p.growth_pct, CAP));
            g.append("circle").attr("class", "fig-growth-margin-ring").attr("cx", px).attr("cy", lineY).attr("r", 6);
            var label = (p.name || "") + " " + HX.fmt(p.growth_pct, "p0");
            var fa = fitAnchor(px, tw(label, 14), W);
            txt(g, fa.x, i % 2 === 0 ? lineY - 14 : lineY + 24, label, "fig-growth-margin-lbl", fa.a);
          });
        }

        host.setAttribute("aria-label",
          "Scatter chart of revenue growth against operating margin: " +
          pts.map(function (p) {
            return p.name + " grew " + HX.fmt(p.growth_pct, "p0") + " with a margin of " + HX.fmt(p.op_margin_pct, "p1");
          }).join("; ") + "." +
          (nom.length ? " Growth only, margin not reported: " +
            nom.map(function (p) { return p.name + " " + HX.fmt(p.growth_pct, "p0"); }).join(", ") + "." : ""));
        return true;
      }

      setup(host, "#fig-growth-margin", draw, function (tl, f) {
        pick(f, ".fig-growth-margin-pt, .fig-growth-margin-ring", tl, { opacity: 0, duration: 0.6, stagger: 0.1 });
        pick(f, ".fig-growth-margin-lbl", tl, { opacity: 0, duration: 0.5, stagger: 0.08 }, 0.4);
      });
    }

    [backlog, depreciation, chain, growthMargin].forEach(function (f) { try { f(); } catch (e) { /* the fallback table stays visible */ } });
  });
})();
