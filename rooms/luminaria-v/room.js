/* The immortal carpet's room. The simulation itself is in luminaria-v.js. */
(function () {
  'use strict';
  var L = window.LuminariaV;
  var canvas = document.getElementById('organism');
  if (!L || !canvas) return;

  var G = L.G, STEPS_PER_FRAME = 2, BRUSH = 9;
  var ctx = canvas.getContext('2d'), image = ctx.createImageData(G, G);
  var stage = document.getElementById('stage');
  var stepEl = document.getElementById('step'), coverEl = document.getElementById('cover'), eventEl = document.getElementById('event');
  var toggle = document.getElementById('toggle'), again = document.getElementById('again'), morrowWound = document.getElementById('morrow-wound');
  var form = document.getElementById('switches'), foodMark = document.getElementById('food-mark');
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var NIGHT = [16, 21, 29], TEAL = [113, 158, 158], VIOLET = [143, 120, 196], CREAM = [244, 231, 194];
  var sim, running, visible = true, frame = null, touched, full;

  function settings() {
    return { food: form.elements.food.value, wraps: form.elements.edges.value === 'wrap', memory: form.elements.memory.checked };
  }
  // The published protocol: untouched switches, and nobody has removed growth by hand.
  function asPublished() { var s = settings(); return !touched && s.food === 'auto' && s.wraps && s.memory; }

  function say(text) { eventEl.textContent = text; }

  function draw() {
    var B = sim.body(), N = sim.nutrient(), M = sim.memory(), d = image.data;
    for (var i = 0, j = 0; i < G * G; i++, j += 4) {
      var n = Math.min(1, N[i] / 1.2) * 0.8, m = M[i] * 0.6, b = B[i];
      for (var c = 0; c < 3; c++) {
        var v = NIGHT[c] + (TEAL[c] - NIGHT[c]) * n;
        v = v + (VIOLET[c] - v) * m;
        d[j + c] = v + (CREAM[c] - v) * b;
      }
      d[j + 3] = 255;
    }
    ctx.putImageData(image, 0, 0);
  }

  function markNutrient() {
    var f = settings().food, right = f === 'right' || (f === 'auto' && sim.time() >= L.SWITCH_STEP);
    foodMark.classList.toggle('gone', f === 'none');
    foodMark.setAttribute('cx', right ? L.RIGHT.x : L.LEFT.x);
  }

  function readout() {
    var m = sim.measure();
    stepEl.textContent = sim.time().toLocaleString('en-US');
    coverEl.textContent = Math.round(m.covered * 100) + '%';
    toggle.textContent = running ? 'Pause' : (sim.time() === 0 ? 'Begin' : 'Resume');
    toggle.hidden = full;
    return m;
  }

  function narrate(t) {
    if (!asPublished()) return;
    if (t === L.SWITCH_STEP + 1) say('Step 250. The nutrient source has moved to the right-hand side.');
    if (t === 370) { sim.woundAsPublished(); say('Step 370. Morrow removes a square of the body. The violet patch is the memory of what was there.'); }
    if (t === 620) say('Step 620. The original experiment ended here. We have let it keep going.');
  }

  function tick() {
    frame = null;
    if (!running || !visible) return;
    for (var k = 0; k < STEPS_PER_FRAME; k++) { var t = sim.step(settings()); narrate(t); }
    draw(); markNutrient();
    if (sim.time() % 10 === 0) {
      var m = readout();
      if (m.covered >= 0.9995) { full = true; running = false; readout(); say('It has covered the entire grid. There is nowhere left to grow. Press Start over to watch it again.'); }
      else if (m.mass < 1) { full = true; running = false; readout(); say('Nothing is left of it. Press Start over to bring it back.'); }
    }
    if (running) frame = requestAnimationFrame(tick);
  }
  function go() { if (running && visible && frame === null) frame = requestAnimationFrame(tick); }

  function start(autoplay) {
    sim = L.create(); touched = false; full = false; running = autoplay;
    var s = settings();
    say(asPublished() ? 'The original experiment is playing: 620 steps, as Morrow ran it.'
      : 'A fresh organism, with your settings' + (s.food === 'none' ? ' and no nutrient' : '') + '. Remove some growth whenever you like.');
    draw(); markNutrient(); readout(); go();
  }

  function woundAt(evt) {
    var box = stage.getBoundingClientRect();
    var x = Math.floor((evt.clientX - box.left) / box.width * G), y = Math.floor((evt.clientY - box.top) / box.height * G);
    if (x < 0 || y < 0 || x >= G || y >= G) return;
    sim.woundAt(x, y, BRUSH);
    if (!touched) { touched = true; say('You have removed some growth. Watch the edges of the gap.'); }
    draw();
    if (full) { full = false; running = true; readout(); go(); }
  }
  var dragging = false;
  stage.addEventListener('pointerdown', function (e) { dragging = e.pointerType === 'mouse'; woundAt(e); });
  stage.addEventListener('pointermove', function (e) { if (dragging && e.buttons) woundAt(e); });
  window.addEventListener('pointerup', function () { dragging = false; });

  toggle.addEventListener('click', function () { running = !running; readout(); go(); });
  again.addEventListener('click', function () { start(true); });
  morrowWound.addEventListener('click', function () {
    sim.woundAsPublished(); touched = true; draw();
    say('A square removed, where Morrow removed it: columns 52 to 83, rows 74 to 105.');
    if (full) { full = false; running = true; readout(); go(); }
  });
  form.addEventListener('change', function (e) {
    markNutrient();
    var s = settings();
    if (e.target.name === 'food') say(s.food === 'none' ? 'The nutrient is gone. Remove some growth now and see whether it makes any difference.' : 'The nutrient source has changed.');
    if (e.target.name === 'edges') say(s.wraps ? 'The edges wrap around again.' : 'Walls are up. Nothing can slip off one edge and arrive on the other.');
    if (e.target.name === 'memory') say(s.memory ? 'Memory is back on.' : 'Memory is off. The violet trace is gone, and so is the small boost it gave.');
  });

  document.addEventListener('visibilitychange', function () { visible = !document.hidden; go(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting && !document.hidden; go(); }).observe(canvas);
  }

  start(!calm);
})();
