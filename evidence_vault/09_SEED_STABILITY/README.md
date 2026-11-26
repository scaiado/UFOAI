# 09_SEED_STABILITY — the §1.4 seed-averaging debt, paid

Session 4. Stored here rather than in `data/processed/` because that path is
gitignored (`.gitignore:6`) — the session-2 lesson that cost the TEP dossier.

| file | what |
|---|---|
| `geipan_tier_seed_stability_FULL6.json` | all six tiers L0–L5; L0–L3 downsample sweep, L4/L5 matcher + downsample |
| `geipan_tier_seed_stability.json` | L4/L5 with the **joint** sweep (both seeds varied) — the estimate |
| `tier_seeds_full6.log` | console table, six tiers |
| `tier_seeds_joint_L4L5.log` | console table, L4/L5 joint |

Each record holds per-seed draws (effect, n/arm, p, null sd) plus mean, sd,
median, min, max, range, fraction p<0.05, and the published single draw's
percentile within the sampling distribution.

**Headline:** L5 +0.1795 → **+0.1972 ± 0.0271**; leakage fraction 51% → 42% ± 9%;
24/24 seeds significant at all six tiers; adjacent tiers not distinguishable.
Report: `omega/reports/geipan_tier_seed_stability.md`.
