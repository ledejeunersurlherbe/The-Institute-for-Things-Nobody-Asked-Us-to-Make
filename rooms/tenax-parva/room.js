/* Tenax parva's room. The simulation itself is in tenax-parva.js. */
(function () {
  'use strict';
  var T = window.TenaxParva;
  var canvas = document.getElementById('organism');
  if (!T || !canvas) return;

  var G = T.G, BRUSH = 8, ERASER = 10, FRAME_BUDGET_MS = 8, MAX_STEPS_PER_FRAME = 5;
  var TRACE_EVERY = 10, TRACE_POINTS = 400;                 // 4,000 steps of history
  var ctx = canvas.getContext('2d'), image = ctx.createImageData(G, G);
  var stage = document.getElementById('stage');
  var sizeEl = document.getElementById('size'), awayEl = document.getElementById('away'), stepEl = document.getElementById('step');
  var eventEl = document.getElementById('event'), toggle = document.getElementById('toggle'), again = document.getElementById('again');
  var tools = document.getElementById('tools'), switches = document.getElementById('switches');
  var traceCanvas = document.getElementById('trace'), tctx = traceCanvas.getContext('2d');
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var NIGHT = [16, 21, 29], HAZE = [96, 128, 172], VIOLET = [143, 120, 196], CREAM = [244, 231, 194];
  var sim, home, running, visible = true, frame = null, trace, changedAt, announced;

  function settings() { return { inhibitor: switches.elements.inhibitor.checked, scaffold: switches.elements.scaffold.checked }; }
  function say(text) { eventEl.textContent = text; }

  function draw() {
    var B = sim.body(), M = sim.scaffold(), H = sim.inhibitor(), d = image.data, showHaze = settings().inhibitor;
    for (var i = 0, j = 0; i < G * G; i++, j += 4) {
      var h = showHaze ? Math.min(1, H[i] / 0.45) * 0.42 : 0, b = B[i], m = M[i] * 0.62;
      for (var c = 0; c < 3; c++) {
        var v = NIGHT[c] + (HAZE[c] - NIGHT[c]) * h;
        v = v + (VIOLET[c] - v) * m;
        d[j + c] = v + (CREAM[c] - v) * b;
      }
      d[j + 3] = 255;
    }
    ctx.putImageData(image, 0, 0);
  }

  function drawTrace() {
    var ratio = window.devicePixelRatio || 1, w = traceCanvas.clientWidth, h = traceCanvas.clientHeight;
    if (traceCanvas.width !== Math.round(w * ratio)) { traceCanvas.width = Math.round(w * ratio); traceCanvas.height = Math.round(h * ratio); }
    tctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    tctx.clearRect(0, 0, w, h);
    var top = 1.6, bottom = 0.4, left = 34, right = 6;
    function y(v) { return (top - Math.min(top, Math.max(bottom, v))) / (top - bottom) * (h - 8) + 4; }
    tctx.fillStyle = '#cdd6d1'; tctx.fillRect(left, y(1.05), w - left - right, y(0.95) - y(1.05));   // within 5 percent
    tctx.strokeStyle = '#44556a'; tctx.lineWidth = 1; tctx.beginPath(); tctx.moveTo(left, y(1)); tctx.lineTo(w - right, y(1)); tctx.stroke();
    tctx.fillStyle = '#44556a'; tctx.font = '12px "Hanken Grotesk", system-ui, sans-serif'; tctx.textBaseline = 'middle';
    tctx.fillText('150%', 0, y(1.5)); tctx.fillText('100%', 0, y(1)); tctx.fillText('50%', 4, y(0.5));
    tctx.strokeStyle = '#10151d'; tctx.lineWidth = 2; tctx.lineJoin = 'round'; tctx.beginPath();
    for (var i = 0; i < trace.length; i++) {
      var x = left + (w - left - right) * (TRACE_POINTS - trace.length + i) / (TRACE_POINTS - 1);
      if (i === 0) tctx.moveTo(x, y(trace[i])); else tctx.lineTo(x, y(trace[i]));
    }
    tctx.stroke();
  }

  function readout() {
    var m = sim.measure(), size = m.mass / T.SET_POINT;
    sizeEl.textContent = Math.round(size * 100) + '%';
    awayEl.textContent = isNaN(m.cx) ? 'n/a' : Math.hypot(m.cx - home.cx, m.cy - home.cy).toFixed(1);
    stepEl.textContent = sim.time().toLocaleString('en-US');
    toggle.textContent = running ? 'Pause' : (sim.time() === 0 ? 'Begin' : 'Resume');
    return { size: size, measure: m };
  }

  function watch(r) {
    var s = settings();
    if (r.measure.mass < 1) { running = false; say('Nothing is left of it. Press Start over for a fresh one.'); readout(); return; }
    if (!s.inhibitor && r.measure.atWall && announced !== 'wall') { announced = 'wall'; say('It has reached the walls. With no inhibitor there is nothing to stop it.'); }
    if (changedAt !== null && s.inhibitor && Math.abs(r.size - 1) <= 0.05 && sim.time() - changedAt > 150) {
      say('Back within 5 percent of its settled size, ' + (sim.time() - changedAt).toLocaleString('en-US') + ' steps after the change.');
      changedAt = null;
    }
  }

  function tick() {
    frame = null;
    if (!running || !visible) return;
    var began = performance.now(), n = 0, s = settings();
    do {
      var t = sim.step(s); n++;
      if (t % TRACE_EVERY === 0) { trace.push(sim.measure().mass / T.SET_POINT); if (trace.length > TRACE_POINTS) trace.shift(); }
    } while (n < MAX_STEPS_PER_FRAME && performance.now() - began < FRAME_BUDGET_MS);
    draw();
    if (sim.time() % 10 < n) { watch(readout()); drawTrace(); }
    if (running) frame = requestAnimationFrame(tick);
  }
  function go() { if (running && visible && frame === null) frame = requestAnimationFrame(tick); }

  function start(autoplay) {
    sim = T.create((Date.now() ^ (Math.random() * 1e9)) >>> 0);
    sim.step({ noise: false });                    // one quiet step so the inhibitor field exists to draw
    var m = sim.measure(); home = { cx: m.cx, cy: m.cy };
    trace = [m.mass / T.SET_POINT]; changedAt = null; announced = null; running = autoplay;
    say('A settled organism. The dashed ring marks where it started.');
    draw(); readout(); drawTrace(); go();
  }

  function changed(message) { changedAt = sim.time(); announced = null; say(message); draw(); readout(); if (!running) drawTrace(); }

  function act(evt) {
    var box = stage.getBoundingClientRect();
    var x = Math.floor((evt.clientX - box.left) / box.width * G), y = Math.floor((evt.clientY - box.top) / box.height * G);
    if (x < 0 || y < 0 || x >= G || y >= G) return;
    var tool = tools.elements.tool.value;
    if (tool === 'remove') { sim.removeAt(x, y, BRUSH); changed('You have removed some growth. Watch the size line.'); }
    else if (tool === 'add') { sim.addAt(x, y, BRUSH); changed('You have added growth. Watch the size line come back down.'); }
    else { sim.eraseScaffoldAt(x, y, ERASER); changed('You have erased part of the scaffold. The violet record is gone there.'); }
  }
  var dragging = false;
  stage.addEventListener('pointerdown', function (e) { dragging = e.pointerType === 'mouse'; act(e); });
  stage.addEventListener('pointermove', function (e) { if (dragging && e.buttons) act(e); });
  window.addEventListener('pointerup', function () { dragging = false; });

  toggle.addEventListener('click', function () { running = !running; readout(); go(); });
  again.addEventListener('click', function () { start(true); });
  document.getElementById('published-remove').addEventListener('click', function () {
    sim.removeSide(false); changed('The right-hand part removed, a little over a third of the body, as in the published experiment.');
  });
  document.getElementById('published-add').addEventListener('click', function () {
    sim.addPatch(); changed('A patch added on the right, about a fifth extra, as in the published experiment.');
  });
  switches.addEventListener('change', function (e) {
    var s = settings();
    if (e.target.name === 'inhibitor') { changedAt = s.inhibitor ? sim.time() : null; announced = null; say(s.inhibitor ? 'The inhibitor is back on. Watch the size line.' : 'The inhibitor is off. Nothing is holding its size now.'); }
    if (e.target.name === 'scaffold') say(s.scaffold ? 'The scaffold is acting again.' : 'The scaffold is switched off. The record is still kept, but nothing uses it.');
    draw();
  });

  document.addEventListener('visibilitychange', function () { visible = !document.hidden; go(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting && !document.hidden; go(); }).observe(canvas);
  }
  window.addEventListener('resize', drawTrace);

  start(!calm);
})();
