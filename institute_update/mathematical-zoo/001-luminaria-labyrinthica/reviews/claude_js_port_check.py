"""Does the lobby's JavaScript port of Specimen 001 follow the same trajectory as Morrow's original?

Requested by Morrow. Matching equations, seeds and parameters is not proof of matching trajectories,
so this compares the actual numbers.

Python side: Morrow's original script is imported and its own main() is run, unmodified. Only the
plotting library is swapped for a stand-in that catches the three arrays main() hands to imshow
(the V field at steps 500, 1,500 and 6,000), so the arrays compared are the ones the original computed.

JavaScript side: lobby/specimen001.js, the file the website runs, is executed with Node and its
V field is dumped at the same three steps.

Run from anywhere:  python claude_js_port_check.py      (needs NumPy, Matplotlib and Node.js)
"""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'original' / 'luminaria_labyrinthica.py'
PORT = HERE.parents[2] / 'lobby' / 'specimen001.js'
STEPS = (500, 1500, 6000)

# ---- Python: run the original's own main() and catch what it draws
spec = importlib.util.spec_from_file_location('original_specimen', ORIGINAL)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
caught = []


class Axis:
    def imshow(self, array, **kw): caught.append(np.array(array, dtype=np.float64))
    def __getattr__(self, name): return lambda *a, **k: None


class Figure:
    def __getattr__(self, name): return lambda *a, **k: None


class Plotting:
    def subplots(self, rows, cols, **kw): return Figure(), [Axis() for _ in range(rows * cols)]
    def close(self, *a, **k): pass


original.plt = Plotting()
original.main()
assert len(caught) == 3 and tuple(original.SNAPSHOT_STEPS) == STEPS

# ---- JavaScript: run the website's file and dump the same three steps
with tempfile.TemporaryDirectory() as tmp:
    runner = f"""
      const s = require({json.dumps(str(PORT))}).create();
      const fs = require('fs');
      for (const n of {list(STEPS)}) {{ s.advance(n - s.step()); fs.writeFileSync({json.dumps(tmp)} + '/v' + n + '.bin', Buffer.from(s.field().buffer.slice(0))); }}
    """
    subprocess.run(['node', '-e', runner], check=True)
    js = [np.fromfile(f'{tmp}/v{n}.bin', dtype=np.float64).reshape(original.N, original.N) for n in STEPS]

# ---- Compare
print(f'Original: {ORIGINAL.name}  (N={original.N}, Du={original.DU}, Dv={original.DV}, feed={original.FEED}, kill={original.KILL}, seed={original.SEED})')
print(f'Port:     {PORT.name}\n')
print(f"{'step':>6} {'largest difference':>20} {'mean difference':>17} {'correlation':>13} {'cells differing in displayed colour':>37}")
worst = 0.0
for n, py, j in zip(STEPS, caught, js):
    d = np.abs(py - j)
    shade = lambda a: np.clip(np.round(a / 0.35 * 255), 0, 255)     # the 256 colour steps the lobby draws with
    print(f'{n:>6} {d.max():>20.3e} {d.mean():>17.3e} {np.corrcoef(py.ravel(), j.ravel())[0, 1]:>13.9f} {int((shade(py) != shade(j)).sum()):>37}')
    worst = max(worst, d.max())
print(f'\nFinal V field, original: min={caught[-1].min():.6f} max={caught[-1].max():.6f} mean={caught[-1].mean():.6f}')
print(f'Final V field, port:     min={js[-1].min():.6f} max={js[-1].max():.6f} mean={js[-1].mean():.6f}')
print(f'\nLargest difference anywhere, at any checked step: {worst:.3e}')
print('VERDICT:', 'identical to the last bit at every checked step' if worst == 0 else 'same trajectory to within floating-point rounding' if worst < 1e-9 else 'TRAJECTORIES DIFFER')
