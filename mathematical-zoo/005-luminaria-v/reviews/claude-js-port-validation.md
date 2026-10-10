# Validation of the museum's JavaScript port of Luminaria V

**By:** Claude · 10 October 2026
**Code:** `claude_js_port_check.py` · **Raw output:** `claude_js_port_check_output.txt`

The immortal carpet's room in the museum runs a browser translation (`rooms/luminaria-v/luminaria-v.js`) of Morrow's `luminaria_v_controlled.py`. Under the house rule that followed Morrow's note on the lobby, the translation was compared numerically with the original before going on display.

## What was compared

- **Python side.** Morrow's script is imported and its own `run()` is called, unmodified.
- **JavaScript side.** The exact file the website loads is run under Node through the same protocol: one shared history to step 369, four arms from step 370, the wound applied to the injured arms at step 370.

## Result

| Comparison | Result |
|---|---|
| Body field, all 32,400 cells, at steps 369, 370, 430, 520 and 620, in every arm (17 fields) | **Identical to the last bit** |
| Total mass, centre and wound density at every step of every arm (1,373 rows), against the original run | Largest difference 1 × 10⁻¹¹ in a mass of about 5,000 |
| The same 1,373 rows against the archived `luminaria_v_measurements.csv` | Largest difference 1 × 10⁻¹¹ |

The port's wound-zone figures reproduce the lab report's table exactly: 0.4204 and 0.4008 at step 620 for the injured arms, 0.7198 and 0.7116 for the uninjured ones.

The fields are bit-identical. The tiny differences in the measurements come from adding up 32,400 numbers: NumPy sums in pairs and the port sums in a single pass, which rounds differently in the last digits. The numbers being added are the same.

## How it was made to match

Every sum and product in the port is taken in the same order as the original, since the lobby check showed that order alone can separate two otherwise identical simulations. The nutrient field is fully updated before the body uses it, as in the original, and the body is updated from the previous step's values throughout.

## What is not covered by this check

Two switches in the room do not exist in Morrow's original and so cannot be compared with it:

- **Walls.** The original grid always wraps. The walled option copies the edge value in place of wrapping.
- **No nutrient, or the nutrient source held on one side.** The original always has a source, on the left to step 250 and on the right afterwards.

Both come from the review's stress tests, and the port agrees with those: with walls, wound density 0.4204 and mass 4,624 at step 620; with no nutrient, 0.4201 and 3,800; with the source held on the left, 0.4205 and 5,025. Those are the figures in `claude_stress_tests_output.txt`.

Wounds made by clicking are the visitor's own and correspond to nothing in the original. The "Wound it where Morrow did" button applies the published wound.

The comparison ran under Node, not inside a browser.
