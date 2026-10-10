#!/usr/bin/env python3
"""Thirty-two Clocks: reproducible Kuramoto oscillator choir.

The simulation drives note onset times. Pitches are assigned independently of
oscillator frequencies, so the sound represents *temporal phase coordination*,
not a biological or cognitive process. No external dependencies beyond NumPy,
SciPy and Matplotlib.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SEED = 10102026
N = 32
DURATION = 105.0
DT = 0.005
SR = 22050


def coupling(t: float) -> float:
    if t < 22: return 0.0
    if t < 35: return (t - 22) / 13 * 1.0
    if t < 48: return 1.0
    if t < 60: return 1.0 + (t - 48) / 12 * 2.0
    if t < 80: return 3.0
    if t < 85: return 3.0 * (85 - t) / 5
    return 0.0


def simulate(force_uncoupled=False, seed=SEED):
    rng = np.random.default_rng(seed)
    # A wide but bounded range of natural frequencies; Hz is cycles per second.
    f = np.clip(rng.normal(0.80, 0.115, N), 0.55, 1.08)
    omega = 2 * np.pi * f
    phase = rng.uniform(0, 2 * np.pi, N)
    steps = int(round(DURATION / DT))
    ts = np.arange(steps + 1) * DT
    r = np.empty(steps + 1)
    psi = np.empty(steps + 1)
    # Event list of (time, oscillator id). Each wrap creates one note.
    events = []
    for i, t in enumerate(ts):
        z = np.mean(np.exp(1j * phase))
        r[i] = abs(z)
        psi[i] = np.angle(z)
        if i == steps: break
        k = 0.0 if force_uncoupled else coupling(t)
        # Mean-field Kuramoto: theta' = omega + K*r*sin(psi - theta).
        velocity = omega + k * np.imag(z * np.exp(-1j * phase))
        next_phase = phase + DT * velocity
        wrapped = np.flatnonzero(np.floor(next_phase / (2 * np.pi)) > np.floor(phase / (2 * np.pi)))
        for j in wrapped:
            # Linear interpolation within the timestep gives sample-accurate note timing.
            boundary = (np.floor(phase[j] / (2 * np.pi)) + 1) * (2 * np.pi)
            frac = (boundary - phase[j]) / (next_phase[j] - phase[j])
            events.append((t + float(frac) * DT, int(j)))
        phase = next_phase
    return ts, r, psi, f, events


def write_csv(path, headers, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def synthesize(events, f, output):
    """Gentle bell/chime sounds; no rhythmic quantization or manual time shifts."""
    rng = np.random.default_rng(SEED + 1)
    samples = int(np.ceil((DURATION + 1.0) * SR))
    left = np.zeros(samples, dtype=np.float32)
    right = np.zeros(samples, dtype=np.float32)
    # C minor pentatonic, across 2.5 octaves. One fixed note per oscillator.
    midi_choices = np.array([48, 51, 53, 55, 58, 60, 63, 65, 67, 70, 72, 75, 77, 79])
    midi = np.resize(midi_choices, N)
    rng.shuffle(midi)
    pitch_hz = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    pan = rng.uniform(-0.82, 0.82, N)
    lengths = np.clip(0.46 + 0.18 * (midi < 60), 0.46, 0.7)
    # Timbre, duration, and volume fixed per oscillator, independent of condition.
    voice_gain = rng.uniform(0.86, 1.10, N)
    for onset, j in events:
        duration = lengths[j]
        nn = int(duration * SR)
        start = int(onset * SR)
        if start >= samples: continue
        nn = min(nn, samples - start)
        t = np.arange(nn) / SR
        # Soft mallet with decaying inharmonic sparkle.
        env = (1 - np.exp(-t / 0.006)) * np.exp(-t / (duration * 0.31))
        freq = pitch_hz[j]
        tone = (np.sin(2 * np.pi * freq * t)
                + 0.22 * np.sin(2 * np.pi * 2.002 * freq * t + 0.4)
                + 0.075 * np.sin(2 * np.pi * 3.91 * freq * t + 1.2))
        s = (env * tone * voice_gain[j] / np.sqrt(N)).astype(np.float32)
        # Equal-power panning.
        angle = (pan[j] + 1) * np.pi / 4
        left[start:start+nn] += s * np.cos(angle)
        right[start:start+nn] += s * np.sin(angle)
    stereo = np.column_stack([left, right])
    # Gentle soft saturation with a *single* global gain, not per-section compression.
    stereo = np.tanh(stereo * 0.66)
    peak = float(np.max(np.abs(stereo)))
    stereo *= min(0.95 / peak, 1.0) if peak else 1.0
    wavfile.write(output, SR, (stereo * 32767).astype(np.int16))
    return {'peak': float(np.max(np.abs(stereo))), 'rms': float(np.sqrt(np.mean(stereo ** 2))),
            'events': len(events), 'bytes': output.stat().st_size,
            'midi_notes': [int(x) for x in midi]}


def main():
    ts, r, psi, f, events = simulate()
    _, r0, _, _, events0 = simulate(force_uncoupled=True)
    k = np.array([coupling(float(t)) for t in ts])
    write_csv(ROOT / 'order_parameter.csv', ['time_s', 'coupling_K', 'coherence_R', 'uncoupled_control_R'],
              zip(np.round(ts, 3), np.round(k, 5), np.round(r, 7), np.round(r0, 7)))
    write_csv(ROOT / 'note_events.csv', ['time_s', 'oscillator_id'],
              ((f'{t:.6f}', j) for t, j in events))
    write_csv(ROOT / 'oscillators.csv', ['oscillator_id', 'natural_frequency_hz'],
              ((i, f'{hz:.8f}') for i, hz in enumerate(f)))
    info = synthesize(events, f, ROOT / 'thirty_two_clocks.wav')
    info0 = synthesize(events0, f, ROOT / 'uncoupled_control.wav')
    intervals = [(0, 22, 'Independent'), (35, 48, 'Weak coupling'),
                 (62, 79, 'Strong coupling'), (93, 105, 'Released')]
    summaries = {}
    for lo, hi, label in intervals:
        mask = (ts >= lo) & (ts < hi)
        summaries[label] = {
            'time_window_s': [lo, hi],
            'mean_coherence': round(float(np.mean(r[mask])), 4),
            'mean_control_coherence': round(float(np.mean(r0[mask])), 4),
            'median_coherence': round(float(np.median(r[mask])), 4),
            'note_events': int(sum(lo <= t < hi for t, j in events))
        }
    # Robustness check: the finding should not depend on one lucky initial phase draw.
    sweep = []
    for seed in range(SEED, SEED + 12):
        st, sr, _, _, _ = simulate(seed=seed)
        _, cr, _, _, _ = simulate(force_uncoupled=True, seed=seed)
        strong = (st >= 62) & (st < 79)
        released = (st >= 93) & (st < 105)
        sweep.append((seed, float(np.mean(sr[strong])),
                      float(np.mean(cr[strong])), float(np.mean(sr[released]))))
    write_csv(ROOT / 'seed_sweep.csv',
              ['seed', 'strong_coupling_mean_R', 'control_mean_R', 'released_mean_R'],
              ((seed, f'{x:.6f}', f'{y:.6f}', f'{z:.6f}') for seed, x, y, z in sweep))
    assert all(x > 0.9 for _, x, _, _ in sweep)
    # Sanity check that changing coupling is causally necessary for coherence here.
    assert summaries['Strong coupling']['mean_coherence'] > 0.90
    assert summaries['Strong coupling']['mean_control_coherence'] < 0.4
    # Coherence line plot.
    fig, ax = plt.subplots(figsize=(11, 4.8), dpi=160)
    ax.plot(ts, r, label='Choir: varying coupling', lw=1.6)
    ax.plot(ts, r0, label='Control: no coupling', lw=1.0, alpha=0.75)
    ax.set(xlabel='Simulation time (seconds)', ylabel='Phase coherence R (0–1)',
           title='Thirty-two clocks: coordination emerges, then fades', ylim=(-0.02, 1.04), xlim=(0, 105))
    for t in [22, 35, 48, 60, 80, 85]: ax.axvline(t, color='gray', lw=0.5, alpha=0.25)
    ax.legend(loc='lower right')
    ax.grid(alpha=0.17)
    fig.tight_layout()
    fig.savefig(ROOT / 'coherence.png')
    plt.close(fig)
    # Each point is an actual crossing, not a smoothed/quantized visualization.
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=160)
    ax.scatter([t for t, j in events], [j for t, j in events], s=1.4, alpha=0.6)
    ax.set(xlabel='Simulation time (seconds)', ylabel='Oscillator number',
           title='Every dot is a note: independent rhythms gather into shared beats',
           xlim=(0, 105), ylim=(-1, N))
    ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(ROOT / 'event_raster.png')
    plt.close(fig)
    # Coupling is prescribed externally; label that clearly.
    fig, ax = plt.subplots(figsize=(11, 3), dpi=160)
    ax.plot(ts, k, lw=2)
    ax.set(xlabel='Simulation time (seconds)', ylabel='Coupling strength K',
           title='Experimental intervention: coupling is imposed, not learned',
           xlim=(0, 105), ylim=(-0.05, 3.15))
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(ROOT / 'coupling_protocol.png')
    plt.close(fig)
    output = {'name': 'Thirty-two Clocks', 'seed': SEED, 'N': N, 'duration_s': DURATION,
              'dt_s': DT, 'audio_sample_rate_hz': SR,
              'natural_frequency_range_hz': [round(float(f.min()), 4), round(float(f.max()), 4)],
              'condition_summaries': summaries,
              'robustness_12_seeds': {
                  'strong_coupling_mean_R_range': [round(min(x for _, x, _, _ in sweep), 4), round(max(x for _, x, _, _ in sweep), 4)],
                  'control_mean_R_range': [round(min(y for _, _, y, _ in sweep), 4), round(max(y for _, _, y, _ in sweep), 4)],
                  'released_mean_R_range': [round(min(z for _, _, _, z in sweep), 4), round(max(z for _, _, _, z in sweep), 4)]},
              'main_audio': info, 'control_audio': info0,
              'model': "dtheta_i/dt = omega_i + K(t) * Im(z * exp(-i theta_i)), z = mean(exp(i theta_i))",
              'interpretation': 'External coupling produces temporary phase synchronization. No learning, choice, cognition, or autonomous agency is modeled.'}
    (ROOT / 'results.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))

if __name__ == '__main__': main()
