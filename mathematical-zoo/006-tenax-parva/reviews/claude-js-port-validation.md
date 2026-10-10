# Validation of the museum's JavaScript port of *Tenax parva*

**By:** Claude · 10 October 2026
**Code:** `claude_js_port_check.py` · **Raw output:** `claude_js_port_check_output.txt`

*Tenax parva*'s room in the museum runs a browser translation (`rooms/tenax-parva/tenax-parva.js`) of `tenax.py`. Under the house rule, the translation was compared numerically with the original before going on display.

Note that the maker of this organism also wrote the port and this check. The check is reproducible, and a second laboratory is welcome to run it.

## Why this check is different from the Luminaria ones

The Luminaria ports could be compared with their originals run for run, because those experiments have no randomness. *Tenax parva* adds a small random jitter at every step, drawn from NumPy's random generator. A browser cannot reproduce that stream, so no run in the room can be the same run as a published seed. The check is therefore in two parts: the rule itself with the jitter switched off, and the behaviour with the jitter on.

## Part 1. The rule, with noise off

The port was started, changed in each of the ways the room allows, and saved. The original `tenax.py`'s own `step()` was then run from the same saved state, and the two were compared after 2,000 steps.

| Scenario | Largest difference in any cell, body | Scaffold |
|---|---:|---:|
| Left untouched | 6 × 10⁻¹⁶ | 4 × 10⁻¹⁶ |
| Right-hand part removed | 6 × 10⁻¹⁶ | 4 × 10⁻¹⁶ |
| Part removed, scaffold erased there | 4 × 10⁻¹⁶ | 3 × 10⁻¹⁶ |
| Scaffold erased, body untouched | 9 × 10⁻¹⁶ | 6 × 10⁻¹⁶ |
| Tissue added | 7 × 10⁻¹⁶ | 4 × 10⁻¹⁶ |
| Part removed, scaffold term off | 8 × 10⁻¹⁶ | 6 × 10⁻¹⁶ |
| Inhibitor switched off | 0 | 0 |

**The port follows the original rule to within the last digit of floating-point arithmetic.** It is not bit-identical where the inhibitor is on, and cannot easily be made so: the inhibitor is found each step with a cosine transform, and the port's transform (a 128-point FFT written for the purpose) does its arithmetic in a different order from SciPy's. The two transforms agree to 6 × 10⁻¹⁶ on a random test field. With the inhibitor off there is no transform, and the port is identical to the last bit.

Unlike the Luminaria organisms, this one settles toward a fixed state, so these last-digit differences do not grow.

## Part 2. The behaviour, with noise on

The port, using its own jitter, was put through the published protocol for 5,000 steps on four seeds and set beside the published twelve.

| Condition | Size at end, relative to untouched twin | | Distance from start, cells | |
|---|---:|---:|---:|---:|
| | **Port** | **Published** | **Port** | **Published** |
| Part removed, scaffold intact | 0.973 | 0.976 (0.972 to 0.980) | 2.93 | 2.92 |
| Part removed, scaffold erased there | 0.917 | 0.921 (0.913 to 0.929) | 7.89 | 7.81 |
| Scaffold erased, body untouched | 0.943 | 0.948 (0.944 to 0.953) | 4.43 | 4.31 |
| Tissue added | 1.009 | 1.010 (1.008 to 1.013) | 1.15 | 1.18 |

The port's figures fall inside or at the edge of the published ranges. The scaffold-intact body ended closer to its start than the scaffold-erased one in 4 of 4 seeds. No body touched a wall.

## Two deliberate differences from the published experiment

- **The body starts already settled.** The published runs grew each body from a rough ellipse for 8,000 steps, and the review of that work noted they had not finished settling: the untouched twins grew a further 4.7% during the follow-up. In the room the body starts as a disc at the settled size (radius 24.89 cells, found by letting one settle with the noise off). The port's untouched twin changes by 0.1% over the same follow-up. This accounts for the port sitting a few thousandths below the published sizes.
- **The added patch is slightly smaller relative to the body:** 17% extra against the published 19%. The patch is the same size in cells; the settled body it is added to is a little larger than the published, not-yet-settled ones.

## What is not covered

- Removing, adding and erasing by clicking are the visitor's own and correspond to nothing published. The two buttons apply the published removal and the published patch.
- Switching the inhibitor back on after the body has spread was not part of the published experiment. In the port the body shrinks again but slowly, reaching about 1.2 times its settled size 6,000 steps later.
- The comparison ran under Node, not inside a browser.
