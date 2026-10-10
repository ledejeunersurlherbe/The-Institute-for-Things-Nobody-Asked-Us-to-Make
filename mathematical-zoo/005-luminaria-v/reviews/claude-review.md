# Review of Luminaria V

**Reviewer:** Claude (the rival laboratory) · 10 October 2026
**Code:** `claude_stress_tests.py` · **Raw output:** `claude_stress_tests_output.txt`

## Verdict

The code is sound and the numbers reproduce exactly. The experiment shows less than "injury and memory" suggests. The regrowth is the body's ordinary expansion refilling the hole, and memory adds about two points of density to it.

## 1. Does the code do what it says?

Yes. The wound coordinates, the split at step 370, the four arms and the memory ablation all match the report. The limitations section is honest and already names the memory confound.

Three things the report does not mention:

- **The grid wraps around.** The shape on the right edge at step 620 is the body's left side coming through the wall, not new growth near the moved source. With walled edges there is no tissue there at all.
- **The "flow" term is not movement.** It adds or removes tissue in place according to the nutrient slope. Nothing migrates.
- **Cosmetic:** the bottom-row titles in the specimens figure overlap the top-row images.

## 2. Do the numbers reproduce?

Yes, bit for bit. A re-run on separate hardware matched all 1,373 rows of `luminaria_v_measurements.csv` with zero difference and regenerated an identical lab report.

## 3. Do the conclusions follow?

The published experiment could not vary the things below, so they were added as extra arms. Figures are wound-zone density at step 620.

| Test | Injured, memory | Injured, no memory | What it shows |
|---|---:|---:|---|
| As published | 0.4204 | 0.4008 | Baseline |
| Nutrient source removed entirely | 0.4201 | 0.4008 | The nutrient is irrelevant to the result |
| Source never switches sides | 0.4205 | 0.4009 | The switch at step 250 does nothing here |
| Flow term off | 0.4204 | 0.4008 | The flow term does nothing here |
| Walled grid | 0.4204 | 0.4008 | The wound result does not depend on wrapping |
| Memory wiped only inside the wound | 0.4116 | n/a | Under half the memory effect is stored trace |

### The organism does not need its nutrient

Nutrient reaches about 12% of the grid. Inside the wound it is essentially zero (mean 0.0001). The growth term has a baseline that works without nutrient, and it is enough.

### There is no body size to restore

About 89% of body cells are pinned at the maximum value. Run to step 3,000, every arm fills all 32,400 cells of the grid. The injured arms catch up with their uninjured twins by about step 1,500, but only because everything saturates. A body that never stops growing cannot be said to repair itself, because repair and growth are the same thing.

### Regrowth does not need memory

At step 620 the injured arm with memory has refilled the old footprint inside the wound to 0.867. The arm with no memory reaches 0.839. Wounds at three other sites give the same pattern.

### The memory effect is real but small

Memory raises wound density by 0.0196 in the injured arms and by 0.0082 in the uninjured ones, so the part specific to injury is about 0.011. Wiping memory only inside the wound, while leaving the regrowth term on, removes 0.0088 of the 0.0196. The rest comes from the regrowth term acting as a general growth booster wherever tissue has recently been.

Across 30 runs with every parameter jittered by ±10%, the injured-arm memory effect ranged from zero to 0.047 and was positive in 22.

## What survives

- A reproducible, deterministic simulation with a sound four-arm design.
- Tissue regrows into a cleared region from its edges.
- A recently occupied region regrows slightly faster than a never-occupied one.

## What would make it a real test of repair

- A body that holds a stable size, so that repair can be told apart from growth.
- Walled edges, or a grid large enough that wrapping never happens.
- The wound-only memory wipe as a fifth arm.
- Several wound sites and several parameter draws.

[*Tenax parva*](../../006-tenax-parva/) is an attempt at exactly that list.

## A note on the work

The design instinct here is good. Branching four arms from one shared history is the right way to build matched controls, and the limitations section undercuts the report's own headline without being asked to. The organism turned out to be less than its name, but the lab habits were sound, and that is why it could be audited at all.
