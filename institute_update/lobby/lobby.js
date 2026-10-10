/* Grows Specimen 001 on the lobby wall. The simulation itself is in specimen001.js. */
(function () {
  'use strict';
  var canvas = document.getElementById('specimen');
  var stepText = document.getElementById('step-text');
  var toggle = document.getElementById('toggle');
  var restart = document.getElementById('restart');
  if (!canvas || !window.Specimen001) return;

  var N = Specimen001.N, STEPS = Specimen001.STEPS;
  var STEPS_PER_FRAME = 3;                 // about half a minute from seed to labyrinth
  var ctx = canvas.getContext('2d');
  var image = ctx.createImageData(N, N);
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Morrow's colour scale for the specimen: V from 0 to 0.35, charcoal to cream.
  var stops = [[16, 21, 29], [35, 45, 64], [68, 85, 106], [113, 158, 158], [214, 213, 176], [244, 231, 194]];
  var lut = new Uint8ClampedArray(256 * 3);
  for (var i = 0; i < 256; i++) {
    var p = (i / 255) * (stops.length - 1), a = Math.min(Math.floor(p), stops.length - 2), f = p - a;
    for (var c = 0; c < 3; c++) lut[i * 3 + c] = stops[a][c] + (stops[a + 1][c] - stops[a][c]) * f;
  }

  var specimen = Specimen001.create();
  var running = !calm, visible = true, frame = null;

  function draw() {
    var v = specimen.field(), d = image.data;
    for (var i = 0, j = 0; i < v.length; i++, j += 4) {
      var k = Math.max(0, Math.min(255, Math.round(v[i] / 0.35 * 255))) * 3;
      d[j] = lut[k]; d[j + 1] = lut[k + 1]; d[j + 2] = lut[k + 2]; d[j + 3] = 255;
    }
    ctx.putImageData(image, 0, 0);
  }

  function label() {
    var s = specimen.step(), done = s >= STEPS;
    stepText.textContent = done ? 'Finished at step 6,000' : 'Step ' + s.toLocaleString('en-US') + ' of 6,000';
    toggle.textContent = running ? 'Pause' : (s === 0 ? 'Grow it' : 'Resume');
    toggle.hidden = done;
  }

  function tick() {
    frame = null;
    if (!running || !visible) return;
    specimen.advance(STEPS_PER_FRAME);
    draw();
    if (specimen.step() >= STEPS) running = false;
    if (specimen.step() % 30 === 0 || !running) label();
    if (running) frame = requestAnimationFrame(tick);
  }
  function go() { if (running && visible && frame === null) frame = requestAnimationFrame(tick); }

  toggle.addEventListener('click', function () { running = !running; label(); go(); });
  restart.addEventListener('click', function () { specimen = Specimen001.create(); running = true; draw(); label(); go(); });

  // Stop working when nobody can see the wall.
  document.addEventListener('visibilitychange', function () { visible = !document.hidden; go(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting && !document.hidden; go(); }).observe(canvas);
  }

  draw(); label(); go();
})();
