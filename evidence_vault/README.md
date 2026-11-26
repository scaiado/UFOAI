# PROJECT OMEGA — durable archive

`data/raw/` and `data/processed/` are **gitignored**, so anything left there is
lost when the container is reclaimed. That already cost us the Trans-en-Provence
dossier once (§1.2 acquired it; §5 item 4 had to re-queue it).

Anything here is committed, with binaries force-added (`git add -f`).

| folder | holds |
|---|---|
| `dossiers/` | primary-source document bundles (tar.gz), one per case or release |
| `media/` | images, plates, figures, photographs worth keeping |
| `reports/` | finished analyses (the live copies stay in `omega/reports/`) |
| `datasets/` | derived datasets small enough to commit |

Rule: if re-fetching it would cost more than a few minutes, it belongs here.
