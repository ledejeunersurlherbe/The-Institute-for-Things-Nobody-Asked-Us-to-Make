"""Figure for tenax.py.  Reads tenax_plotdata.npz, writes tenax_figure.png."""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
BLUE, ORANGE, AQUA, YELLOW, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#6250d6'
TISSUE = LinearSegmentedColormap.from_list('tissue', [SURF, '#cde2fb', '#5598e7', '#0d366b'])


def style(ax, title, xlabel, ylabel):
    ax.set_facecolor(SURF)
    ax.set_title(title, loc='left', fontsize=11, color=INK, pad=10)
    ax.set_xlabel(xlabel, fontsize=9, color=INK2); ax.set_ylabel(ylabel, fontsize=9, color=INK2)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(color=GRID, linewidth=.8); ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)


def band(ax, t, arr, color, label, ls='-', dy=0):
    mu, sd = arr.mean(0), arr.std(0)
    ax.fill_between(t, mu - sd, mu + sd, color=color, alpha=.15, linewidth=0)
    ax.plot(t, mu, color=color, linewidth=2, linestyle=ls, label=label)
    return mu


def draw(out):
    d = np.load(Path(out) / 'tenax_plotdata.npz')
    t = d['t']
    fig = plt.figure(figsize=(12.5, 8.2), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 6, height_ratios=[1, .78], hspace=.5, wspace=.12, left=.06, right=.97, top=.89, bottom=.06)
    fig.suptitle('Tenax parva: the body defends its size; the scaffold decides where it regrows',
                 x=.06, ha='left', fontsize=13, color=INK, fontweight='bold')

    gs0 = gs[0, :].subgridspec(1, 2, wspace=.16)
    ax = fig.add_subplot(gs0[0])
    style(ax, 'Body size after perturbation (12 seeds, mean and 1 sd)', 'steps after perturbation', 'mass relative to paired sham')
    ax.axhspan(.95, 1.05, color=GRID, alpha=.7, linewidth=0)
    ax.text(t[-1], 1.058, 'within 5% of sham', ha='right', va='bottom', fontsize=7.5, color=INK2)
    band(ax, t, d['mass_amputate'], BLUE, 'amputated, scaffold intact')
    band(ax, t, d['mass_amputate_wipe'], ORANGE, 'amputated, scaffold erased')
    band(ax, t, d['mass_graft'], AQUA, 'grafted (tissue added)')
    ko = d['mass_inhibitor_off'].mean(0)
    ax.plot(t, ko, color=YELLOW, linewidth=2, label='inhibitor switched off')
    ax.set_ylim(.5, 1.6); ax.set_xlim(0, t[-1])
    i = int(np.argmax(ko > 1.6))
    ax.annotate(f'keeps growing\n(x{ko[-1]:.0f} by the end)', xy=(t[i], 1.6), xytext=(t[i] + 260, 1.47), fontsize=8, color=INK2,
                arrowprops=dict(arrowstyle='-', color=INK2, linewidth=.8))
    ax.legend(frameon=False, fontsize=8, loc='upper center', bbox_to_anchor=(.5, -.16), labelcolor=INK, ncol=2)

    ax = fig.add_subplot(gs0[1])
    style(ax, 'Distance from the old position (12 seeds, mean and 1 sd)', 'steps after perturbation', 'centroid shift, cells')
    band(ax, t, d['shift_amputate'], BLUE, 'amputated, scaffold intact')
    band(ax, t, d['shift_amputate_wipe'], ORANGE, 'amputated, scaffold erased')
    band(ax, t, d['shift_no_scaffold'], VIOLET, 'amputated, scaffold term off', ls='--')
    band(ax, t, d['shift_wipe_only'], AQUA, 'scaffold erased, tissue untouched')
    ax.set_xlim(0, t[-1]); ax.set_ylim(0, None)
    ax.legend(frameon=False, fontsize=8, loc='upper center', bbox_to_anchor=(.5, -.16), labelcolor=INK, ncol=2)

    foot = d['foot'].astype(float)
    panels = [('before', d['pre']), ('just after amputation', d['snap_amputate'][0]),
              ('5,000 steps later\nscaffold intact', d['snap_amputate'][1]), ('5,000 steps later\nscaffold erased', d['snap_amputate_wipe'][1]),
              ('graft, just after', d['snap_graft'][0]), ('graft, 5,000 steps later', d['snap_graft'][1])]
    for j, (ttl, img) in enumerate(panels):
        ax = fig.add_subplot(gs[1, j])
        ax.imshow(img, cmap=TISSUE, vmin=0, vmax=1, interpolation='nearest')
        ax.contour(foot, levels=[.5], colors=[ORANGE], linewidths=1.1, linestyles='--')
        ax.set_title(ttl, fontsize=8.5, color=INK, pad=5)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(GRID)
    fig.text(.06, .015, 'One seed shown. Dashed outline: the footprint before perturbation. The frame is the whole walled grid.', fontsize=8, color=INK2)
    fig.savefig(Path(out) / 'tenax_figure.png', facecolor=SURF)
    plt.close(fig)


if __name__ == '__main__':
    draw(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent)
