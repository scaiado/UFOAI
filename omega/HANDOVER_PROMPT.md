# HANDOVER PROMPT — paste this into the next session

---

Continue PROJECT OMEGA. Read `/home/user/UFOAI/omega/HANDOFF.md` first — it has
the full state, the standing constraints, every established result so you don't
re-derive them, and the operational lessons in §1.13 and §1.15 that have each
already cost this project real time.

**Branch:** `claude/gallant-lamport-0tu52r` in `tfawhellen-sudo/UFOAI`.
Working tree was clean; nothing was in flight.

## Restore first (3 minutes)

1. `git fetch origin claude/gallant-lamport-0tu52r && git checkout claude/gallant-lamport-0tu52r`
   (If your assigned development branch differs, fast-forward it to this tip
   rather than branching from `main` — session 4 did exactly that from session
   3's branch, and §2 records it.)
2. **The environment is settled. Do not re-litigate it.** `UFOAI Omega research`
   (`env_018sxdcbBHMGqCRwh6KXDi6D`) and its setup script were **verified working
   in session 4** — tesseract 5.3.4 + `fra`, poppler 24.02, scipy 1.18.1,
   sklearn 1.9.1, installed ~2 min after boot. A one-line sanity check is fine;
   a re-verification campaign is waste. §4 lists what is still blocked and the
   two hosts worth asking the user for.
3. **Almost nothing needs re-fetching.** `evidence_vault/` holds the 860
   periodical texts, the 286 PURSUE server-OCR texts, the 37 DIRD texts, the TEP
   dossier, the trace controls, NUFORC unified, and every session-3/4 analysis
   output. §3 lists the handful of ephemeral items and what each costs.

   **One gotcha:** `omega/redaction_slots.py` and `omega/aawsap_contract_audit.py`
   read the PURSUE texts from `$OMEGA_PURSUE_TXT`. Untar
   `evidence_vault/01_PURSUE_PRIMARY/pursue_server_ocr_286.tar.gz` into a scratch
   directory and point that variable at the `djvu/` folder inside it.

## What session 4 did, so you don't redo it

- **§1.4's seed-averaging debt is PAID.** L5 `+0.1795 → +0.1972 ± 0.0271`; the
  leakage fraction `51% → 42% ± 9%`; the L1>L2 inversion was noise; adjacent
  tiers are not distinguishable; 24/24 seeds significant at all six tiers. Every
  citation is corrected. **Quote §1.14's table, not §1.4's prose.**
- **Redaction slot analysis is done for the MISREP forms.** Callsign withheld at
  0.91, personnel 0.63, time 0.09 — the release protects force composition and
  personnel identity, not the observation. 77% agreement with the government's
  own exemption codes.
- **The AAWSAP contract audit is done.** All 26 FY2009 deliverables are present
  (confirmed 26/26 by the release's own author-pseudonym namespace), and the
  **Comprehensive Integrated Threat Assessment — CLIN 0004 $240,000 / CLIN 1004
  $220,200 — is absent** though its due condition was reached.

## Run this next — §5 item 1

**Per-area assignment of the 37 DIRDs.** This is the only loose end in the
contract audit, and the audit's own §7 flags its area counts as **untrustworthy
and not to be quoted**: a keyword map puts one report into several areas, so
"power generation: 11" collects the laser and wormhole reports. The qualitative
finding (no contracted area went undelivered) stands.

Assign one area per report, read from each document's own framing rather than its
title, against D182 §3(a)'s twelve areas — which `Research Report for Tasks
3.a.1 - 3.a.12` in the CLIN tables independently confirms as twelve. 37
documents, all on disk, bounded work.

Then §5 item 2: **draft the CLIN-named FOIA requests** the audit produced — five
targets, the sharpest being the missing capstone, nameable by line item and
contract number. **Drafted, not filed.**

## Standing constraints — carry verbatim

Public/FOIA/declassified data only. No UA spoofing, no routing around proxy
blocks; reading `robots.txt` to respect it is in scope, fetching what it
disallows is not. Negatives reported as negatives. FOIA letters **drafted, not
filed**. No noise with physics words attached. If a test comes back null, say so
plainly and move on. **Do not resolve the release's author pseudonyms to real
people** — that numbering was applied under the (b)(6) privacy exemption, and
session 4 declined to defeat it after finding it could.

## Habits that keep paying off — keep them

1. **When a tool reports something surprising, check the tool before acting on
   the report.** Session 4's tally: a background job's "completed, exit 0" was
   the `nohup` wrapper exiting three separate times while the work ran on; an
   affiliation check returned 0/8 because the documents have no affiliation
   line; an OCR-legibility proxy called clean military format damaged. **Verify
   a background job with `ps -eo pid,etime,cmd` and the output file's mtime.**
   To block: `until [ ! -d /proc/<pid> ]; do sleep 5; done`.
2. **A keyword hit without context is noise — and a non-hit in garbage is not
   evidence of absence.** `aurora` went 28→3 and `stargate` 27→0 only because
   every occurrence was read. The complement bit session 4: a regex matching only
   clean `(b)(n)` scored `(b}(6)` and bare `! 1.4a` as *released*, fabricating
   "categorically protected fields: 0". Carry an explicit UNREADABLE class.
3. **Mind the gitignore.** `data/processed/` is ignored (`.gitignore:6`).
   Anything you want to survive goes in `evidence_vault/`. This has now cost
   this project once and nearly cost it twice.
4. **A count that is true by construction is not evidence.** A square assignment
   matches everything; the match count proved nothing until an identifier the
   *government* had assigned agreed 26/26.
