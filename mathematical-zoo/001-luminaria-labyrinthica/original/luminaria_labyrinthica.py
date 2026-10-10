"""Reproducible Gray–Scott reaction–diffusion experiment: Luminaria labyrinthica.
Run: python luminaria_labyrinthica.py
Requires numpy and matplotlib. All numbers below are explicit experimental settings.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

OUT = Path(__file__).resolve().parent
N = 220
STEPS = 6000
SEED = 42
DU, DV = 0.16, 0.08
FEED, KILL = 0.035, 0.062
DT = 1.0
SNAPSHOT_STEPS = (500, 1500, 6000)


def laplacian(a):
    """Five-point finite difference, with wraparound/periodic boundary."""
    return (np.roll(a, 1, 0) + np.roll(a, -1, 0)
            + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4*a)


def main():
    rng = np.random.default_rng(SEED)
    u = np.ones((N, N), dtype=np.float64)
    v = np.zeros((N, N), dtype=np.float64)
    yy, xx = np.ogrid[:N, :N]
    for _ in range(12):
        x, y = rng.integers(20, N-20, size=2)
        radius = rng.integers(3, 9)
        patch = (xx-x)**2 + (yy-y)**2 <= radius**2
        u[patch] = 0.50 + rng.uniform(-0.04, 0.04)
        v[patch] = 0.25 + rng.uniform(-0.03, 0.03)

    frames = {}
    for step in range(1, STEPS + 1):
        uvv = u*v*v
        du = DU*laplacian(u) - uvv + FEED*(1-u)
        dv = DV*laplacian(v) + uvv - (FEED+KILL)*v
        u += DT*du
        v += DT*dv
        if step in SNAPSHOT_STEPS:
            frames[step] = v.copy()

    cmap = LinearSegmentedColormap.from_list(
        'luminaria', ['#10151d', '#232d40', '#44556a', '#719e9e', '#d6d5b0', '#f4e7c2'])
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.9), dpi=150, constrained_layout=True)
    for ax, step in zip(axes, SNAPSHOT_STEPS):
        ax.imshow(frames[step], cmap=cmap, vmin=0, vmax=0.35, interpolation='nearest')
        ax.set_title(f'Step {step:,}')
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle('SPECIMEN 001 / A WORLD WITH NO BLUEPRINT', fontsize=16)
    output = OUT/'luminaria_labyrinthica_reproduced.png'
    fig.savefig(output, dpi=160, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved {output}')
    print(f'Final concentration of V: minimum={v.min():.6f}, maximum={v.max():.6f}, mean={v.mean():.6f}')


if __name__ == '__main__':
    main()
