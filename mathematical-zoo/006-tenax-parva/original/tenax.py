"""Tenax parva: a size-regulating body with a positional scaffold.

Run:  python tenax.py            (NumPy, SciPy, Matplotlib; about 7 minutes on 2 cores)
Writes tenax_timeseries.csv, tenax_summary.csv, tenax_robustness.csv, tenax_figure.png

MODEL (128 x 128 grid, walled edges, nothing wraps)
  B  tissue, 0..1
  H  inhibitor made by tissue, spreading over length L:  H = B + L^2 lap(H)   (solved exactly each step)
  M  scaffold, a slow record of where tissue has been:   dM/dt = (B - M) / tau
  dB/dt = D lap(B) + r B (1-B) (B - theta) + noise,   theta = a + g H - m (M - B)
Tissue advances where theta < 1/2 and retreats where theta > 1/2.  The inhibitor raises theta as the
body gets bigger, so growth stops at a set size.  The scaffold term is zero whenever tissue matches
the record (M = B), so it cannot change the set size; it only acts where the two disagree.

PREDICTIONS, written before the runs
  H1 size:     amputated and grafted bodies both return to within 5% of their paired sham's mass,
               and a body whose inhibitor is switched off does not.
  H2 position: after amputation, a body with its scaffold intact ends closer to its old position
               (smaller centroid shift, higher overlap with the old footprint) than one whose
               scaffold was erased in the removed region.
"""
import csv
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.fft import dctn, idctn

OUT = Path(__file__).resolve().parent
G = 128
_k = np.pi * np.arange(G) / G
LAM = (2 - 2 * np.cos(_k))[:, None] + (2 - 2 * np.cos(_k))[None, :]
Y, X = np.mgrid[:G, :G]
P0 = dict(a=.2, g=1., L=25., D=.2, r=.06, m=.2, tau=1000., noise=.02)
T_EQ, T_POST, REC = 8000, 5000, 50
SEEDS = list(range(12))


def inhibitor(B, L):
    return idctn(dctn(B, type=2, norm='ortho') / (1 + L * L * LAM), type=2, norm='ortho')


def lap(a):
    p = np.pad(a, 1, mode='edge')
    return p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:] - 4 * a


def step(B, M, P, rng):
    theta = P['a'] + P['g'] * inhibitor(B, P['L']) - P['m'] * (M - B)
    B = B + P['D'] * lap(B) + P['r'] * B * (1 - B) * (B - theta) + P['noise'] * rng.standard_normal(B.shape) * B * (1 - B)
    B = np.clip(B, 0, 1)
    return B, M + (B - M) / P['tau']


def com(B):
    s = B.sum()
    return ((B * X).sum() / s, (B * Y).sum() / s) if s > 1 else (np.nan, np.nan)


def equilibrate(seed, P):
    rng = np.random.default_rng(seed)
    cx, cy = 64 + rng.uniform(-4, 4, 2)
    rx, ry = rng.uniform(18, 30, 2)
    B = ((X - cx) ** 2 / rx ** 2 + (Y - cy) ** 2 / ry ** 2 <= 1) * 1.
    M = np.zeros_like(B)
    for _ in range(T_EQ):
        B, M = step(B, M, P, rng)
    return B, M


def follow(B, M, P, seed, ref):
    """Run T_POST steps.  Every arm of a seed uses the same noise stream, so arms are paired."""
    rng = np.random.default_rng(seed + 10_000)
    m0, cx, cy, foot = ref
    rows = []
    for t in range(0, T_POST + 1):
        if t:
            B, M = step(B, M, P, rng)
        if t % REC == 0:
            f = B > .5
            x, y = com(B)
            rows.append((t, B.sum(), np.hypot(x - cx, y - cy), (f & foot).sum() / max((f | foot).sum(), 1), f[[0, -1], :].any() or f[:, [0, -1]].any()))
    return rows, B


WOUNDS = {
    'right': lambda cx, cy: X > cx + 5,
    'top': lambda cx, cy: Y < cy - 5,
    'diagonal': lambda cx, cy: (X - cx) + (Y - cy) > 8,
    'hole': lambda cx, cy: (X - cx) ** 2 + (Y - cy) ** 2 <= 12 ** 2,
    'notch': lambda cx, cy: (np.abs(Y - cy) < 7) & (X > cx),
}


