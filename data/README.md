# Persistent state

Two things need to persist across runs and must NOT live as a committed file in this repo:

1. **Dedup history** -- every LinkedIn URL ever captured, so Stage 6 can exclude repeats.
2. **Yesterday's sent-count** -- needed by `deliver.py`'s `compute_target()` for the daily
   target math.

Recommended: a dedicated tab in the same Google Sheet used for delivery (e.g. `_dedup_log` and
`_daily_counts`), read/written via the same Sheets integration as the main delivery write. A
committed JSON file in git would work for a low-volume prototype but will produce merge
conflicts and unbounded repo growth once this runs daily at scale -- don't ship that long-term.
