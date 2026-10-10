"""Does the museum's JavaScript port of Tenax parva behave like the original?

House standard: a port goes on a wall only after it has been compared numerically with the original.

Tenax parva cannot be checked the way the Luminaria ports were. The published runs used random noise
from NumPy's generator, which a browser cannot reproduce, so no browser run can be the same run as a
published seed. The check is therefore in two parts.

PART 1. The rule, with noise off.
  The port is started, perturbed in each of the ways the room allows, and its state is saved before
  and after 2,000 further steps. The original tenax.py's own step() is then run from the same saved
  state for the same 2,000 steps with noise set to zero, and the two end states are compared cell by cell.

PART 2. The behaviour, with noise on.
  The port, using its own noise, is put through the published protocol (untouched twin, part removed,
  part removed and scaffold erased, tissue added, scaffold erased only) for 5,000 steps on several
  seeds, and its end-of-run figures are set beside the published twelve-seed figures.

Run from anywhere:  python claude_js_port_check.py      (NumPy, SciPy and Node.js; about 6 minutes)
"""
import csv
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'original' / 'tenax.py'
SUMMARY = HERE.parent / 'original' / 'tenax_summary.csv'
PORT = HERE.parents[2] / 'rooms' / 'tenax-parva' / 'tenax-parva.js'
STEPS = 2000
SEEDS = [1, 2, 3, 4]

spec = importlib.util.spec_from_file_location('original_tenax', ORIGINAL)
tenax = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tenax)
G = tenax.G

SCENARIOS = {
    'left untouched': ('', {}),
    'right-hand part removed': ('s.removeSide(false);', {}),
    'part removed, scaffold erased there': ('s.removeSide(true);', {}),
    'scaffold erased, body untouched': ('s.eraseScaffoldSide();', {}),
    'tissue added': ('s.addPatch();', {}),
    'part removed, scaffold term off': ('s.removeSide(false);', {'scaffold': False}),
    'inhibitor switched off': ('', {'inhibitor': False}),
}

with tempfile.TemporaryDirectory() as tmp:
    runner = f"""
      const T = require({json.dumps(str(PORT))}), fs = require('fs'), tmp = {json.dumps(tmp)};
      const dump = (s, name) => {{ fs.writeFileSync(`${{tmp}}/${{name}}_B.bin`, Buffer.from(s.body().buffer.slice(0))); fs.writeFileSync(`${{tmp}}/${{name}}_M.bin`, Buffer.from(s.scaffold().buffer.slice(0))); }};
      const base = T.create(1); for (let t = 0; t < 500; t++) base.step({{ noise: false }});
      const scenarios = {json.dumps({k: [v[0], v[1]] for k, v in SCENARIOS.items()})};
      let i = 0;
      for (const [name, [op, opts]] of Object.entries(scenarios)) {{
        const s = base.clone(); eval(op); dump(s, 'start' + i);
        for (let t = 0; t < {STEPS}; t++) s.step(Object.assign({{ noise: false }}, opts));
        dump(s, 'end' + i); i++;
      }}
      // Part 2: the published protocol with the port's own noise
      const rows = [];
      for (const seed of {json.dumps(SEEDS)}) {{
        const pre = T.create(seed); for (let t = 0; t < 2000; t++) pre.step({{}});
        const m0 = pre.measure();
        const arms = {{ sham: '', remove: 's.removeSide(false);', remove_erase: 's.removeSide(true);', erase_only: 's.eraseScaffoldSide();', add: 's.addPatch();' }};
        const end = {{}};
        for (const [arm, op] of Object.entries(arms)) {{
          const s = pre.clone(seed + 1000); eval(op); const start = s.measure().mass;
          for (let t = 0; t < 5000; t++) s.step({{}});
          const m = s.measure(); end[arm] = {{ start, mass: m.mass, shift: Math.hypot(m.cx - m0.cx, m.cy - m0.cy), wall: m.atWall }};
        }}
        for (const arm of Object.keys(arms)) rows.push([seed, arm, end[arm].start / m0.mass, end[arm].mass / end.sham.mass, end[arm].shift, end[arm].wall, end.sham.mass / m0.mass]);
      }}
      fs.writeFileSync(tmp + '/rows.json', JSON.stringify(rows));
    """
    subprocess.run(['node', '-e', runner], check=True)
    load = lambda name: np.fromfile(f'{tmp}/{name}.bin').reshape(G, G)

    print(f'Original: {ORIGINAL.name}     Port: {PORT.name}\n')
    print(f'PART 1. The rule with noise off: {STEPS:,} steps from an identical saved state')
    print(f"   {'scenario':<38}{'largest difference, body':>26}{'scaffold':>12}{'body mass, port / original':>32}")
    rng = np.random.default_rng(0)
    worst = 0.0
    for i, (name, (_, opts)) in enumerate(SCENARIOS.items()):
        B, M = load(f'start{i}_B').copy(), load(f'start{i}_M').copy()
        P = dict(tenax.P0, noise=0.0)
        if opts.get('scaffold') is False: P['m'] = 0.0
        if opts.get('inhibitor') is False: P['g'] = 0.0
        for _ in range(STEPS):
            B, M = tenax.step(B, M, P, rng)
        jb, jm = load(f'end{i}_B'), load(f'end{i}_M')
        db, dm = float(np.abs(B - jb).max()), float(np.abs(M - jm).max())
        worst = max(worst, db, dm)
        print(f'   {name:<38}{db:>26.3e}{dm:>12.3e}{jb.sum():>18.3f} / {B.sum():.3f}')
    rows = json.loads(Path(tmp, 'rows.json').read_text())

