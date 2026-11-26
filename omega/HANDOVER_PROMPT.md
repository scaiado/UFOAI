# HANDOVER PROMPT — paste this into the next session

---

Continue PROJECT OMEGA. Read `/home/user/UFOAI/omega/HANDOFF.md` first — it has
the full state, the standing constraints, every established result so you don't
re-derive them, and the operational lessons in §1.13 that have each already cost
this project real time.

**Branch:** `claude/magical-gauss-wzgdqd` in `tfawhellen-sudo/UFOAI`.
**Last commit:** `78ffee8`. Working tree was clean; nothing was in flight.

## Restore first (5 minutes)

1. `git fetch origin claude/magical-gauss-wzgdqd && git checkout claude/magical-gauss-wzgdqd`
2. **Check the environment.** The session-2 start found `allowed_hosts: []` and
   scipy/sklearn missing. There is now an environment called **`UFOAI Omega
   research`** (`env_018sxdcbBHMGqCRwh6KXDi6D`) with 8 allowlisted hosts and a
   setup script. **That script has never actually run** — a setup script does not
   execute on the machine that creates it. Verify `tesseract --version`,
   `tesseract --list-langs` (need `fra`), and `import scipy, sklearn`. If any
   fail: `apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-fra
   poppler-utils` and `pip install scipy scikit-learn`. **Report whether the
   setup script worked** — that is itself the test.
3. **Most data no longer needs re-fetching.** `evidence_vault/` (145 MB,
   committed, not gitignored) holds the 860 periodical texts, the 286 PURSUE
   server-OCR texts, the 37 DIRD texts, the TEP dossier, the trace controls, and
   the NUFORC unified file. Untar what you need. §3 lists the handful of things
   that are still ephemeral and how long each takes to rebuild.

## Run this next — item 1 of §5, and do it before quoting any number

**Pay the §1.4 seed-averaging debt.**

§1.4's **L4 (+0.2176)** and **L5 (+0.1795)** were *single* length-matched draws
with one matcher seed. Session 3 measured matched tiers varying by **±0.1**
across seeds — enquête W3's single draw landed at +0.2607 against a 24-seed mean
of +0.150, and pv W3's landed at −0.0444 against a mean of +0.024. Both were
extremes read as point estimates.

**+0.1795 is quoted as this project's upper bound on content in `HANDOFF.md`,
`omega/reports/baass_ten_month_report.md`,
`omega/reports/geipan_trans_en_provence.md` and
`omega/reports/dird_corpus.md`.** It is overprecise until seed-averaged.

Use `omega/geipan_cd_seed_stability.py` as the pattern: hold the tier fixed,
vary only the matcher seed, 24 draws, report mean ± sd, median, range, and the
fraction of seeds reaching p<0.05. It is cheap now that `toks()` is memoised
(12,412× warm). **Then correct every downstream citation**, and say plainly in
the commit what the number was and what it became.

Then continue down §5: redaction slot analysis (item 2 — novel, and the only
route left into *what* is withheld), then the AAWSAP contract audit (item 3 —
three primary documents already on disk, never compared).

## Standing constraints — carry verbatim

Public/FOIA/declassified data only. No UA spoofing, no routing around proxy
blocks; reading `robots.txt` to respect it is in scope, fetching what it
disallows is not. Negatives reported as negatives. FOIA letters **drafted, not
filed**. No noise with physics words attached. If a test comes back null, say so
plainly and move on.

## Two habits that have paid off repeatedly — keep them

1. **When a tool reports something surprising, check the tool before acting on
   the report.** This caught: "0 failures" over two empty provinces, 31s/page
   OCR producing correct output, a monitor announcing a crash that never
   happened, and a keyword search that found 37 documents by finding zero.
2. **A keyword hit without context is noise.** `aurora` went 28→3 and
   `stargate` 27→0 only because every single occurrence was read. The surviving
   `aurora` hits are all hedged — "alleged", "rumored", "supposed".

