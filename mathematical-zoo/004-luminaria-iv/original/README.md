# Luminaria IV — Parametric breeding trial
## Museum accession: IV / Reconstructed record (2026-10-10)

**Original historical output:** `original_figure.png` (retained without editing).

**Important provenance:** The source script, original seed, original initial-condition geometry, numerical integration details, and mutation procedure for the first Phase IV run are **not available** in the preserved files. This package therefore contains a new, explicitly **reconstructed implementation** (`reconstructed_breeding.py`), not a claim to reproduce the exact original image or its exact counts. The values below were reported in the contemporaneous conversation.

### Historical experiment
The three configurations reportedly used a Gray–Scott two-field reaction–diffusion system; two parent parameter vectors were combined into one offspring vector, with a small mutation, and each was simulated for **950 steps**. Occupied area was said to be the number of cells whose V concentration exceeded 0.08.

| vector | Du | Dv | feed | kill | originally reported occupied cells |
|---|---:|---:|---:|---:|---:|
| Parent A | .160 | .080 | .032 | .060 | 1,606 |
| Parent B | .150 | .075 | .039 | .063 | 740 |
| Offspring | .160 | .075 | .033 | .0625 | 878 |

We **cannot recover the precise recombination/mutation operator** from the above alone. In particular, the offspring feed (.033) and kill (.0625) are not simply copies of corresponding parental values. These are historical values, not inferred genotypes.

### New reconstruction (separate experiment)
Run: `python reconstructed_breeding.py` (requires Python 3, NumPy, Matplotlib).

Implemented Gray–Scott discrete update, timestep 1, periodic boundaries; 130x130 grid, five initially seeded circular patches, fixed RNG seed 42, 950 steps. Each of the three runs starts from **identical initial conditions**. The offspring vector is explicitly set to the historically reported offspring parameter vector (no simulated mating operation or spontaneous reproduction). The script writes `reconstruction.png` and `reconstructed_measurements.csv`.

The reconstruction's observed occupied cells are **2,481 (A), 1,330 (B), 1,613 (offspring)**. These DO NOT match the historical outputs; the original geometry/algorithm is unknown. The new script demonstrates that the reported parameter configurations can be simulated and compared, not that it reproduces the original trial exactly.

### What is and is not established
- Established in historical account: a third Gray–Scott parameter vector was reportedly constructed from parental parameters, initialized, and run; the original figure survives.
- Confirmed by the reconstruction: these three **parameter vectors** generate reproducible nonidentical spatial patterns under a declared new initial condition and algorithm.
- **Not established:** autonomous reproduction, inheritance mediated by entities in a shared environment, organismal sexual reproduction, adaptive fitness advantage, spontaneous evolution, numerical identity of the first run, or exactly how the original mutant was constructed.
- The term *offspring* refers to externally engineered parameter recombination, not a biological claim.

### Recommended peer-review test
Ask whether an explicitly recorded operator (uniform crossover, interpolation, or crossover plus seeded Gaussian mutation) with fixed random seed reproduces the declared offspring parameters. Then run multiple independent initial conditions and quantify phenotype variability and robustness, using identical field initialization across lineages and declared boundaries.

Preserve both original result and this reconstructed run. Do not silently overwrite original images or retroactively treat reconstructed measurements as the original data.
