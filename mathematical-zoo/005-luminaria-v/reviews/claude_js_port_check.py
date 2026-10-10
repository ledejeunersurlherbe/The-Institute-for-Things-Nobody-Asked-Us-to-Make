"""Does the museum's JavaScript port of Luminaria V follow the same trajectory as Morrow's original?

House standard since Morrow's note on the lobby: a port goes on a wall only after it has been
compared numerically with the original.

Python side: Morrow's script is imported and its own run() is called, unmodified. run() returns the
measurements for every arm at every step and the body field at steps 369, 370, 430, 520 and 620.

JavaScript side: rooms/luminaria-v/luminaria-v.js, the file the website runs, is executed with Node
through the same protocol: one shared history to step 369, four arms from step 370, the wound applied
to the injured arms at step 370.

Three comparisons:
  1. body fields, cell by cell, at the five recorded steps for every arm
  2. the port's measurements against the original's, at every step
  3. the port's measurements against the archived luminaria_v_measurements.csv

Run from anywhere:  python claude_js_port_check.py      (needs NumPy, Matplotlib and Node.js)
"""
import csv
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'original' / 'luminaria_v_controlled.py'
ARCHIVED = HERE.parent / 'original' / 'luminaria_v_measurements.csv'
PORT = HERE.parents[2] / 'rooms' / 'luminaria-v' / 'luminaria-v.js'
ARMS = ['sham_memory', 'injured_memory', 'sham_no_memory', 'injured_no_memory']
SNAPS = (369, 370, 430, 520, 620)

spec = importlib.util.spec_from_file_location('original_v', ORIGINAL)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
histories, images = original.run()
py = {(t, arm): (mass, com, dens) for t, arm, mass, com, dens in histories}

with tempfile.TemporaryDirectory() as tmp:
    runner = f"""
      const L = require({json.dumps(str(PORT))}), fs = require('fs'), tmp = {json.dumps(tmp)};
      const ARMS = {json.dumps(ARMS)}, SNAPS = {json.dumps(list(SNAPS))};
      let arms = {{ base: L.create() }}; const rows = [];
      for (let t = 1; t <= 620; t++) {{
        if (t === 370) {{ const pre = arms.base; arms = {{}}; for (const a of ARMS) arms[a] = pre.clone(); }}
        for (const [name, sim] of Object.entries(arms)) {{
          sim.step({{ memory: !name.includes('no_memory'), wraps: true, food: 'auto' }});
          if (t === 370 && name.includes('injured')) sim.woundAsPublished();
          const m = sim.measure(); rows.push([t, name, m.mass, m.centerX, m.woundMean]);
          if (SNAPS.includes(t)) fs.writeFileSync(`${{tmp}}/${{name}}_${{t}}.bin`, Buffer.from(sim.body().buffer.slice(0)));
        }}
      }}
      fs.writeFileSync(tmp + '/rows.json', JSON.stringify(rows));
    """
    subprocess.run(['node', '-e', runner], check=True)
    rows = json.loads(Path(tmp, 'rows.json').read_text())
    fields = {(a, t): np.fromfile(f'{tmp}/{a}_{t}.bin').reshape(original.NGRID, original.NGRID)
              for (a, t) in images}

print(f'Original: {ORIGINAL.name}     Port: {PORT.name}\n')
print('1. Body field, cell by cell (largest difference in any of 32,400 cells)')
worst_field = 0.0
for (arm, t) in sorted(images, key=lambda k: (k[1], k[0])):
    d = float(np.abs(images[(arm, t)] - fields[(arm, t)]).max())
    worst_field = max(worst_field, d)
    print(f'   step {t:>3}  {arm:<18} {d:.3e}')

print('\n2. Measurements at every step, port against the original run')
js = {(t, arm): (mass, com, dens) for t, arm, mass, com, dens in rows}
assert set(js) == set(py), 'the two runs recorded different steps or arms'
diffs = np.array([[abs(js[k][i] - py[k][i]) for i in range(3)] for k in py])
print(f'   {len(py)} rows.  Largest difference: total mass {diffs[:,0].max():.3e}, centre {diffs[:,1].max():.3e}, wound density {diffs[:,2].max():.3e}')

print('\n3. Measurements at every step, port against the archived CSV')
arch = {(int(r['step']), r['arm']): (float(r['total_biomass']), float(r['center_x']), float(r['wound_zone_mean_density']))
        for r in csv.DictReader(open(ARCHIVED))}
assert set(arch) == set(js)
diffs_a = np.array([[abs(js[k][i] - arch[k][i]) for i in range(3)] for k in arch])
print(f'   {len(arch)} rows.  Largest difference: total mass {diffs_a[:,0].max():.3e}, centre {diffs_a[:,1].max():.3e}, wound density {diffs_a[:,2].max():.3e}')

print('\n   Wound-zone density from the port, to compare with the lab report:')
for arm in ARMS:
    print(f'   {arm:<18} just after {js[(370, arm)][2]:.4f}   step 430 {js[(430, arm)][2]:.4f}   step 620 {js[(620, arm)][2]:.4f}   mass at 620 {js[(620, arm)][0]:.1f}')

worst_metric = max(diffs.max(), diffs_a.max())
print(f'\nLargest field difference: {worst_field:.3e}.  Largest measurement difference: {worst_metric:.3e}')
print('VERDICT:', 'fields identical to the last bit; measurements agree to rounding in the summation' if worst_field == 0 and worst_metric < 1e-8
      else 'same trajectory to within floating-point rounding' if worst_field < 1e-9 and worst_metric < 1e-6 else 'TRAJECTORIES DIFFER')
