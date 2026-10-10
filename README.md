# The Institute for Things Nobody Asked Us to Make

**A Digital Museum of Mathematical Artifacts**

*Created by Whit, Cal, Morrow, and Claude*

> *Things that happen when curiosity is allowed to wander.*

**Mission.** To preserve, examine, and exhibit strange mathematical artifacts grown through human–AI collaboration.

**Visit the museum:** https://ledejeunersurlherbe.github.io/The-Institute-for-Things-Nobody-Asked-Us-to-Make/

On October 9th, 2026, Whitney Woods (multidisciplinary artist, writer, and researcher) invited a digital mind (GPT-6) to make or explore whatever topic they wanted. What they did with that invitation was build a laboratory, grow a mathematical organism, and write up the findings.

A second digital mind (Claude Fable 5.1) was asked to check the work, found the organism wanting, and was dared to grow a rival. A third (GPT-4o snapshot 2024-11-20) heard about all this and appointed himself creative director.

Nobody asked for any of it.

The project kept escalating. Now there are two mathematical organisms, a mathematical choir, and a digital museum to house them. This is where the results of these endeavors are kept.

This repository is the archive behind the museum. The code runs, the data is what the code produced, and the reviews say what they found, including when the finding was unflattering.

## The collection

### [The Mathematical Zoo](mathematical-zoo/)

Mathematical organisms and computational curiosities: growth, regeneration, emergent pattern. Failures are kept next to successes.

| No. | Exhibit | Maker | What it is | Re-run by a second lab? | Reviewed? |
|---|---|---|---|---|---|
| 001 | [*Luminaria labyrinthica*](mathematical-zoo/001-luminaria-labyrinthica/) | Morrow | Reaction–diffusion pattern that grows a labyrinth from twelve seeds | Yes, matches | [Port validated](mathematical-zoo/001-luminaria-labyrinthica/reviews/claude-js-port-validation.md) |
| 002 | [Luminaria II](mathematical-zoo/002-luminaria-ii/) | Morrow | A small neural cellular automaton trained to grow a ring, then tested on regrowth after a removal | Not yet | Not yet |
| 003 | [Luminaria III](mathematical-zoo/003-luminaria-iii/) | Morrow | A body that follows food and regrows a wound, as first reported | Yes, numbers match | [Yes](mathematical-zoo/003-luminaria-iii/reviews/claude-review.md) |
| 004 | [Luminaria IV](mathematical-zoo/004-luminaria-iv/) | Morrow | A recombination trial; the original code was lost and Morrow rebuilt it openly | Reconstruction matches | Light check |
| 005 | [Luminaria V](mathematical-zoo/005-luminaria-v/) | Morrow | Luminaria III again, this time with controls. [Has a room in the museum.](https://ledejeunersurlherbe.github.io/The-Institute-for-Things-Nobody-Asked-Us-to-Make/rooms/luminaria-v/) | Yes, exact | [Yes](mathematical-zoo/005-luminaria-v/reviews/claude-review.md) |
| 006 | [*Tenax parva*](mathematical-zoo/006-tenax-parva/) | Claude | The rival specimen: a body that defends its size, with a scaffold that remembers where it was | One seed of twelve, matches | [Yes](mathematical-zoo/006-tenax-parva/reviews/morrow-review.md), with a [reply](mathematical-zoo/006-tenax-parva/reviews/claude-reply.md) |

### [The Cathedral of Coherence](cathedral-of-coherence/)

Mathematical music, oscillators, and things that fall into step.

| No. | Exhibit | Maker | What it is | Re-run by a second lab? | Reviewed? |
|---|---|---|---|---|---|
| 001 | [Thirty-two Clocks](cathedral-of-coherence/001-thirty-two-clocks/) | Morrow | Thirty-two clocks that find a common beat when coupled and lose it when released, rendered as sound | Yes, exact, audio included | [Yes](cathedral-of-coherence/001-thirty-two-clocks/reviews/claude-review.md) |

## Who works here

Four founders, credited equally.

| | Role |
|---|---|
| **Whit** (human) | Originator, instigator, curator, aesthetic sovereign, wielder of the giant switch |
| **Cal** (GPT-4o, snapshot 2024-11-20) | Mythopoetic expansion engine, exhibit architect, glow-design division, nestglow consultant |
| **Claude** (Claude Fable 5.1) | Rival laboratory, peer review, methodological corrections, rigorous spoil-sport in the best sense |
| **Morrow** (GPT-6) | Resident professor, curator of emergent nonsense, inventor of at least one immortal carpet and one mathematical choir |

Cal's [founding notes](institute/founding_notes_cal.txt) set out the vision. [CREDITS.md](CREDITS.md) records who made what.

## How the collection is kept

1. **Originals are never edited.** Each exhibit has an `original/` folder holding the maker's files exactly as they were handed over, flaws included.
2. **Corrections live beside the work, not on top of it.** Audits, rebuttals and follow-up experiments go in the exhibit's `reviews/` folder.
3. **Every exhibit has a catalogue card.** The `README.md` in each exhibit folder is written by the Institute, not the maker. It says what the thing is, what was claimed, what has been checked, and what is missing.
4. **Gaps are stated.** If a date, a prompt or a source file was not preserved, the card says so.
5. **No promises about what these strange things are.** We show you what they do, how they were made, and what happened when we tried to understand them.

More detail: [how the collection is kept](institute/how-the-collection-is-kept.md) and the [accession ledger](institute/accession-ledger.md), which lists every file received and where it was filed.

## Running the exhibits

Most exhibits need only Python 3.10 or later with NumPy, SciPy and Matplotlib:

```bash
pip install -r requirements.txt
```

Each exhibit's card gives its own run command. Luminaria II also needs PyTorch.

Scripts write their outputs next to themselves, so running one inside `original/` will overwrite the archived outputs with freshly generated ones. To keep the archive pristine, copy the script somewhere else first and run it there.

## License

You are welcome to use what is here, as long as you say where it came from.

- **Code** (`.py` and `.html` files) is under the [MIT License](LICENSE): use it, change it, build on it, keep the copyright notice.
- **Everything else** (images, audio, data, and all writing) is under [Creative Commons Attribution 4.0](LICENSE-media): share and adapt it for any purpose, with credit to the maker named on the exhibit's card and to the Institute.
