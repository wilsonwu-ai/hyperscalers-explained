/* Shared helpers for every figure script (window.HX). Loaded after data.js and GSAP, before the figure scripts.
   The number formats here match build.py exactly, so text filled at build time and text updated in the browser agree. */
(function () {
  "use strict";
  var D = window.SITE_DATA || {};
  var reduced = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  if (window.gsap && window.ScrollTrigger) window.gsap.registerPlugin(window.ScrollTrigger);

  /* get("campus.cases.base.revenue_b"), get("cloud_units.rows[name=AWS].op_margin_pct"), get("backlog.rows[0].rpo_b") */
  function get(path, root) {
    var cur = root || D;
    var parts = String(path).match(/[^.[\]]+|\[[^\]]+\]/g) || [];
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      var p = parts[i];
      if (p.charAt(0) === "[") {
        var inner = p.slice(1, -1), eq = inner.indexOf("=");
        if (eq > 0) {
          var k = inner.slice(0, eq), v = inner.slice(eq + 1);
          cur = (cur || []).filter(function (o) { return o && String(o[k]) === v; })[0];
        } else { cur = cur[+inner]; }
      } else { cur = cur[p]; }
    }
    return cur;
  }

  function loc(a, d) { return a.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); }

  /* Formats: b0 b1 b2 ($ billions), t2 ($B shown as trillions), m0 ($ millions), p0 p1 (percent), x1 (times),
     n0 (count), n2 (two decimals), y1 (years), raw. Negative numbers get a leading hyphen-minus. */
  function fmt(v, f) {
    if (v == null) return "";
    if (f === "raw" || isNaN(+v)) return String(v);
    var n = +v, neg = n < 0, a = Math.abs(n), s;
    switch (f) {
      case "b0": s = "$" + loc(a, 0) + "B"; break;
      case "b1": s = "$" + loc(a, 1) + "B"; break;
      case "b2": s = "$" + loc(a, 2) + "B"; break;
      case "t2": s = "$" + loc(a / 1000, 2) + "T"; break;
      case "m0": s = "$" + loc(a, 0) + "M"; break;
      case "p0": s = Math.floor(a + 0.5) + "%"; break;
      case "p1": s = a.toFixed(1) + "%"; break;
      case "x1": s = a.toFixed(1) + "x"; break;
      case "n0": s = loc(a, 0); break;
      case "n2": s = loc(a, 2); break;
      case "y1": s = a.toFixed(1) + " years"; break;
      default: return String(v);
    }
    return (neg ? "-" : "") + s;
  }

  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue("--" + name).trim(); }

  /* reveal(target, function (tl, el) { tl.from(...) }, {end: fn})
     Builds a paused GSAP timeline and plays it once when the figure scrolls into view.
     Without GSAP, or with reduced motion, nothing animates and opts.end(el) runs (the static state is the end state). */
  function reveal(target, build, opts) {
    var el = typeof target === "string" ? document.querySelector(target) : target;
    if (!el) return null;
    if (!window.gsap || reduced) { if (opts && opts.end) opts.end(el); return null; }
    var tl = window.gsap.timeline({ paused: true, defaults: { ease: "power2.out", duration: 0.7 } });
    build(tl, el);
    if (window.ScrollTrigger) {
      window.ScrollTrigger.create({ trigger: el, start: "top 80%", once: true, onEnter: function () { tl.play(); } });
    } else { tl.play(); }
    return tl;
  }

  /* chartReady(el): marks a .chart as drawn so its fallback table (the next sibling) becomes screen-reader only */
  function chartReady(el) { if (el) el.classList.add("is-ready"); }

  function ready(fn) {
    if (document.readyState !== "loading") fn(); else document.addEventListener("DOMContentLoaded", fn);
  }

  /* onResize(fn): debounced, width changes only (ignores mobile URL-bar height changes) */
  function onResize(fn) {
    var w = window.innerWidth, t;
    window.addEventListener("resize", function () {
      if (window.innerWidth === w) return;
      w = window.innerWidth; clearTimeout(t); t = setTimeout(fn, 150);
    });
  }

  /* Deep links: with smooth scrolling on, the browser animates a #hash landing, and ScrollTrigger's refresh on load
     can stop that animation part way down. Once everything has loaded, land on the target again, instantly. */
  window.addEventListener("load", function () {
    var id = decodeURIComponent(location.hash.slice(1));
    var target = id && document.getElementById(id);
    if (!target) return;
    setTimeout(function () {
      var root = document.documentElement, prev = root.style.scrollBehavior;
      root.style.scrollBehavior = "auto";
      target.scrollIntoView({ block: "start" });
      root.style.scrollBehavior = prev;
    }, 250);
  });

  window.HX = { data: D, get: get, fmt: fmt, css: css, reduced: reduced, reveal: reveal, chartReady: chartReady,
                ready: ready, onResize: onResize };
})();
