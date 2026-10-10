"""Luminaria III: is the 'migration' caused by the nutrient source moving?  By Claude.

The III source file was not preserved, but its protocol lists the same parameters as Luminaria V,
and V's injured-with-memory arm reproduces III's reported numbers, so this uses V's update rule.

Run:  python claude_migration_check.py     (NumPy only; under a minute)
"""
import numpy as np

P = dict(n_diff=.16, n_keep=.994, src_add=.09, cons=.018, m_keep=.986, m_add=.06, flow=.032, growth=.16, gthr=.12, gbase=.26,
         gN=2., memreg=.14, mthr=.09, mbase=.14, persist=.085, pthr=.08, decay=.030, dbase=.14, dthr=.07, spread=.022, cut=.007)
G = 180
Y, X = np.mgrid[:G, :G]
LEFT = ((X - 24) ** 2 + (Y - 90) ** 2 <= 13 ** 2)
RIGHT = ((X - 156) ** 2 + (Y - 90) ** 2 <= 13 ** 2)


def shift(a, s, ax, wraps):
    r = np.roll(a, s, ax)
    if not wraps:  # walled edge: copy the edge value instead of wrapping round
        i = [slice(None)] * 2
        i[ax] = 0 if s == 1 else -1
        r[tuple(i)] = a[tuple(i)]
    return r


def step(B, N, M, t, wraps=True, switch=250, source=True):
    nbrs = lambda a: shift(a, 1, 0, wraps) + shift(a, -1, 0, wraps) + shift(a, 1, 1, wraps) + shift(a, -1, 1, wraps)
    N = (N + P['n_diff'] * (nbrs(N) - 4 * N)) * P['n_keep']
    if source:
        N[LEFT if t <= switch else RIGHT] += P['src_add']
    N = np.clip(N - P['cons'] * B * N, 0, 1.5)
    M = np.clip(P['m_keep'] * M + P['m_add'] * B, 0, 1)
    nb = .40 * B + .15 * nbrs(B)
    grad = .5 * (shift(N, -1, 1, wraps) - shift(N, 1, 1, wraps))
    growth = P['growth'] * (1 - B) * np.maximum(nb - P['gthr'], 0) * (P['gbase'] + P['gN'] * N)
    reg = P['memreg'] * (1 - B) * M * np.maximum(nb - P['mthr'], 0) * (P['mbase'] + N)
    persist = P['persist'] * B * np.maximum(nb - P['pthr'], 0)
    decay = P['decay'] * B * (P['dbase'] + np.maximum(0, P['dthr'] - N))
    B = np.clip(B + growth + reg + persist + P['spread'] * (nbrs(B) - 4 * B) - decay + P['flow'] * grad * B, 0, 1)
    B[B < P['cut']] = 0
    return B, N, M


def run(**kw):
    B = np.zeros((G, G)); B[(X - 40) ** 2 + (Y - 90) ** 2 <= 12 ** 2] = .92
    N = np.zeros_like(B); M = np.zeros_like(B); out = {}
    for t in range(1, 621):
        B, N, M = step(B, N, M, t, **kw)
        if t == 370:
            B[74:106, 52:84] = 0
        if t in (250, 430, 520, 620):
            out[t] = ((B * X).sum() / B.sum(), B.sum(), B[:, 150:].sum(), B[74:106, 52:84].mean())
    return out


if __name__ == '__main__':
    for name, kw in [('as published (source moves at 250, grid wraps)', {}), ('source never moves', dict(switch=10 ** 9)),
                     ('no nutrient source at all', dict(source=False)), ('walled grid, source moves', dict(wraps=False)),
                     ('walled grid, source never moves', dict(wraps=False, switch=10 ** 9))]:
        o = run(**kw)
        print(f"{name:47s} centre x at 250: {o[250][0]:.2f}, at 520: {o[520][0]:.2f}, shift {o[520][0] - o[250][0]:+.2f} | "
              f"at 620: wound {o[620][3]:.3f}, mass {o[620][1]:.2f}, mass beyond x=150: {o[620][2]:.1f}")
