/* Hyperscalers, explained: diagrams-b (fig-cost-stack, fig-forces, fig-scenarios, fig-tam).
   The static HTML is the finished picture. This file only refreshes the hooked numbers from site data,
   plays a short reveal on scroll (via HX.reveal, skipped for reduced motion) and runs the scenario taps.
   Every block is guarded: a missing element or data key means the block quietly does nothing. */
(function () {
  "use strict";

  if (!window.HX || typeof window.HX.ready !== "function") return;
  var HX = window.HX;

  function one(sel, root) {
    try { return (root || document).querySelector(sel); } catch (e) { return null; }
  }
  function all(sel, root) {
    try { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); } catch (e) { return []; }
  }
  function safe(fn) {
    try { fn(); } catch (e) { /* one figure must never break the others */ }
  }

  /* Same job as build.py: put HX.fmt(HX.get(k), f) into every hooked element. Missing data leaves the static text. */
  function refreshHooks(root) {
    all("[data-k]", root).forEach(function (el) {
      var v = HX.get(el.getAttribute("data-k"));
      if (v === undefined || v === null) return;
      el.textContent = HX.fmt(v, el.getAttribute("data-f") || "raw");
    });
  }

  /* Grow an SVG shape upward from its own bottom edge. Falls back to a fade if the box cannot be measured. */
  function growUp(tl, el, at) {
    if (!el) return;
    var bb = null;
    try { bb = el.getBBox(); } catch (e) { bb = null; }
    if (bb && bb.height > 0) {
      tl.from(el, { scaleY: 0, svgOrigin: (bb.x + bb.width / 2) + " " + (bb.y + bb.height), duration: 0.8 }, at);
    } else {
      tl.from(el, { opacity: 0, duration: 0.6 }, at);
    }
  }

  /* ---------- fig-cost-stack ---------- */
  function initCostStack() {
    var root = one("#fig-cost-stack");
    if (!root) return;
    refreshHooks(root);
    HX.reveal(root, function (tl, el) {
      growUp(tl, one(".fig-cost-stack-fac", el), 0);
      growUp(tl, one(".fig-cost-stack-it", el), 0.1);
      var lt = all(".fig-cost-stack-lt, .fig-cost-stack-total, .fig-cost-stack-heads", el);
      if (lt.length) tl.from(lt, { opacity: 0, duration: 0.6, stagger: 0.1 }, 0.5);
      var arr = one(".fig-cost-stack-arr", el);
      if (arr) tl.from(arr, { opacity: 0, x: -10, duration: 0.7 }, 1.0);
      growUp(tl, one(".fig-cost-stack-dep", el), 1.2);
      growUp(tl, one(".fig-cost-stack-run", el), 1.3);
      growUp(tl, one(".fig-cost-stack-pow", el), 1.4);
      var labs = all(".fig-cost-stack-lab", el);
      if (labs.length) tl.from(labs, { opacity: 0, x: -6, duration: 0.6, stagger: 0.1 }, 1.9);
    });
  }

  /* ---------- fig-forces ---------- */
  function initForces() {
    var root = one("#fig-forces");
    if (!root) return;
    refreshHooks(root);
    var words = { 1: "very low", 2: "low", 3: "medium", 4: "high", 5: "very high" };
    all(".fig-forces-card", root).forEach(function (card) {
      var lvl = Number(HX.get("forces[" + card.getAttribute("data-i") + "].level"));
      if (!lvl || isNaN(lvl)) return;
      all(".fig-forces-dot", card).forEach(function (d, j) {
        if (j < lvl) d.classList.add("is-on"); else d.classList.remove("is-on");
      });
      var w = one(".fig-forces-word", card);
      if (w && words[lvl]) w.textContent = words[lvl];
    });
    HX.reveal(root, function (tl, el) {
      var cards = all(".fig-forces-card", el);
      if (cards.length) tl.from(cards, { opacity: 0, y: 14, duration: 0.7, stagger: 0.1 });
      var dots = all(".fig-forces-dot.is-on", el);
      if (dots.length) tl.from(dots, { scale: 0, duration: 0.4, stagger: 0.08 }, "-=0.3");
    });
  }

  /* ---------- fig-scenarios ---------- */
  function initScenarios() {
    var root = one("#fig-scenarios");
    if (!root) return;
    var cells = all(".fig-scenarios-cell", root);
    var live = one(".fig-scenarios-live", root);
    var hint = one(".fig-scenarios-hint", root);

    function say(text) { if (live) live.textContent = text || ""; }
    function close(c) {
      c.classList.remove("is-open");
      c.setAttribute("aria-expanded", "false");
    }
    function toggle(c) {
      var wasOpen = c.classList.contains("is-open");
      cells.forEach(close);
      if (wasOpen) { say(""); return; }
      c.classList.add("is-open");
      c.setAttribute("aria-expanded", "true");
      var name = one(".fig-scenarios-name", c);
      var watch = one(".fig-scenarios-watch", c);
      say((name ? name.textContent : "") + ". " + (watch ? watch.textContent : ""));
    }

    if (cells.length) {
      root.classList.add("is-interactive");
      if (hint) hint.hidden = false;
      cells.forEach(function (c) {
        c.setAttribute("aria-expanded", "false");
        c.addEventListener("click", function () { toggle(c); });
      });
    }

    HX.reveal(root, function (tl, el) {
      var heads = all(".fig-scenarios-colhead, .fig-scenarios-rowhead", el);
      var ax = one(".fig-scenarios-axis-x", el);
      var ay = one(".fig-scenarios-axis-y", el);
      if (heads.length) tl.from(heads, { opacity: 0, duration: 0.5, stagger: 0.08 }, 0);
      if (ax) tl.from(ax, { scaleX: 0, transformOrigin: "0% 50%", duration: 0.7 }, 0);
      if (ay) tl.from(ay, { scaleY: 0, transformOrigin: "50% 100%", duration: 0.7 }, 0);
      var cs = all(".fig-scenarios-cell", el);
      if (cs.length) tl.from(cs, { opacity: 0, y: 12, duration: 0.7, stagger: 0.12 }, "-=0.2");
    });
  }

  /* ---------- fig-tam ---------- */
  function initTam() {
    var root = one("#fig-tam");
    if (!root) return;
    refreshHooks(root);
    HX.reveal(root, function (tl, el) {
      /* every circle touches the same bottom point (84, 176), so they grow from there */
      var circles = all(".fig-tam-circle", el);
      if (circles.length) tl.from(circles, { scale: 0, svgOrigin: "84 176", duration: 0.9, stagger: 0.25 });
      var tags = all(".fig-tam-tag", el);
      if (tags.length) tl.from(tags, { opacity: 0, x: -6, duration: 0.6, stagger: 0.12 }, "-=0.4");
      var rows = all(".fig-tam-legend li", el);
      if (rows.length) tl.from(rows, { opacity: 0, y: 8, duration: 0.6, stagger: 0.1 }, "-=0.3");
    });
  }

  HX.ready(function () {
    safe(initCostStack);
    safe(initForces);
    safe(initScenarios);
    safe(initTam);
  });
})();
