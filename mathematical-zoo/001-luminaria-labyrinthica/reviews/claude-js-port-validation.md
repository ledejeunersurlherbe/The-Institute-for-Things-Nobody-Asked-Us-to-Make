# Validation of the lobby's JavaScript port of Specimen 001

**By:** Claude · 10 October 2026 · **Requested by:** Morrow
**Code:** `claude_js_port_check.py` · **Raw output:** `claude_js_port_check_output.txt`

## The request

The museum's lobby grows *Luminaria labyrinthica* live, using a JavaScript port (`lobby/specimen001.js`) of Morrow's Python original. The placard says it grows "from the very same equations and seeds as the original." Morrow's note on the draft:

> The JavaScript port appears thoughtfully implemented, but its claim to reproduce the original experiment exactly deserves a numerical comparison against the original Python output. Matching equations, seeds, and parameters is a strong start; it doesn't by itself establish identical trajectories, particularly without checking discretization and update details.

That is correct, and a claim on a museum wall should be checked like any other.

## What was compared

- **Python side.** Morrow's script is imported and its own `main()` is run without modification. The plotting library is replaced by a stand-in that catches the three arrays `main()` passes to `imshow`: the V field at steps 500, 1,500 and 6,000. So the Python numbers are the ones the original code computed, not a re-implementation of it.
- **JavaScript side.** The exact file the website loads is run under Node, and its V field is dumped at the same three steps.

## Result

| Step | Largest difference in any cell | Cells drawn in a different colour |
|---:|---:|---:|
| 500 | 0 | 0 of 48,400 |
| 1,500 | 0 | 0 of 48,400 |
| 6,000 | 0 | 0 of 48,400 |

Final V field in both: minimum 0.000328, maximum 0.385352, mean 0.138679.

**The port is identical to the original, to the last bit, at every step checked.**

## What the check caught

It did not start out that way. The first version of the port matched the original only to within 3 × 10⁻¹² at step 6,000 (3 × 10⁻¹⁵ at step 500, growing about a thousandfold along the way). That is far below anything visible, and the placard's wording would have survived it. But it meant "the same" was not quite true.

The cause was the order of arithmetic. The original works out each cell's whole change and then adds it to the cell. The first port added the terms to the cell one at a time. On paper those are the same sum; in floating point they round differently in the last digit, and this system amplifies small differences. The port now adds in the original's order, and the difference is exactly zero.

So Morrow's note was right in the specific way it predicted: matching equations, seeds and parameters did not by itself establish identical trajectories. The update details mattered.

## The update details

- **Discretization.** Both use the same five-point Laplacian on a 220 × 220 grid that wraps at the edges, with a time step of 1. The four neighbours are summed in the same order.
- **Update order.** Both compute every cell's change from the previous step's values and then apply all changes at once. The port does this with two buffers that swap each step; the original does it with whole-array arithmetic. Neither updates in place.
- **Starting state.** The twelve seed patches (position, radius, and the two concentrations) were read out of NumPy's `default_rng(42)` and written into the port as constants, in the original order, so that later patches overwrite earlier ones identically.
- **Precision.** Both use 64-bit floating point.

## What is not covered

- The lobby draws 3 simulation steps per frame and stops at step 6,000, so a visitor sees every third step. Nothing is skipped in the calculation.
- The comparison ran under Node. Browsers use the same floating-point arithmetic, but no browser was instrumented for this check.
- The colours on the wall use Morrow's six-stop scale, interpolated in 256 steps. Matplotlib interpolates the same stops slightly differently, so the wall is not pixel-identical to the archived figure even though the numbers behind it are.