print(f'\n   Largest difference in any cell of any scenario: {worst:.3e}')

print(f'\nPART 2. Behaviour with noise on: the port on {len(SEEDS)} seeds of its own, against the published 12 seeds')
published = {r['arm']: r for r in csv.DictReader(open(SUMMARY))}
pairs = [('remove', 'amputate', 'part removed, scaffold intact'), ('remove_erase', 'amputate_wipe', 'part removed, scaffold erased there'),
         ('erase_only', 'wipe_only', 'scaffold erased, body untouched'), ('add', 'graft', 'tissue added')]
print(f"   {'':<38}{'size at end / untouched twin':>44}{'distance from start, cells':>40}")
print(f"   {'':<38}{'port':>22}{'published':>22}{'port':>20}{'published':>20}")
for js_arm, py_arm, label in pairs:
    r = np.array([[x[3], x[4]] for x in rows if x[1] == js_arm])
    p = published[py_arm]
    print(f"   {label:<38}{r[:,0].mean():>14.3f} ({r[:,0].min():.3f}-{r[:,0].max():.3f})"
          f"{float(p['mass_over_sham_end_mean']):>12.3f} ({float(p['min']):.3f}-{float(p['max']):.3f})"
          f"{r[:,1].mean():>20.2f}{float(p['centroid_shift_end_mean']):>20.2f}")
start = {a: np.mean([x[2] for x in rows if x[1] == a]) for a in ('remove', 'add')}
drift = np.mean([x[6] for x in rows if x[1] == 'sham'])
print(f"\n   Fraction left after the removal: {start['remove']:.3f} (published 0.622).  Size just after adding: {start['add']:.3f} (published 1.190).")
print(f"   Untouched twin, size at end / size at start: {drift:.4f} (published 1.0471; the port starts already settled).")
print(f"   Scaffold intact ended closer to its start than scaffold erased in {sum(a[4] < b[4] for a, b in zip([x for x in rows if x[1]=='remove'], [x for x in rows if x[1]=='remove_erase']))} of {len(SEEDS)} seeds.")
print(f"   Any body touching a wall: {any(x[5] for x in rows)}")
print('\nVERDICT (part 1):', 'the port follows the original rule to within floating-point rounding' if worst < 1e-6 else 'THE RULES DIFFER')
