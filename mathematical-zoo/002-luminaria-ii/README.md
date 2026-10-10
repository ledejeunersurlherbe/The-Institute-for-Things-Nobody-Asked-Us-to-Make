# 002 · Luminaria II

*Growth and wound response*

**What it is.** A neural cellular automaton: a grid of cells that all follow the same small learned rule, each seeing only its immediate neighbours. The rule is trained so that a single seeded cell grows into a target shape, a translucent ring with a bright core. The grown shape is then wounded by blanking a rectangle, and the script measures how much of it returns, against an unwounded control run with identical random updates.

| | |
|---|---|
| **Maker** | Morrow (GPT-6) |
| **Date made** | 9 or 10 October 2026; the exact day was not recorded |
| **How it came about** | Morrow's second self-chosen project, following *Luminaria labyrinthica*. |
| **Needs** | Python 3, NumPy, Matplotlib, PyTorch |

## What the maker claimed

Nothing is on file. No lab report, figure or printed measurements were preserved for this exhibit, only the script and the trained weights. Any claims Morrow made about the result live in the original conversation.

## What has been checked

Nothing yet. This exhibit has not been re-run or reviewed.

Things a reviewer should look at:

- Whether the saved weights, loaded into the script's model, reproduce the growth and repair the maker saw.
- The training loop only ever grows the shape from a seed. It never trains on damaged shapes. Any regrowth after wounding is therefore untrained behaviour, which makes it more interesting if it happens and less surprising if it does not.
- The wound is one rectangle, one random seed, one run.

## In `original/`

| File | What it is |
|---|---|
| `luminaria_ii.py` | Training, growth, wounding, control run, figure and measurements |
| `luminaria_ii_weights.pt` | The trained weights Morrow saved (PyTorch format, about 19 KB) |

## Run it

The script saves its outputs to `/mnt/data`, a folder that existed in Morrow's workspace and probably does not exist on yours. To run it unchanged, create that folder first, or copy the script and change the one line that sets `out`.

```bash
pip install torch
python luminaria_ii.py
```

It retrains from scratch each time (280 training steps) and prints the wound measurements at the end.

## Missing

- The original figure, `luminaria_ii_experiment.png`
- The printed measurements from Morrow's run
- Any written report
