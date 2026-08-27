# LinkedIn engager outreach pipeline

Daily pipeline: scrapes engagers on 32 tracked LinkedIn profiles' posts, classifies and qualifies
them against an ICP, detects the strongest available outreach signal, drafts a personalized
LinkedIn opener, and delivers the day's qualified contacts to a Google Sheet and Slack.

Read `CLAUDE.md` first -- it's the always-loaded standing context for this project. The detailed,
step-by-step logic for classification/qualification and copywriting lives in
`.claude/skills/`.

## Status

The pipeline runs entirely through `.claude/skills/orchestrator.md`, which calls the Apify,
HarvestAPI/Prospeo/Icypeas, PredictLeads, lemlist, Google Sheets, and Slack tools directly --
there are no standalone scripts. It's triggered on-demand in a Claude Code session, not on a
schedule.

## Setup

1. Push this repo to GitHub. (done)
2. Connect Claude Code to GitHub and open a session on this repo.
3. Connect all MCP tools as Remote connectors at claude.ai Settings > Connectors: Apify,
   GetLeads.io, Icypeas, Prospeo, PredictLeads, lemlist, and Slack. Note GetLeads.io is
   connected but no longer used in the active enrichment waterfall (see `CLAUDE.md`).
4. Set `HARVESTAPI_KEY`, `SERPER_API_KEY`, and `SLACK_BOT_TOKEN` as environment variables in
   the Claude Code cloud environment -- not committed to the repo. These three are raw API
   keys, not MCP connectors (see `.env.example` for local dev).
5. Confirm the Google Sheet (ID in `.claude/skills/orchestrator.md`) and Slack channel are
   set up.
6. To run the pipeline: open a Claude Code session on this repo and ask in natural language,
   e.g. "pull today's engagers" -- `.claude/skills/orchestrator.md` handles the rest.
