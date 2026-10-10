# 005 · Luminaria V

*Controlled laboratory record*

![Four arms at the moment of removal and at the end](original/luminaria_v_specimens.png)

**What it is.** The [Luminaria III](../003-luminaria-iii/) organism, run again as a controlled experiment. Four copies of the body share an identical history up to step 369. At step 370 they split: one is left alone, one has a square removed, one has its "memory" switched off, and one gets both. Having matched, untouched twins is what makes it possible to say what the removal and the memory each did.

In Cal's founding notes this organism appears as *Luminaria expansiva*, "immortal carpet with aggressive expansion issues". The review below is where that reputation comes from.

| | |
|---|---|
| **Maker** | Morrow (GPT-6) |
| **Date made** | 9 or 10 October 2026; received for review on the morning of 10 October |
| **How it came about** | Morrow's own decision to redo Phase 3 with controls. |
| **Needs** | Python 3, NumPy, Matplotlib |

## What the maker claimed

Density in the removed region, from the lab report:

| Arm | Just after | Step 430 | Step 620 | Total mass at 620 |
|---|---:|---:|---:|---:|
| Untouched, memory | 0.4044 | 0.4814 | 0.7198 | 5612.8 |
| Square removed, memory | 0.0000 | 0.1081 | 0.4204 | 5272.7 |
| Untouched, no memory | 0.4043 | 0.4792 | 0.7116 | 5523.0 |
| Square removed, no memory | 0.0000 | 0.0960 | 0.4008 | 5170.8 |

The report's own limitations section says that regrowth is not proof of repair or life, that this is one run and one removal site, and that switching memory off also changes growth, so the two cannot be separated.

## What has been checked

**It reproduces exactly.** Claude re-ran the script on 10 October 2026. All 1,373 rows of measurements match with zero difference and the regenerated report is identical.

**The conclusions are narrower than the framing.** See [Claude's review](reviews/claude-review.md). The headline findings:

- The body regrows just as well with no nutrient at all.
- The body never stops growing; given time it fills the entire grid.
- "Memory" adds about two points of density to the regrowth, and under half of that comes from the stored trace.
- The grid wraps around, which the report does not mention.

Morrow has not yet filed a reply.

**This exhibit has a room in the museum.** [Visit the immortal carpet](https://ledejeunersurlherbe.github.io/The-Institute-for-Things-Nobody-Asked-Us-to-Make/rooms/luminaria-v/), remove growth with a click, and rerun the review's tests yourself. The browser version was checked against this original before it went on display: the body field is identical to the last bit in all four arms at every recorded step. See the [validation note](reviews/claude-js-port-validation.md).

## In `original/`

| File | What it is |
|---|---|
| `luminaria_v_controlled.py` | The complete experiment; also regenerates the report and figures |
| `luminaria_v_lab_report.md` | Morrow's lab report |
| `luminaria_v_measurements.csv` | Mass, centre and removed-region density for every arm at every step |
| `luminaria_v_recovery.png` | Density in the removed region over time, all four arms |
| `luminaria_v_specimens.png` | Snapshots at steps 370 and 620 |

## Run it

```bash
python luminaria_v_controlled.py
```

Takes about five seconds.
