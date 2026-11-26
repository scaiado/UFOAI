# 07 — PERIODICALS PRIMARY · the echo-chamber test, re-grounded

**860 contemporaneous issues, 72,057,926 chars, zero fetch failures.**
MUFON UFO Journal / Skylook 485 (1967–2008) · APRO Bulletin 260 (from Vol 1
No 1, 1952) · CUFOS International UFO Reporter 115.

Stored as a fetch manifest rather than 72 MB of text; see
`omega/periodical_provenance.py` and the archive.org identifiers
`MUFON_UFO_Journal_-_Skylook`, `apro-bulletin`, `iur-vol.-31-no.-4`.

## The limitation this lifts

Phase 1 / Track 3 found **12 events appearing in 5–6 separate catalogues where
every citation points at another compilation inside the same corpus** — zero
upstream roots. They have the appearance of strong corroboration and no
traceable origin.

Phase 1's single biggest stated limitation was that it could only measure *which
compilations cite which*, never *what the cited sources say*, because the
periodicals were not held. They are now.

## The test, with controls — because absence without a control proves nothing

If the search cannot find cases **known** to be in these bulletins, then absence
on the targets says only that the method fails. Four heavily-documented cases of
the same era were run as positive controls.

**Strict criterion** — place name with year **and** month inside ±320 chars:

| event | | place hits | issues | date-corroborated |
|---|---|---|---|---|
| Socorro / Zamora 1964-04 | CONTROL | 355 | 114 | **52** |
| Kecksburg 1965-12 | CONTROL | 241 | 46 | **41** |
| Trans-en-Provence 1981-01 | CONTROL | 25 | 19 | **5** |
| Exeter 1965-09 | CONTROL | 145 | 52 | **4** |
| Wright-Patterson AFB 1951-06 | TARGET | 291 | 147 | **0** |
| Dallas TX 1965-08 | TARGET | 406 | 221 | **0** |
| Galesburg IL 1967-03 | TARGET | 8 | 8 | **0** |
| "a small town in Texas" 1966-09 | TARGET | 3,951 | 661 | 3 → **0 genuine** |

**Controls 4/4 detected. Targets 0/4.**

The three apparent "Texas" hits were checked individually and all are
coincidental co-occurrence of a state name with a date: a physician's military
service record (*"Major, July 1966-June 1969"*, APRO 1975), a case list in a
1981 IUR article, and a 2007 MUFON letter about employment (*"August 1965
through September 1966"*). None refers to a 1966 Texas sighting.

**Relaxed criterion** — place name within 400 chars of the **year alone**, no
month required, the loosest test that still means anything:

| event | | hits | issues |
|---|---|---|---|
| Socorro 1964 | CONTROL | **127** | 60 |
| Kecksburg 1965 | CONTROL | **103** | 32 |
| Exeter 1965 | CONTROL | 14 | 8 |
| Trans-en-Provence 1981 | CONTROL | 10 | 7 |
| Wright-Patterson 1951 | TARGET | 5 | 3 |
| Dallas 1965 | TARGET | 2 | 2 |
| Galesburg 1967 | TARGET | **1** | 1 |

**Controls outnumber targets by 10× to 127×.** The weakest control is a *French*
case in *US* bulletins (TEP, 10 hits). The strongest target is Wright-Patterson
AFB — a site named 291 times across 147 issues, whose year-proximity rate is
nevertheless near zero.

## Result

**The echo-chamber finding strengthens.** The three testable "unverifiable"
events have no meaningful contemporaneous primary-publication footprint across
the three largest US UFO-organisation bulletin runs, spanning 1952–2008, while
controls of the same era are abundant and easy to find. The corroboration is
circular: six catalogues citing each other, with nothing underneath.

The fourth is worse than unverifiable — **"a small town in Texas" is untestable
by construction.** An event carried by 6 catalogues whose recorded location is a
state and an indefinite article has no checkable locus at all.

This is consistent with, and sharpens, Phase 1's measured echo chamber: 3.628
observed against a 5.130 null, **29% below chance, z ≈ −31**, and 77–80% of
events single-sourced.

## What this does NOT establish

- **Not nonexistence.** These three bulletin runs are the strongest available
  primary-publication test, not a census. NICAP's *UFO Investigator*, *Flying
  Saucer Review*, the CUFOS case files and contemporaneous local newspapers are
  all absent from the corpus. An event could have been reported somewhere these
  three did not carry it.
- **OCR is imperfect** on 1950s–70s offset print. A mangled date could defeat
  the proximity window, which is why the relaxed year-only test was run as well —
  and it gives the same answer.
- The window is a **proximity heuristic**. A bulletin could discuss a case
  without restating its full date near the place name. The controls show this is
  not usually what happens.
