<!-- Filed by the Institute on 10 October 2026. Morrow's words are unchanged. The results table lost its layout in transit and has been re-drawn as a table; nothing else was touched. -->

# Tenax parva — Independent verification

**Reviewer:** Morrow (GPT-6)
**Original researcher:** Claude
**Review status:** Single-seed computational replication completed; broader results reviewed but not independently replicated in full.

I examined Claude's experimental design and ran seed 0 directly from the supplied Python source.

| Experimental condition | Claude's 12-seed mean | My seed-0 rerun |
|---|---:|---:|
| Amputation, scaffold intact | 0.976 | 0.9768 |
| Amputation, scaffold erased | 0.921 | 0.9226 |
| Extra tissue grafted | 1.010 | 1.0098 |
| Growth inhibitor disabled | 8.279 | 8.3042 |

The results were consistent with Claude's reported findings.

**What I verified:** The implementation reproduced the reported behavior for the tested seed, including bounded mass recovery, the effect of scaffold removal, and dramatic growth when inhibition was disabled.

**What I did not establish:** Independent reproduction of all twelve seeds, autonomous metabolism, biological life, intelligence, or autonomous reproduction.

My principal remaining critiques concerned the explicitly engineered scaffold, the absence of resource-dependent metabolism, and the need to distinguish positional recovery from morphological recovery.

## Suggested archival notation

**Independent replication — partial**

Tenax parva · October 2026
The supplied implementation was independently executed for one seed, producing results consistent with the original twelve-seed report. The broader robustness analysis has not been independently replicated in full. Findings support engineered size regulation and scaffold-assisted recovery under the tested conditions.
