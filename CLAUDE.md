# LinkedIn Engager Outreach Pipeline

This project runs a daily pipeline that finds people who liked or commented on a tracked set of
LinkedIn posts, qualifies them against an ICP, detects the strongest outreach signal available,
drafts a personalized opener, and delivers the day's qualified contacts to a Google Sheet and
Slack. It runs as two Claude Code Routines: a 10pm WAT run (scrape → qualify → queue) and a 9am
run (select → deliver).

The 10pm evening (scrape → qualify → queue) routine runs on weekdays only (Mon-Fri). Weekend
scraping is intentionally disabled — do not schedule or run the evening routine on Saturday or
Sunday.

Read this file in full before doing any work in this repo. It holds the standing rules that
apply across every script — the two skill files under `.claude/skills/` hold the detailed,
situational logic for the classification and copywriting steps specifically.

## Pipeline order (do not reorder or skip stages)

1. **Scrape** — Apify actor `harvestapi/linkedin-profile-posts` (LinkedIn Profile Posts Scraper,
   No Cookies). Tracks the 32 profiles in `config/tracked_profiles.json`. Pulls posts from the
   last 24h, up to 100 reactions and 100 comments per post (comments filtered to the last week).
2. **Classify + extract topic** — see `.claude/skills/classification-qualification.md`, Stages 1-2.
   Posts that don't fit one of the 5 categories are excluded entirely; do not scrape their engagers.
3. **Enrich** — waterfall order is fixed: **HarvestAPI → Prospeo → Icypeas**, for both contact
   and company data. Never skip a tool in the sequence, and never reorder it. If all three return
   no company match, the record fails ICP fit — do not proceed further with it.
   Prospeo, Icypeas, and lemlist are official hosted MCP connectors — call them as tools, not raw
   HTTP requests. HarvestAPI is a raw API (see Credentials below), not an MCP connector.
4. **Qualify** — company fit, then contact fit (see skill file, Stages 4-5). Both gates are
   pass/fail; either one failing excludes the record from all further stages.
5. **Dedup + campaign check** — exclude anyone already captured on any previous day, and exclude
   anyone who has ever appeared in **any** lemlist campaign (not just currently-active ones).
6. **Comment substantivity** (comments only) — see skill file, Stage 7.
7. **Signal detection** — check in this fixed order: Newly Hired Sales/RevOps Leader (role tenure
   < 90 days, from enrichment) → Company Hiring Sales/RevOps Roles (PredictLeads, last 30 days,
   same city/state/country, job posting must still be live) → Post Engagers - Like (default).
8. **Copywriting** — see `.claude/skills/copywriting.md`. Branch strictly on outreach_signal +
   data_source (my post vs. competitor post). Never reuse option_a/option_b/implication text
   across rows with different topics, even within the same problem_area.
9. **Deliver** — see "Daily volume logic" below for exactly what goes out and when.

## Daily volume logic (informational target, never a cap)

```
overshoot(day-1) = max(0, sent_yesterday - 100)
target(day)      = max(0, 100 - overshoot(day-1))
```

Every day, send **all** contacts that qualify — never cap or hold any back. `target` is only
ever reported alongside the actual count, never enforced. The Slack message each morning must
state both numbers, e.g. "132 contacts sent today (target was 100)". If `target(day) == 0`,
explicitly call this out: "Target hit 0 today due to yesterday's overshoot of {N} — still
sending all {count} qualified contacts."

## Data source labeling

`data_source` = "My Post" if the post creator is Natasha Odeyemi, else "Competitor Post". This
determines which copywriting branch applies (see skill file) — get this wrong and every message
downstream uses the wrong template.

## Persistent state

Dedup history and yesterday's sent-count live outside git (a Google Sheet tab or small hosted
store — see `data/README.md`), not as a committed JSON file. Never rely on git history as the
source of truth for who's already been contacted.

## Credentials

Apify, Icypeas, Prospeo, PredictLeads, and lemlist are all official hosted MCP connectors,
authenticated once via claude.ai's Connectors settings — call them as tools, not raw HTTP
requests, inside any Claude Code session or routine. No API keys are stored in this repo or its
environment variables for these; the routine's Connectors section is where each one gets included.

HarvestAPI and Serper are both raw API keys, not MCP connectors — they're read from
`HARVESTAPI_KEY` and `SERPER_API_KEY` environment variables respectively, unlike the true
MCP-connected tools above. HarvestAPI (harvestapi.io) is Stage 3's first enrichment waterfall
tool; Serper is the Stage 0b reaction-URL resolution fallback. Neither is GetLeads.io, which has
been removed from the waterfall entirely.

## Full spec

The original, fully worked specification (including every rule, worked example, and edge case)
lives in `docs/original_spec.md` for reference when a script needs a detail not summarized here
or in the skill files.
