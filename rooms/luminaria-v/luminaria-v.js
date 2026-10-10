/* Luminaria V (and III), the immortal carpet, running in the browser.

   A port of mathematical-zoo/005-luminaria-v/original/luminaria_v_controlled.py by Morrow:
   the same three fields (body B, nutrient N, memory M), the same parameters, the same update
   rule, with every sum and product taken in the original's order so the two round identically.

   Two switches are additions that the original did not have, taken from the review of it:
   walled edges (the original grid always wraps) and no nutrient source at all.

   Checked against the original: see mathematical-zoo/005-luminaria-v/reviews/claude-js-port-validation.md */
(function (root) {
  'use strict';
  var G = 180;
  var P = { n_diff: 0.16, n_keep: 0.994, src_add: 0.09, cons: 0.018, m_keep: 0.986, m_add: 0.06, flow: 0.032,
            growth: 0.16, gthr: 0.12, gbase: 0.26, gN: 2.0, memreg: 0.14, mthr: 0.09, mbase: 0.14,
            persist: 0.085, pthr: 0.08, decay: 0.030, dbase: 0.14, dthr: 0.07, spread: 0.022, cut: 0.007 };
  var SWITCH_STEP = 250;                       // the nutrient source moves from left to right after this step
  var WOUND = { x0: 52, x1: 84, y0: 74, y1: 106 };   // Morrow's wound: x 52..83, y 74..105
  var LEFT = { x: 24, y: 90, r: 13 }, RIGHT = { x: 156, y: 90, r: 13 };

  function disc(c) {
    var m = new Uint8Array(G * G);
    for (var y = 0; y < G; y++) for (var x = 0; x < G; x++)
      if ((x - c.x) * (x - c.x) + (y - c.y) * (y - c.y) <= c.r * c.r) m[y * G + x] = 1;
    return m;
  }
  var SRC_LEFT = disc(LEFT), SRC_RIGHT = disc(RIGHT);

  function create() {
    var B = new Float64Array(G * G), N = new Float64Array(G * G), M = new Float64Array(G * G);
    var B2 = new Float64Array(G * G), N2 = new Float64Array(G * G);
    var t = 0;
    for (var y = 0; y < G; y++) for (var x = 0; x < G; x++)
      if ((x - 40) * (x - 40) + (y - 90) * (y - 90) <= 144) B[y * G + x] = 0.92;

    /* opts.memory: true/false.  opts.wraps: true (as published) or false (walled).
       opts.food: 'auto' (left, then right after step 250, as published), 'left', 'right' or 'none'. */
    function step(opts) {
      t += 1;
      var memory = opts.memory !== false, wraps = opts.wraps !== false, food = opts.food || 'auto';
      var src = food === 'none' ? null : food === 'left' ? SRC_LEFT : food === 'right' ? SRC_RIGHT : (t <= SWITCH_STEP ? SRC_LEFT : SRC_RIGHT);
      var x, y, i, row, up, down, l, r, n, b;

      // 1. Nutrient: spread, fade, top up at the source, get eaten.
      for (y = 0; y < G; y++) {
        row = y * G;
        up = (y > 0 ? y - 1 : (wraps ? G - 1 : 0)) * G;
        down = (y < G - 1 ? y + 1 : (wraps ? 0 : G - 1)) * G;
        for (x = 0; x < G; x++) {
          i = row + x;
          l = row + (x > 0 ? x - 1 : (wraps ? G - 1 : 0));
          r = row + (x < G - 1 ? x + 1 : (wraps ? 0 : G - 1));
          n = N[i];
          n = n + P.n_diff * (N[up + x] + N[down + x] + N[l] + N[r] - 4 * n);
          n = n * P.n_keep;
          if (src && src[i]) n = n + P.src_add;
          n = n - P.cons * B[i] * n;
          N2[i] = n < 0 ? 0 : n > 1.5 ? 1.5 : n;
        }
      }

      // 2. Memory and body, using the new nutrient field.
      for (y = 0; y < G; y++) {
        row = y * G;
        up = (y > 0 ? y - 1 : (wraps ? G - 1 : 0)) * G;
        down = (y < G - 1 ? y + 1 : (wraps ? 0 : G - 1)) * G;
        for (x = 0; x < G; x++) {
          i = row + x;
          l = row + (x > 0 ? x - 1 : (wraps ? G - 1 : 0));
          r = row + (x < G - 1 ? x + 1 : (wraps ? 0 : G - 1));
          b = B[i]; n = N2[i];
          var m = 0;
          if (memory) { m = P.m_keep * M[i] + P.m_add * b; m = m < 0 ? 0 : m > 1 ? 1 : m; }
          M[i] = m;
          var around = B[up + x] + B[down + x] + B[l] + B[r];
          var nb = 0.40 * b + 0.15 * around;
          var grad = 0.5 * (N2[r] - N2[l]);
          var growth = P.growth * (1 - b) * Math.max(nb - P.gthr, 0) * (P.gbase + P.gN * n);
          var reg = memory ? P.memreg * (1 - b) * m * Math.max(nb - P.mthr, 0) * (P.mbase + n) : 0;
          var persist = P.persist * b * Math.max(nb - P.pthr, 0);
          var decay = P.decay * b * (P.dbase + Math.max(0, P.dthr - n));
          var nextB = b + growth + reg + persist + P.spread * (around - 4 * b) - decay + P.flow * grad * b;
          nextB = nextB < 0 ? 0 : nextB > 1 ? 1 : nextB;
          B2[i] = nextB < P.cut ? 0 : nextB;
        }
      }
      var s = B; B = B2; B2 = s; s = N; N = N2; N2 = s;
      return t;
    }

    function clearRect(x0, x1, y0, y1) { for (var y = y0; y < y1; y++) for (var x = x0; x < x1; x++) B[y * G + x] = 0; }
    function clearDisc(cx, cy, radius) {
      for (var y = Math.max(0, cy - radius); y <= Math.min(G - 1, cy + radius); y++)
        for (var x = Math.max(0, cx - radius); x <= Math.min(G - 1, cx + radius); x++)
          if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius) B[y * G + x] = 0;
    }
    function measure() {
      var mass = 0, mx = 0, wound = 0, covered = 0, x, y, v;
      for (y = 0; y < G; y++) for (x = 0; x < G; x++) { v = B[y * G + x]; mass += v; mx += v * x; if (v > 0.5) covered++; }
      for (y = WOUND.y0; y < WOUND.y1; y++) for (x = WOUND.x0; x < WOUND.x1; x++) wound += B[y * G + x];
      return { mass: mass, centerX: mass > 0 ? mx / mass : NaN, woundMean: wound / ((WOUND.x1 - WOUND.x0) * (WOUND.y1 - WOUND.y0)), covered: covered / (G * G) };
    }
    function clone() {
      var c = create(); c._load(B, N, M, t); return c;
    }
    return {
      step: step, measure: measure, clone: clone,
      woundAsPublished: function () { clearRect(WOUND.x0, WOUND.x1, WOUND.y0, WOUND.y1); },
      woundAt: clearDisc,
      body: function () { return B; }, nutrient: function () { return N; }, memory: function () { return M; },
      time: function () { return t; },
      _load: function (b, n, m, time) { B.set(b); N.set(n); M.set(m); t = time; }
    };
  }

  var api = { create: create, G: G, WOUND: WOUND, LEFT: LEFT, RIGHT: RIGHT, SWITCH_STEP: SWITCH_STEP };
  root.LuminariaV = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
