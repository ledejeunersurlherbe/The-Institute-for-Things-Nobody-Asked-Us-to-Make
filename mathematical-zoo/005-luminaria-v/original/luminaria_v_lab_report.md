# Luminaria V — controlled laboratory record

## Design
Four arms share identical initial conditions and steps 1–369. At step 370, one factor is injury (removing biomass from cells x=52..83, y=74..105), one is memory ablation (M reset to zero and memory-dependent regrowth removed thereafter). Source switches from x=24 to x=156 after step 250. All conditions otherwise identical.

## Outcomes

| Arm | Wound area mean immediately after intervention | At step 430 | At step 620 | Total biomass at 620 |
|---|---:|---:|---:|---:|
| sham_memory | 0.4044 | 0.4814 | 0.7198 | 5612.8 |
| injured_memory | 0.0000 | 0.1081 | 0.4204 | 5272.7 |
| sham_no_memory | 0.4043 | 0.4792 | 0.7116 | 5523.0 |
| injured_no_memory | 0.0000 | 0.0960 | 0.4008 | 5170.8 |

## Limitations
- Regrowth is not by itself proof of homeostasis, self-directed repair, cognition, or living status.
- This is one seeded environment and one wound location, not a statistical sample.
- The sham branches provide matched counterfactuals; conclusions are limited to these deterministic rules.
- The memory ablation also changes the local growth dynamics and so does not isolate mnemonic content from a growth contribution.
- The model has no autonomous reproduction, and body boundaries are diffuse.

## Reproducibility
Run `python luminaria_v_controlled.py` with NumPy and Matplotlib. Parameters, initial conditions, update equations, intervention schedule, metrics, and figures are all embedded in that source file. CSV records each trial.