/* Diagrams A: fig-hero, fig-situation, fig-garage, fig-stack, fig-revenue-tree.
   The HTML already holds the finished picture, so the page reads correctly with no script.
   Scroll reveals animate from a hidden state to that picture. With reduced motion, or without GSAP,
   HX.reveal does nothing and the static state stays. Nothing in here may throw. */
(function () {
  "use strict";

  var HX = window.HX;
  if (!HX || typeof HX.ready !== "function") { return; }
  var doc = document;

  function q(sel, root) {
    try { return (root || doc).querySelector(sel); } catch (e) { return null; }
  }
  function qa(sel, root) {
    try { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); } catch (e) { return []; }
  }
  function safe(fn) {
    try { fn(); } catch (e) { /* a broken figure must never break the page */ }
  }
  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }

  /* tl.from(...) on every match of sel inside root, skipped quietly when nothing matches */
  function addFrom(tl, root, sel, vars, pos) {
    var t = qa(sel, root);
    if (tl && t.length) { tl.from(t, vars, pos); }
  }

  /* ---------- fig-hero ---------- */
  function initHero() {
    var root = q("#fig-hero");
    if (!root) { return; }

    /* the campus assembles when it scrolls into view; the idle blinking and drifting is CSS only */
    HX.reveal(root, function (tl) {
      addFrom(tl, root, ".fig-hero-pylon-g", { opacity: 0, y: 8, duration: 0.7 }, 0);
      addFrom(tl, root, ".fig-hero-wiregrp", { opacity: 0, duration: 0.6 }, 0.3);
      addFrom(tl, root, ".fig-hero-bld-g", { opacity: 0, y: 10, duration: 0.7 }, 0.2);
      addFrom(tl, root, ".fig-hero-rk", { opacity: 0, y: 8, duration: 0.6, stagger: 0.08 }, 0.5);
      addFrom(tl, root, ".fig-hero-pipe", { attr: { x2: 226 }, duration: 0.8 }, 1.0);
      addFrom(tl, root, ".fig-hero-arrow", { opacity: 0, duration: 0.4 }, 1.6);
      addFrom(tl, root, ".fig-hero-coins", { opacity: 0, duration: 0.6 }, 1.2);
      addFrom(tl, root, ".fig-hero-lab", { opacity: 0, duration: 0.6, stagger: 0.1 }, 0.6);
    });

    /* count-up on load: the hero is visible at once. The markup already shows the final numbers. */
    var g = window.gsap;
    if (HX.reduced || !g || typeof g.to !== "function") { return; }
    qa("[data-k]", root).forEach(function (span) {
      var k = span.getAttribute("data-k");
      var f = span.getAttribute("data-f") || "raw";
      var target = HX.get(k);
      if (typeof target !== "number" || !isFinite(target)) { return; }
      var finalText = HX.fmt(target, f);
      var o = { v: 0 };
      span.textContent = HX.fmt(0, f);
      g.to(o, {
        v: target,
        duration: 1.8,
        delay: 0.2,
        ease: "power2.out",
        onUpdate: function () { span.textContent = HX.fmt(o.v, f); },
        onComplete: function () { span.textContent = finalText; }
      });
      /* safety net: if the tab was hidden and the tween stalled, still end on the true number */
      window.setTimeout(function () { span.textContent = finalText; }, 6000);
    });
  }

  /* ---------- fig-situation ---------- */
  function initSituation() {
    var root = q("#fig-situation");
    if (!root) { return; }
    HX.reveal(root, function (tl) {
      addFrom(tl, root, ".fig-sit-card", { opacity: 0, y: 14, duration: 0.7, stagger: 0.1 }, 0);
      addFrom(tl, root, ".fig-sit-hot", { opacity: 0.4, scale: 0.94, duration: 0.6, stagger: 0.12 }, 0.5);
      addFrom(tl, root, ".fig-sit-go", { opacity: 0, y: -8, duration: 0.7 }, 0.9);
    });
  }

  /* ---------- fig-garage ---------- */
  function initGarage() {
    var root = q("#fig-garage");
    if (!root) { return; }
    HX.reveal(root, function (tl) {
      var needle = q(".fig-garage-needle", root);
      var origin = "160 282";
      addFrom(tl, root, ".fig-garage-a", { opacity: 0, y: 12, duration: 0.7 }, 0);
      addFrom(tl, root, ".fig-garage-or", { opacity: 0, duration: 0.4 }, 0.5);
      addFrom(tl, root, ".fig-garage-b", { opacity: 0, y: 12, duration: 0.7 }, 0.7);
      addFrom(tl, root, ".fig-garage-arc-on", { opacity: 0, duration: 0.8 }, 1.0);
      if (needle) {
        /* the needle sweeps in from the left, settles, then keeps a gentle tick */
        tl.from(needle, { rotation: -80, svgOrigin: origin, duration: 1.2 }, 1.0);
        tl.to(needle, { rotation: 5, svgOrigin: origin, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: -1 }, 2.4);
      }
      /* the hour cells fill one by one, like a meter counting */
      addFrom(tl, root, ".fig-garage-cell-on", { opacity: 0, duration: 0.3, stagger: 0.18 }, 1.2);
    });
  }

  /* ---------- fig-stack ---------- */
  function initStack() {
    var root = q("#fig-stack");
    if (!root) { return; }
    var pairs = [];
    qa(".fig-stack-btn", root).forEach(function (btn) {
      var id = btn.getAttribute("aria-controls");
      var detail = id ? doc.getElementById(id) : null;
      if (detail) { pairs.push({ btn: btn, detail: detail }); }
    });
    if (!pairs.length) { return; }

    function setOpen(pair, open) {
      pair.btn.setAttribute("aria-expanded", open ? "true" : "false");
      pair.detail.hidden = !open;
    }
    function openOnly(pair) {
      pairs.forEach(function (p) { setOpen(p, p === pair); });
    }

    /* with script, the explanations start folded; without it they all stay visible */
    root.classList.add("fig-stack-js");
    pairs.forEach(function (p) { setOpen(p, false); });

    pairs.forEach(function (pair) {
      pair.btn.addEventListener("click", function () {
        if (pair.detail.hidden) { openOnly(pair); } else { setOpen(pair, false); }
      });
      /* keyboard users: arriving on a layer reveals it (tap and mouse use the click above) */
      pair.btn.addEventListener("focus", function () {
        var kb = false;
        try { kb = pair.btn.matches(":focus-visible"); } catch (e) { kb = false; }
        if (kb && pair.detail.hidden) { openOnly(pair); }
      });
    });

    /* layers build up from the bottom: the list is in bottom-to-top order */
    HX.reveal(root, function (tl) {
      addFrom(tl, root, ".fig-stack-layer", { opacity: 0, y: 24, duration: 0.7, stagger: 0.1 }, 0);
    });
  }

  /* ---------- fig-revenue-tree ---------- */
  function initRevenue() {
    var root = q("#fig-revenue-tree");
    if (!root) { return; }
    var nodes = qa(".fig-rt-node", root);
    var rootLabel = q(".fig-rt-root", root);
    if (!nodes.length) { return; }

    HX.reveal(root, function (tl) {
      var n = nodes.length;
      var o = { v: 0 };
      /* each node draws its piece of the trunk and its branch in turn; --draw 1 is the static state */
      nodes.forEach(function (node) { node.style.setProperty("--draw", "0"); });
      function paint() {
        nodes.forEach(function (node, i) {
          node.style.setProperty("--draw", String(clamp01(o.v * n - i)));
        });
      }
      function finish() {
        nodes.forEach(function (node) { node.style.removeProperty("--draw"); });
      }
      if (rootLabel) { tl.from(rootLabel, { opacity: 0, y: -6, duration: 0.5 }, 0); }
      tl.to(o, { v: 1, duration: 1.5, ease: "none", onUpdate: paint, onComplete: finish }, 0.1);
      addFrom(tl, root, ".fig-rt-card", { opacity: 0, y: 10, duration: 0.6, stagger: 0.3 }, 0.1);
      addFrom(tl, root, ".fig-rt-op", { opacity: 0, duration: 0.4, stagger: 0.3 }, 0.3);
    });
  }

  HX.ready(function () {
    safe(initHero);
    safe(initSituation);
    safe(initGarage);
    safe(initStack);
    safe(initRevenue);
  });
})();
