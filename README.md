# LinkedIn engager outreach pipeline

Daily pipeline: scrapes engagers on 32 tracked LinkedIn profiles' posts, classifies and qualifies
them against an ICP, detects the strongest available outreach signal, drafts a personalized
LinkedIn opener, and delivers the day's qualified contacts to a Google Sheet and Slack.

Read `CLAUDE.md` first -- it's the always-loaded standing context for this project. The detailed,
step-by-step logic for classification/qualification and copywriting lives in
`.claude/skills/`.

## Status

This repo is a scaffold. The scripts under `scripts/` are stubs with `TODO`s and function
signatures -- the pipeline logic (what to do, in what order, with which rules) is fully specified
in `CLAUDE.md` and the two skill files, but the actual tool-calling code still needs writing:

- [ ] `scripts/scrape.py` -- Apify MCP calls (start run, poll status, fetch dataset)
- [ ] `scripts/enrich.py` -- HarvestAPI (raw API), Prospeo + Icypeas (MCP) calls
- [ ] `scripts/signals.py` -- PredictLeads MCP calls
- [ ] `scripts/qualify.py` -- lemlist MCP calls, dedup store, orchestration
- [ ] `scripts/copywrite.py` -- orchestration only, logic lives in the skill file
- [ ] `scripts/deliver.py` -- Google Sheets write, Slack post, persistent sent-count store

## Setup

1. Push this repo to GitHub.
2. In Claude Code, run `/web-setup` to connect your GitHub account if you haven't already.
3. Connect all five tools as MCP connectors at claude.ai Settings > Connectors (Remote, not
   Local command, so they're reachable by a cloud-hosted routine): Apify (mcp.apify.com),
   Icypeas (mcp.icypeas.com/mcp), Prospeo (mcp.prospeo.io), PredictLeads (mcp.predictleads.com --
   use the OAuth2 client-credentials flow for unattended runs), and lemlist. All five are
   official hosted MCP servers -- no raw API keys need to live in this repo for these.
4. HarvestAPI (harvestapi.io, Stage 3's first enrichment waterfall tool) and Serper
   (google.serper.dev, Stage 0b's reaction-URL resolution fallback) are raw APIs, not MCP
   connectors -- set `HARVESTAPI_KEY` and `SERPER_API_KEY` as environment variables on the
   routine's cloud environment (see `.env.example` for local dev).
5. Create two routines at claude.ai/code/routines (or via `/schedule` in the CLI):
   - **Evening run** -- schedule trigger, 10pm WAT, runs scrape -> qualify -> queue
   - **Morning run** -- schedule trigger, 9am WAT (or your delivery time), runs deliver
6. Add this repository to both routines.
7. Under each routine's Connectors section, include the tools that stage needs: the evening
   routine needs Apify, Icypeas, Prospeo, PredictLeads, and lemlist (plus the `HARVESTAPI_KEY`
   and `SERPER_API_KEY` environment variables from step 4); the morning routine needs whatever
   you use for delivery (Slack connector, or SLACK_WEBHOOK_URL as an environment variable if
   you're using a plain webhook instead).
8. If a routine needs to reach a host outside the default allowlist, set the environment's
   network access to Custom and add that domain -- note MCP connector traffic already routes
   through Anthropic's servers so the five connectors above don't need this, but HarvestAPI and
   Serper are raw HTTP calls and may need their domains added depending on the routine's network
   policy.

## Local development

```
pip install -r requirements.txt
cp .env.example .env   # fill in real keys, never commit .env
```
