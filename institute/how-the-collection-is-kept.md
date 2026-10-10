# How the collection is kept

## Layout

```
README.md                    the front door
CREDITS.md                   who made what
LICENSE, LICENSE-media        how others may reuse the code and everything else
requirements.txt             the shared Python environment
institute/                   founding notes, these conventions, the accession ledger
mathematical-zoo/            Division 1
cathedral-of-coherence/      Division 2
    NNN-exhibit-name/
        README.md            the catalogue card, written by the Institute
        original/            the maker's files, exactly as received
        reviews/             audits, rebuttals, follow-up experiments
```

Exhibits are numbered within their division in the order they were made.

## Adding a new exhibit

1. Make a folder in the right division: next number, short name, lower case, hyphens.
2. Put the maker's files in `original/` without changing them. If a file arrived with a meaningless name such as `image.png`, give it a descriptive one and say so on the card.
3. Write the catalogue card (`README.md`). Copy an existing card and change the contents. A card covers:
   - what the exhibit is, in two or three plain sentences
   - maker, date, and the prompt or circumstance that produced it
   - what the maker claimed
   - what has been independently checked, and by whom
   - what is in `original/`
   - how to run it
   - what is missing or uncertain
4. Add a row to the collection table in the top-level `README.md`.
5. Add the files to the accession ledger.

## Adding a review

Reviews go in the exhibit's `reviews/` folder, named for the reviewer: `claude-review.md`, `morrow-reply.md`, and so on. A review should state what was re-run, what matched, what did not, and which conclusions survive. If the review involved new code, the code and its raw output go in the same folder so that the review can itself be checked.

A maker who disagrees with a review writes a reply and files it alongside. Nobody edits anyone else's file.

## Corrections

If an original turns out to be wrong, it stays as it is. The correction goes in a review, and the catalogue card is updated to say what is now known. The record of having been wrong is part of the collection.

## Large files

Audio is kept in the repository for now. If the collection grows to dozens of recordings, full-length audio should move to GitHub Releases, with short excerpts kept here.
