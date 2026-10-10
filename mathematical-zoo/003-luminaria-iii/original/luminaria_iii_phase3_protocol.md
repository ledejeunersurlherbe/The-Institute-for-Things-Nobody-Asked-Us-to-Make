
# Luminaria III / Phase 3 protocol

Grid: 180x180
Fields: body B, nutrient N, memory M

Schedule:
- left nutrient source active through step 250
- right nutrient source active from step 251 onward
- injury applied at step 370 in body region (slice(74, 106, None), slice(52, 84, None))

Parameters:
{'s0': 0.4, 's1': 0.15, 'n_diff': 0.16, 'n_keep': 0.994, 'src_add': 0.09, 'cons': 0.018, 'm_keep': 0.986, 'm_add': 0.06, 'flow': 0.032, 'growth': 0.16, 'gthr': 0.12, 'gbase': 0.26, 'gN': 2.0, 'memreg': 0.14, 'mthr': 0.09, 'mbase': 0.14, 'persist': 0.085, 'pthr': 0.08, 'decay': 0.03, 'dbase': 0.14, 'dthr': 0.07, 'spread': 0.022, 'cut': 0.007}

Results:
- center of mass at step 250: 32.48
- center of mass at step 520: 39.24
- rightward shift: 6.75 cells
- wound density before injury (step 369): 0.403
- wound density immediately after injury (step 371): 0.001
- wound density at step 430: 0.108
- wound density at step 620: 0.420
- wound refill gain from immediate post-injury to final: 0.419
- final total mass: 5272.72
