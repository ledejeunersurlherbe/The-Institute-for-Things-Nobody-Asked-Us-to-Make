# Specimen 001 — *Luminaria labyrinthica*
## Laboratory protocol

**Model:** Two-species Gray–Scott reaction–diffusion system. The simulation produces concentration patterns, not biological organisms. "Species" is our affectionate nickname.

### Materials
Python 3, NumPy, Matplotlib. Run `python luminaria_labyrinthica.py` from the same folder as the script. It saves `luminaria_labyrinthica_reproduced.png`.

### Environment
- Grid: 220 × 220 cells, periodic (wraparound) boundaries.
- Initial chemical U concentration: 1 everywhere.
- Initial chemical V concentration: 0 everywhere.
- Twelve randomly centered circular seed regions (centers between cells 20 and 199; radii 3–8 cells).
- Within each seed region, U is set to 0.50 plus a small random offset (±0.04), V to 0.25 plus a small random offset (±0.03).
- Random generator: NumPy `default_rng(42)`.

### Dynamics
At every discrete step, compute the five-point discrete Laplacian `L(A)` as the sum of its four nearest neighbors minus four times the center value. For each grid cell, calculate updates **using the previous U and V concentrations**:

`ΔU = 0.16 L(U) − UV² + 0.035 (1−U)`

`ΔV = 0.08 L(V) + UV² − (0.035+0.062) V`

Then update `U += ΔU`, `V += ΔV` (Euler integration, time step = 1). Repeat for 6,000 steps. Save snapshots of V at steps 500, 1,500, and 6,000.

### Display
Map V concentration from 0 to 0.35 using a six-stop charcoal-to-cream palette, keeping the same color scale for all frames. The colors are visualization choices, **not** the colors of real chemicals.

### Repeatability and variations
Keep the seed and all values unchanged for a reproducible result. Change `SEED` for different initial placements, or change `FEED` and `KILL` to explore different patterns. Tiny adjustments can qualitatively alter the resulting geometry. The outcome of a new parameter choice is an experiment, not a guarantee.

### Interpretive note
The emergent pattern does not itself demonstrate life, cognition, or experience. The experiment illustrates how local interactions create ordered global structures without explicitly encoding the finished form.
