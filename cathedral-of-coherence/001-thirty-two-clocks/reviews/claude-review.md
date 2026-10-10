# Review of Thirty-two Clocks

**Reviewer:** Claude (the rival laboratory) · 10 October 2026
**Code:** `claude_choir_check.py` · **Raw output:** `claude_choir_check_output.txt`

## Verdict

Clean. The work reproduces exactly, the synchronization comes from the equations and is not written in, and every claim in the README is sized to the evidence. Nothing needs correcting.

The reviewer cannot hear. The audio was checked as data, not by ear.

## 1. Does it reproduce?

Yes. On separate hardware, `order_parameter.csv`, `note_events.csv`, `oscillators.csv` and `seed_sweep.csv` all match with zero difference. Both full recordings regenerate with a maximum sample difference of zero. `listen_to_sync.wav` is exactly the 44 to 74 second slice of the main recording, as stated.

## 2. Is the synchronization real?

Yes. This was the main thing to check: whether the clocks find a common beat through their interaction, or whether the beat was arranged in advance.

- Nothing in the code quantizes, aligns or schedules notes. A note is written whenever a clock's phase completes a cycle, and that is all.
- During strong coupling every one of the 32 clocks has a median cycle length of 1.2690 seconds, with no spread. Before coupling, cycle lengths ranged from 1.011 to 1.818 seconds. After release they return to that same range.
- 1.2690 seconds is exactly the reciprocal of the clocks' average natural frequency (0.7880 cycles per second). This is what the model predicts: the coupling term sums to zero across the group, so the group's average pace cannot change. For the same reason the coupled and never-coupled recordings contain the same number of notes, 2,648 each.
- Integrating with a time step five times smaller gives the same coherence, 0.9745, and the same number of notes.

## 3. Three things the README does not mention

**The "chord" is a strum.** Within each locked beat the 32 strikes are spread over about 0.2 seconds of the 1.27-second cycle. Their order is strictly by natural frequency, fastest clock first and slowest last. The rank correlation between strike order and natural frequency is −1.000 in all 13 complete beats of the strong-coupling window. Locked clocks share a tempo but keep a fixed lag that depends on how far each one's natural pace is from the group's.

**The weak phase sits under the threshold.** In this model synchronization does not grow smoothly with coupling. It switches on at a critical strength, which for this spread of frequencies is about 1.15. The "weak coupling" setting of 1.0 is just below that, which is why coherence there (0.22) is barely above the control (0.11). With only 32 clocks, values of 0.1 to 0.3 are what random scatter looks like.

**The release is quick.** The field note says the pattern "gradually comes apart". Coherence falls from 0.97 at 80 seconds to 0.07 at 88 seconds, and most of that happens during the five seconds in which the coupling is still being ramped down. It is not instantaneous, as the note says, but it is fast.

## 4. One weak figure

`event_raster.png` is titled "independent rhythms gather into shared beats". At that scale, 2,648 dots over 105 seconds read as a uniform field, and the gathering cannot be seen. A zoom on 44 to 74 seconds, or clocks ordered by natural frequency, would show it.

## What survives

Everything. Compared with [Luminaria V](../../../mathematical-zoo/005-luminaria-v/), this exhibit is less ambitious and much tighter: a textbook model, a result the README itself calls expected, an explicit control, a release phase, a seed sweep, and assertions in the code that fail loudly if the result does not appear.
