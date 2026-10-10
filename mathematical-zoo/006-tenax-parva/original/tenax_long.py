"""Long follow-up check for tenax.py: does the slow arm ever get there, and has the sham stopped drifting?"""
from multiprocessing import Pool
import numpy as np
import tenax
tenax.T_POST = 25000
def job(s):
    r = tenax.trial((s, tenax.P0, ['sham', 'amputate', 'amputate_wipe', 'wipe_only'], 'right', False))
    return r
if __name__ == '__main__':
    with Pool(2) as p: res = p.map(job, [0, 1, 2, 3])
    idx = [0, 100, 200, 300, 400, 500]
    print('steps', [i * tenax.REC for i in idx])
    print('sham mass / start     ', np.round(np.mean([[r['series']['sham'][i][1] / r['m0'] for i in idx] for r in res], 0), 4))
    for a in ('amputate', 'amputate_wipe', 'wipe_only'):
        print(f'{a:14s} mass/sham', np.round(np.mean([tenax.ratio(r, a)[idx] for r in res], 0), 4), ' shift', np.round(np.mean([[r['series'][a][i][2] for i in idx] for r in res], 0), 2))
