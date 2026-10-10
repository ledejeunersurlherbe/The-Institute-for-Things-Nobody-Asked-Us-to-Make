/* Tenax parva, running in the browser.

   A port of mathematical-zoo/006-tenax-parva/original/tenax.py by Claude: the same three fields
   (body B, scaffold M, inhibitor H), the same parameters and the same update rule, on the same
   walled 128 x 128 grid.

     H  = B + L^2 lap(H)                      solved exactly each step with a cosine transform
     theta = a + g H - m (M - B)
     B += D lap(B) + r B (1-B) (B - theta) + noise
     M += (B - M) / tau

   Two honest differences from the published experiment:
   1. The random noise comes from this file's own generator. NumPy's random stream cannot be
      reproduced here, so a run in the browser is not the same run as any published seed.
   2. The published runs grew each body from a rough ellipse for 8,000 steps. Here the body starts
      as a disc already at its settled size, so that visitors do not wait.

   Checked against the original: see mathematical-zoo/006-tenax-parva/reviews/claude-js-port-validation.md */
(function (root) {
  'use strict';
  var G = 128, HALF = G / 2;
  var P = { a: 0.2, g: 1.0, L: 25.0, D: 0.2, r: 0.06, m: 0.2, tau: 1000.0, noise: 0.02 };
  var SETTLED_RADIUS = 24.89;  // the radius the body settles at; found by letting one settle, see the note
  var SET_POINT = 2015;        // settled body size, in cells' worth of tissue

  // ---- cosine transform (DCT-II and its inverse) through a 128-point FFT
  var REV = new Uint8Array(G), COS = new Float64Array(HALF), SIN = new Float64Array(HALF);
  var TW_C = new Float64Array(G), TW_S = new Float64Array(G);
  (function () {
    for (var i = 0; i < G; i++) { var r = 0; for (var b = 0; b < 7; b++) if (i & (1 << b)) r |= 1 << (6 - b); REV[i] = r; }
    for (var k = 0; k < HALF; k++) { COS[k] = Math.cos(2 * Math.PI * k / G); SIN[k] = Math.sin(2 * Math.PI * k / G); }
    for (var j = 0; j < G; j++) { TW_C[j] = Math.cos(Math.PI * j / (2 * G)); TW_S[j] = Math.sin(Math.PI * j / (2 * G)); }
  })();
  var re = new Float64Array(G), im = new Float64Array(G), line = new Float64Array(G);

  function fft(inverse) {   // in place on re, im; unnormalised
    var i, j, k, len, half, step, wr, wi, xr, xi, t;
    for (i = 0; i < G; i++) { j = REV[i]; if (j > i) { t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
    for (len = 2; len <= G; len <<= 1) {
      half = len >> 1; step = G / len;
      for (i = 0; i < G; i += len) for (j = 0, k = 0; j < half; j++, k += step) {
        wr = COS[k]; wi = inverse ? SIN[k] : -SIN[k];
        xr = re[i + j + half] * wr - im[i + j + half] * wi; xi = re[i + j + half] * wi + im[i + j + half] * wr;
        re[i + j + half] = re[i + j] - xr; im[i + j + half] = im[i + j] - xi;
        re[i + j] += xr; im[i + j] += xi;
      }
    }
  }
  function dct() {          // line -> line, X[k] = sum x[n] cos(pi (2n+1) k / 2N)
    var n, k;
    for (n = 0; n < HALF; n++) { re[n] = line[2 * n]; re[G - 1 - n] = line[2 * n + 1]; }
    for (n = 0; n < G; n++) im[n] = 0;
    fft(false);
    for (k = 0; k < G; k++) line[k] = re[k] * TW_C[k] + im[k] * TW_S[k];
  }
  function idct() {         // exact inverse of dct()
    var n, k, a, b;
    re[0] = line[0]; im[0] = 0;
    for (k = 1; k < G; k++) { a = line[k]; b = -line[G - k]; re[k] = a * TW_C[k] - b * TW_S[k]; im[k] = a * TW_S[k] + b * TW_C[k]; }
    fft(true);
    for (n = 0; n < HALF; n++) { line[2 * n] = re[n] / G; line[2 * n + 1] = re[G - 1 - n] / G; }
  }
  var DENOM = new Float64Array(G * G);
  function setLength(L) {
    for (var y = 0; y < G; y++) for (var x = 0; x < G; x++)
      DENOM[y * G + x] = 1 + L * L * ((2 - 2 * Math.cos(Math.PI * y / G)) + (2 - 2 * Math.cos(Math.PI * x / G)));
  }
  setLength(P.L);
  function solveInhibitor(B, H) {
    var x, y;
    for (y = 0; y < G; y++) { for (x = 0; x < G; x++) line[x] = B[y * G + x]; dct(); for (x = 0; x < G; x++) H[y * G + x] = line[x]; }
    for (x = 0; x < G; x++) { for (y = 0; y < G; y++) line[y] = H[y * G + x]; dct(); for (y = 0; y < G; y++) H[y * G + x] = line[y] / DENOM[y * G + x]; }
    for (x = 0; x < G; x++) { for (y = 0; y < G; y++) line[y] = H[y * G + x]; idct(); for (y = 0; y < G; y++) H[y * G + x] = line[y]; }
    for (y = 0; y < G; y++) { for (x = 0; x < G; x++) line[x] = H[y * G + x]; idct(); for (x = 0; x < G; x++) H[y * G + x] = line[x]; }
  }

  // ---- a small seeded random source (mulberry32, then Box-Muller for a normal draw)
  function randomSource(seed) {
    var s = seed >>> 0, spare = null;
    function uniform() { s = (s + 0x6D2B79F5) >>> 0; var t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
    return function normal() {
      if (spare !== null) { var v = spare; spare = null; return v; }
      var u = 0; while (u === 0) u = uniform();
      var mag = Math.sqrt(-2 * Math.log(u)), ang = 2 * Math.PI * uniform();
      spare = mag * Math.sin(ang); return mag * Math.cos(ang);
    };
  }

  function create(seed) {
    var B = new Float64Array(G * G), M = new Float64Array(G * G), H = new Float64Array(G * G), B2 = new Float64Array(G * G);
    var t = 0, normal = randomSource(seed === undefined ? 1 : seed);
    var cx0 = (G - 1) / 2, cy0 = (G - 1) / 2, width = Math.sqrt(2 * P.D / P.r);   // the front's natural width
    for (var y = 0; y < G; y++) for (var x = 0; x < G; x++) {
      var d = Math.sqrt((x - cx0) * (x - cx0) + (y - cy0) * (y - cy0));
      B[y * G + x] = 1 / (1 + Math.exp((d - SETTLED_RADIUS) / width));
      M[y * G + x] = B[y * G + x];
    }

    /* opts.inhibitor (default on), opts.scaffold (default on: the scaffold term acts), opts.noise (default on) */
    function step(opts) {
      opts = opts || {};
      var g = opts.inhibitor === false ? 0 : P.g, m = opts.scaffold === false ? 0 : P.m, noise = opts.noise === false ? 0 : P.noise;
      var x, y, i, row, up, down, l, r, b, theta, next;
      if (g !== 0) solveInhibitor(B, H);
      for (y = 0; y < G; y++) {
        row = y * G; up = (y > 0 ? y - 1 : 0) * G; down = (y < G - 1 ? y + 1 : G - 1) * G;
        for (x = 0; x < G; x++) {
          i = row + x; l = row + (x > 0 ? x - 1 : 0); r = row + (x < G - 1 ? x + 1 : G - 1);
          b = B[i];
          theta = P.a + g * H[i] - m * (M[i] - b);
          next = b + P.D * (B[up + x] + B[down + x] + B[l] + B[r] - 4 * b) + P.r * b * (1 - b) * (b - theta);
          if (noise !== 0) next = next + noise * normal() * b * (1 - b);
          B2[i] = next < 0 ? 0 : next > 1 ? 1 : next;
        }
      }
      for (i = 0; i < G * G; i++) M[i] = M[i] + (B2[i] - M[i]) / P.tau;
      var s = B; B = B2; B2 = s;
      return ++t;
    }

    function disc(field, cx, cy, radius, value) {
      for (var y = Math.max(0, Math.floor(cy - radius)); y <= Math.min(G - 1, Math.ceil(cy + radius)); y++)
        for (var x = Math.max(0, Math.floor(cx - radius)); x <= Math.min(G - 1, Math.ceil(cx + radius)); x++)
          if ((x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius) field[y * G + x] = value === 'max1' ? Math.max(field[y * G + x], 1) : value;
    }
    function measure() {
      var mass = 0, mx = 0, my = 0, wall = false, v;
      for (var y = 0; y < G; y++) for (var x = 0; x < G; x++) {
        v = B[y * G + x]; mass += v; mx += v * x; my += v * y;
        if (v > 0.5 && (x === 0 || y === 0 || x === G - 1 || y === G - 1)) wall = true;
      }
      return { mass: mass, cx: mass > 1 ? mx / mass : NaN, cy: mass > 1 ? my / mass : NaN, atWall: wall };
    }
    return {
      step: step, measure: measure,
      removeAt: function (x, y, r) { disc(B, x, y, r, 0); },
      addAt: function (x, y, r) { disc(B, x, y, r, 'max1'); },
      eraseScaffoldAt: function (x, y, r) { disc(M, x, y, r, 0); },
      /* The published perturbations, placed relative to the body's present centre. */
      removeSide: function (eraseScaffoldToo) {
        var c = measure();
        for (var y = 0; y < G; y++) for (var x = 0; x < G; x++) if (x > c.cx + 5) { B[y * G + x] = 0; if (eraseScaffoldToo) M[y * G + x] = 0; }
      },
      eraseScaffoldSide: function () { var c = measure(); for (var y = 0; y < G; y++) for (var x = 0; x < G; x++) if (x > c.cx + 5) M[y * G + x] = 0; },
      addPatch: function () { var c = measure(); disc(B, c.cx + 25, c.cy, 14, 'max1'); },
      body: function () { return B; }, scaffold: function () { return M; },
      inhibitor: function () { return H; },
      time: function () { return t; },
      clone: function (newSeed) { var c = create(newSeed === undefined ? seed : newSeed); c._load(B, M, t); return c; },
      _load: function (b, m, time) { B.set(b); M.set(m); t = time; }
    };
  }

  var api = { create: create, G: G, P: P, SETTLED_RADIUS: SETTLED_RADIUS, SET_POINT: SET_POINT, _solveInhibitor: solveInhibitor };
  root.TenaxParva = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