def trial(job):
    """One seed, one parameter set, a list of arms.  Returns per-arm time series plus snapshots."""
    seed, P, arms, wound, snaps = job
    B, M = equilibrate(seed, P)
    m0 = B.sum()
    if m0 < 50:
        return dict(seed=seed, viable=False, wound=wound)
    cx, cy = com(B)
    foot = B > .5
    ref = (m0, cx, cy, foot)
    cut = WOUNDS[wound](cx, cy)
    graft = (X - (cx + 25)) ** 2 + (Y - cy) ** 2 <= 14 ** 2
    Bc = B.copy(); Bc[cut] = 0
    Mw = M.copy(); Mw[cut] = 0
    start = {
        'sham': (B, M, P),
        'amputate': (Bc, M, P),                       # scaffold intact
        'amputate_wipe': (Bc, Mw, P),                 # scaffold erased where tissue was removed
        'wipe_only': (B, Mw, P),                      # scaffold erased, tissue untouched
        'graft': (np.maximum(B, graft * 1.), M, P),   # extra tissue added
        'no_scaffold': (Bc, M, dict(P, m=0.)),        # amputate with the scaffold term off everywhere
        'inhibitor_off': (B, M, dict(P, g=0.)),
    }
    res = dict(seed=seed, viable=True, wound=wound, m0=m0, removed=B[cut].sum() / m0, added=(np.maximum(B, graft * 1.).sum() - m0) / m0, series={}, snaps={})
    if snaps:
        res['snaps']['pre'] = B.copy(); res['snaps']['foot'] = foot
    for arm in arms:
        Bi, Mi, Pi = start[arm]
        rows, Bend = follow(Bi.copy(), Mi.copy(), Pi, seed, ref)
        res['series'][arm] = rows
        if snaps:
            res['snaps'][arm] = (Bi.copy(), Bend)
    return res


def ratio(res, arm, col=1):
    return np.array([r[col] for r in res['series'][arm]]) / np.array([r[col] for r in res['series']['sham']])


