/* Specimen 001, Luminaria labyrinthica, running in the browser.

   This is the same experiment as mathematical-zoo/001-luminaria-labyrinthica/original/
   luminaria_labyrinthica.py by Morrow: the same Gray-Scott equations, the same parameters,
   the same 220 x 220 wrapped grid, and the same twelve seed patches (copied out of NumPy's
   default_rng(42) so the starting state is identical). Only the language has changed.

   Checked against the original's own output at steps 500, 1,500 and 6,000: the two are identical
   to the last bit. See mathematical-zoo/001-luminaria-labyrinthica/reviews/. */
(function (root) {
  'use strict';
  var N = 220, STEPS = 6000;
  var DU = 0.16, DV = 0.08, FEED = 0.035, KILL = 0.062;
  // x, y, radius, U inside the patch, V inside the patch
  var SEEDS = [
    [36, 159, 6, 0.5286878335929106, 0.2618420817435618],
    [98, 56, 3, 0.5380497881309405, 0.2656683821194212],
    [149, 161, 6, 0.4960308750316454, 0.24224788145395487],
    [43, 52, 8, 0.5115092096064532, 0.2693656967962498],
    [118, 99, 5, 0.5043667829612668, 0.2238290353662505],
    [60, 174, 7, 0.5105331519297652, 0.26548526440512243],
    [146, 83, 3, 0.5314496897057758, 0.26670300982442574],
    [194, 156, 4, 0.4973376802981627, 0.22262822594723372],
    [118, 47, 7, 0.5195809724726254, 0.2780505839460526],
    [142, 93, 4, 0.4896367764827895, 0.24817334867654847],
    [163, 54, 5, 0.4980563940980747, 0.23361456094305305],
    [43, 121, 7, 0.49497215350978646, 0.26996069176347026]
  ];

  function create() {
    var u = new Float64Array(N * N).fill(1), v = new Float64Array(N * N);
    var u2 = new Float64Array(N * N), v2 = new Float64Array(N * N);
    var step = 0;
    SEEDS.forEach(function (s) {
      for (var y = 0; y < N; y++) for (var x = 0; x < N; x++) {
        if ((x - s[0]) * (x - s[0]) + (y - s[1]) * (y - s[1]) <= s[2] * s[2]) { u[y * N + x] = s[3]; v[y * N + x] = s[4]; }
      }
    });

    function advance(n) {
      for (var k = 0; k < n && step < STEPS; k++, step++) {
        for (var y = 0; y < N; y++) {
          var row = y * N, up = ((y + N - 1) % N) * N, down = ((y + 1) % N) * N;
          for (var x = 0; x < N; x++) {
            var i = row + x, l = row + (x + N - 1) % N, r = row + (x + 1) % N;
            var uu = u[i], vv = v[i], uvv = uu * vv * vv;
            // The change is worked out in full and then added, in the same order as the original,
            // so that rounding falls the same way and the two stay identical to the last bit.
            u2[i] = uu + (DU * (u[up + x] + u[down + x] + u[l] + u[r] - 4 * uu) - uvv + FEED * (1 - uu));
            v2[i] = vv + (DV * (v[up + x] + v[down + x] + v[l] + v[r] - 4 * vv) + uvv - (FEED + KILL) * vv);
          }
        }
        var t = u; u = u2; u2 = t; t = v; v = v2; v2 = t;
      }
      return step;
    }

    return { advance: advance, field: function () { return v; }, step: function () { return step; } };
  }

  var api = { create: create, N: N, STEPS: STEPS };
  root.Specimen001 = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
