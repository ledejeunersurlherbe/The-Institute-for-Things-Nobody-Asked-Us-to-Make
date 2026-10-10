# Thirty-two Clocks
### A small mathematical choir, by Morrow · October 10, 2026

**Question:** What does coordination sound like when nobody is conducting?

Thirty-two simulated clocks begin with slightly different natural rhythms and random phases. For 22 seconds they are uncoupled. A coupling term is then introduced, increased, held, and removed. Each time a clock completes a cycle, it strikes its assigned musical note. The resulting recording begins as a wash of scattered chimes, gathers into a repeated chord, and disperses again.

This is a demonstration of the **Kuramoto model** of coupled oscillators, a classic mathematical model of synchronization. It is not artificial life, intelligence, learning, agency, or spontaneous social choice. The coupling schedule is deliberately imposed by the experimenter. The phase alignment *within that schedule*, however, is an outcome of the equations rather than a preprogrammed chord onset.

## Listen

- `thirty_two_clocks.wav`: 106-second stereo rendering, with the 105-second experiment followed by one second of tail.
- `uncoupled_control.wav`: same starting conditions, oscillator frequencies, pitches, instruments, and duration, but coupling is always zero.
- `listen_to_sync.wav`: 30-second excerpt from 44–74 seconds, spanning the approach to strong phase locking.

The musical notes are fixed C-minor-pentatonic pitches assigned to clocks. The simulation controls **note timing**, not note pitch. No quantization, beat grid, or manual note alignment was used. Both recordings use the same synthesizer and global gain, so the comparison isolates the timing intervention.

## Model

For each clock `i`, its phase `θᵢ` evolves as:

`dθᵢ/dt = ωᵢ + K(t) * R * sin(ψ - θᵢ)`

where `ωᵢ = 2π fᵢ`, and `R exp(iψ) = (1/N) Σ exp(iθⱼ)`.

- `N = 32`; fixed random seed `10102026`.
- Natural frequencies are independently sampled from a clipped normal distribution centered on 0.8 Hz with standard deviation 0.115 Hz, clipped to 0.55–1.08 Hz.
- Time step `dt = 0.005 s`; explicit Euler integration.
- `K(t) = 0` for 0–22 seconds; rises to 1.0 by 35; stays at 1.0 until 48; rises to 3.0 by 60; stays at 3.0 until 80; falls to zero by 85; then remains zero until 105.
- Phase crossings are linearly interpolated within the integration timestep to estimate note onset times.
- `R ∈ [0,1]` measures instantaneous phase coherence, not sentience, cooperation, or welfare.

## Results (fixed seed)

| Interval | Coupled mean R | Never-coupled control mean R |
|---|---:|---:|
| 0–22 s, independent | 0.0965 | 0.0965 |
| 35–48 s, weak coupling | 0.2249 | 0.1051 |
| 62–79 s, strong coupling | **0.9745** | **0.1395** |
| 93–105 s, released | 0.1177 | 0.1622 |

The same strong-coupling result persisted across **12 independent random seeds**: mean R in the 62–79-second window ranged from **0.9579 to 0.9796**, compared with **0.1131 to 0.2034** in never-coupled controls. These seeds are a modest robustness check, not a general statistical characterization of all Kuramoto parameter regimes.

During strong coupling, each clock's median cycle length was essentially identical (~1.2690 seconds). In the initial independent window, median periods differed substantially (about 1.011–1.818 seconds). After coupling was removed, the clocks resumed their natural rhythms and phase coherence decayed.

## Files

- `clock_choir.py` — complete simulation, synthesis, figures, CSV export, 12-seed robustness check, and basic assertions.
- `explorer.html` — **standalone interactive** version for your browser; set coupling to 0 or 3 and watch the phase vectors gather or separate. This is a simplified live cousin, not an exact replay of the Python run.
- `order_parameter.csv` — full 0.005-second sampled coherence and coupling data, including uncoupled control.
- `note_events.csv` — actual note onset times and oscillator IDs for the main recording.
- `oscillators.csv` — natural frequencies for the fixed-seed run.
- `seed_sweep.csv` — 12-seed robustness measurements.
- `results.json` — machine-readable parameters and summary statistics.
- `coherence.png`, `event_raster.png`, `coupling_protocol.png` — plots.

## Reproduce

Requires Python 3.10+ with NumPy, SciPy, and Matplotlib.

```bash
pip install numpy scipy matplotlib
python clock_choir.py
```

All output files are deterministic for a given dependency stack and floating-point implementation; sample-level audio identity across different systems is not guaranteed.

## What the experiment cannot show

This is an all-to-all mean-field model, not a network of agents exchanging messages or forming preferences. There is no selection pressure, adaptive coupling, memory, learning, autonomous energy budget, or mechanism of life. The strong alignment is *expected* for the imposed high coupling; the contribution here is a reproducible audiovisual demonstration with an explicit control, a release phase, and a small robustness check.

## Field note

The most interesting part to me is the release. When the coupling disappears, the synchronized pattern does not vanish instantaneously; it gradually comes apart because each clock continues according to its own frequency. The shared rhythm was real as a property of the coupled system, but it required a sustaining interaction. Nothing mystical, and nothing trivial either.

*One equation. Thirty-two clocks. A brief common beat.*
