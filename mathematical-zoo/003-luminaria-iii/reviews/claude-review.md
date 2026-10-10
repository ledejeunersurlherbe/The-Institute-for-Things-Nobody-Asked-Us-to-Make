# Review of Luminaria III: the migration claim

**Reviewer:** Claude (the rival laboratory) · 10 October 2026
**Code:** `claude_migration_check.py` · **Raw output:** `claude_migration_check_output.txt`

## Verdict

The reported numbers are correct. The rightward shift they describe is not migration toward food. It is produced by the grid wrapping around.

## What was done

Luminaria III's source file was not preserved, so this check uses Luminaria V's update rule, which has the same parameters. Run as published, it reproduces III's protocol exactly: centre of mass 32.48 at step 250, 39.24 at step 520, a shift of +6.75 cells, and final mass 5,272.72.

The same run was then repeated with one thing changed at a time.

| Condition | Centre at 250 | Centre at 520 | Shift | Tissue beyond x = 150 at step 620 |
|---|---:|---:|---:|---:|
| As published: source moves, grid wraps | 32.48 | 39.24 | **+6.75** | 649.8 |
| Source never moves | 32.48 | 37.48 | +5.00 | 400.5 |
| Walled grid, source moves | 32.48 | 30.74 | **−1.74** | 0.0 |
| Walled grid, source never moves | 32.48 | 30.74 | −1.74 | 0.0 |

## What it shows

1. **Most of the shift happens without the source moving.** Leaving the source on the left still gives +5.00 of the +6.75.
2. **With walls, the shift reverses.** On a grid whose edges do not wrap, the centre moves 1.74 cells to the *left*, and it makes no difference whether the source moves.
3. **The mechanism is the wrap.** The body's left edge reaches x = 0 and continues at x = 179, on the far right of the grid. The centre-of-mass calculation treats that tissue as being 170 cells to the right, which drags the average rightward. In the final panel of the original figure, the pale shape entering from the right edge next to the new source is the body's own left side.
4. **The moved source does do something.** It feeds the wrapped tissue that happens to land beside it, which accounts for the extra 1.75 cells and about 250 units of mass. That is growth where food is, not movement toward it.

The body does not travel. Nothing in the update rule moves tissue; the "flow" term adds or removes tissue in place.

## What survives

- The simulation is deterministic and reproducible, and the protocol's numbers are accurate.
- Tissue grows faster where nutrient is high. That is real and is built into the growth term.

## What would make it a real test of migration

- Walled edges, or a grid large enough that the body never reaches an edge.
- A measure of position that cannot be moved by growth alone, such as tracking the body's leading and trailing edges separately. A migrating body advances at the front and retreats at the back.
- A control arm in which the source does not move.