def main():
    all_arms = ['sham', 'amputate', 'amputate_wipe', 'wipe_only', 'graft', 'no_scaffold', 'inhibitor_off']
    core = ['sham', 'amputate', 'amputate_wipe', 'graft']
    rng = np.random.default_rng(2026)
    jitter = [{k: v * rng.uniform(.9, 1.1) for k, v in P0.items()} for _ in range(20)]
    jobs = [(s, P0, all_arms, 'right', s == 0) for s in SEEDS]
    jobs += [(100 + i, P, core, 'right', False) for i, P in enumerate(jitter)]
    jobs += [(200 + s, P0, ['sham', 'amputate', 'amputate_wipe'], w, False) for w in ('top', 'diagonal', 'hole', 'notch') for s in range(4)]
    with Pool(2) as pool:
        results = pool.map(trial, jobs, chunksize=1)
    main_res, jit_res, geo_res = results[:12], results[12:32], results[32:]

    # ---- time series and summary for the main experiment
    with open(OUT / 'tenax_timeseries.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['seed', 'arm', 'step', 'mass', 'mass_over_sham', 'centroid_shift', 'overlap_with_old_footprint', 'touches_wall'])
        for r in main_res:
            for arm, rows in r['series'].items():
                rat = ratio(r, arm)
                for row, q in zip(rows, rat):
                    w.writerow([r['seed'], arm, row[0], f'{row[1]:.3f}', f'{q:.4f}', f'{row[2]:.3f}', f'{row[3]:.4f}', int(row[4])])
    summ = []
    print(f"set-point mass across seeds: mean {np.mean([r['m0'] for r in main_res]):.0f}, sd {np.std([r['m0'] for r in main_res]):.0f}; "
          f"removed {np.mean([r['removed'] for r in main_res]):.2f}, grafted {np.mean([r['added'] for r in main_res]):.2f} of body")
    print(f"sham drift over the follow-up (end mass / start mass): {np.mean([r['series']['sham'][-1][1] / r['m0'] for r in main_res]):.4f}")
    for arm in all_arms:
        e = np.array([[ratio(r, arm)[-1], r['series'][arm][-1][2], r['series'][arm][-1][3], ratio(r, arm)[0], r['series'][arm][-1][4]] for r in main_res])
        summ.append([arm, len(e)] + [f'{v:.4f}' for v in (e[:, 3].mean(), e[:, 0].mean(), e[:, 0].std(), e[:, 0].min(), e[:, 0].max(), e[:, 1].mean(), e[:, 1].std(), e[:, 2].mean(), e[:, 2].std())] + [int(e[:, 4].sum())])
        print(f"{arm:14s} mass/sham start {e[:,3].mean():.3f} -> end {e[:,0].mean():.3f} (sd {e[:,0].std():.3f}, range {e[:,0].min():.3f}-{e[:,0].max():.3f}) | shift {e[:,1].mean():.2f} (sd {e[:,1].std():.2f}) | overlap {e[:,2].mean():.3f} (sd {e[:,2].std():.3f}) | at wall {int(e[:,4].sum())}/12")
    with open(OUT / 'tenax_summary.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['arm', 'n_seeds', 'mass_over_sham_start', 'mass_over_sham_end_mean', 'sd', 'min', 'max', 'centroid_shift_end_mean', 'sd', 'overlap_end_mean', 'sd', 'seeds_touching_wall']); w.writerows(summ)
    sh = lambda arm: np.array([r['series'][arm][-1][2] for r in main_res])
    ov = lambda arm: np.array([r['series'][arm][-1][3] for r in main_res])
    print(f"H2 paired: scaffold intact closer to old position in {(sh('amputate') < sh('amputate_wipe')).sum()}/12 seeds; "
          f"mean shift difference {np.mean(sh('amputate_wipe') - sh('amputate')):.2f} cells; higher overlap in {(ov('amputate') > ov('amputate_wipe')).sum()}/12")
    # time to recover to within 5% of sham
    for arm in ('amputate', 'amputate_wipe', 'no_scaffold', 'graft'):
        ts = []
        for r in main_res:
            q = np.abs(ratio(r, arm) - 1) <= .05
            ok = [i for i in range(len(q)) if q[i:].all()]
            ts.append(ok[0] * REC if ok else np.nan)
        print(f"  {arm:14s} steps until within 5% of sham and staying there: median {np.nanmedian(ts):.0f}, never in {int(np.isnan(ts).sum())}/12")

    # ---- robustness
    rob = []
    for r, P in zip(jit_res, jitter):
        if not r['viable']:
            rob.append(['jitter', r['seed'], 'right', 0] + [''] * 7); continue
        wall = any(r['series'][a][-1][4] for a in core)
        rob.append(['jitter', r['seed'], 'right', 1, f"{r['m0']:.0f}", f"{ratio(r,'amputate')[-1]:.4f}", f"{ratio(r,'amputate_wipe')[-1]:.4f}", f"{ratio(r,'graft')[-1]:.4f}", f"{r['series']['amputate'][-1][2]:.2f}", f"{r['series']['amputate_wipe'][-1][2]:.2f}", int(wall)])
    for r in geo_res:
        rob.append(['geometry', r['seed'], r['wound'], 1, f"{r['m0']:.0f}", f"{ratio(r,'amputate')[-1]:.4f}", f"{ratio(r,'amputate_wipe')[-1]:.4f}", '', f"{r['series']['amputate'][-1][3]:.3f}", f"{r['series']['amputate_wipe'][-1][3]:.3f}", f"{r['removed']:.2f}"])
    with open(OUT / 'tenax_robustness.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['set', 'seed', 'wound', 'viable', 'set_point_mass', 'amputate_mass_over_sham_end', 'amputate_wipe_mass_over_sham_end', 'graft_mass_over_sham_end', 'amputate: shift (jitter) or overlap (geometry)', 'amputate_wipe: same', 'touches_wall (jitter) or removed fraction (geometry)']); w.writerows(rob)
    v = [r for r in jit_res if r['viable']]
    a = np.array([[ratio(r, 'amputate')[-1], ratio(r, 'amputate_wipe')[-1], ratio(r, 'graft')[-1], r['series']['amputate'][-1][2], r['series']['amputate_wipe'][-1][2], r['m0'], any(r['series'][x][-1][4] for x in core)] for r in v])
    print(f"jitter +-10% on all 8 parameters: {len(v)}/20 viable; set-point mass {a[:,5].min():.0f}-{a[:,5].max():.0f}; touching wall {int(a[:,6].sum())}")
    print(f"  within 5% of sham at end: amputate {(np.abs(a[:,0]-1)<=.05).sum()}/{len(v)}, graft {(np.abs(a[:,2]-1)<=.05).sum()}/{len(v)}; ranges amp {a[:,0].min():.3f}-{a[:,0].max():.3f}, graft {a[:,2].min():.3f}-{a[:,2].max():.3f}")
    print(f"  scaffold intact closer than wiped: {(a[:,3] < a[:,4]).sum()}/{len(v)}; median shift {np.median(a[:,3]):.2f} vs {np.median(a[:,4]):.2f}")
    for wd in ('top', 'diagonal', 'hole', 'notch'):
        g = [r for r in geo_res if r['wound'] == wd]
        print(f"  wound {wd:9s} removed {np.mean([r['removed'] for r in g]):.2f}: mass/sham end {np.mean([ratio(r,'amputate')[-1] for r in g]):.3f} / wiped {np.mean([ratio(r,'amputate_wipe')[-1] for r in g]):.3f}; "
              f"overlap {np.mean([r['series']['amputate'][-1][3] for r in g]):.3f} vs wiped {np.mean([r['series']['amputate_wipe'][-1][3] for r in g]):.3f}; "
              f"intact better in {sum(r['series']['amputate'][-1][3] > r['series']['amputate_wipe'][-1][3] for r in g)}/4")
    np.savez_compressed(OUT / 'tenax_plotdata.npz', t=np.array([r[0] for r in main_res[0]['series']['sham']]),
                        **{f'mass_{a_}': np.array([ratio(r, a_) for r in main_res]) for a_ in all_arms},
                        **{f'shift_{a_}': np.array([[x[2] for x in r['series'][a_]] for r in main_res]) for a_ in all_arms},
                        pre=main_res[0]['snaps']['pre'], foot=main_res[0]['snaps']['foot'],
                        **{f'snap_{a_}': np.array(main_res[0]['snaps'][a_]) for a_ in all_arms})


if __name__ == '__main__':
    main()
    if '--no-figure' not in sys.argv:
        import tenax_figure
        tenax_figure.draw(OUT)
