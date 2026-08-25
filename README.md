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
- [ ] `scripts/enrich.py` -- GetLeads.io, Icypeas, Prospeo MCP calls
- [ ] `scripts/signals.py` -- PredictLeads MCP calls
- [ ] `scripts/qualify.py` -- lemlist MCP calls, dedup store, orchestration
- [ ] `scripts/copywrite.py` -- orchestration only, logic lives in the skill file
- [ ] `scripts/deliver.py` -- Google Sheets write, Slack post, persistent sent-count store

## Setup

1. Push this repo to GitHub.
2. In Claude Code, run `/web-setup` to connect your GitHub account if you haven't already.
3. Connect all six tools as MCP connectors at claude.ai Settings > Connectors (Remote, not
   Local command, so they're reachable by a cloud-hosted routine): Apify (mcp.apify.com),
   GetLeads.io, Icypeas (mcp.icypeas.com/mcp), Prospeo (mcp.prospeo.io), PredictLeads
   (mcp.predictleads.com -- use the OAuth2 client-credentials flow for unattended runs), and
   lemlist. All six are official hosted MCP servers -- no raw API keys need to live in this repo.
4. Create two routines at claude.ai/code/routines (or via `/schedule` in the CLI):
   - **Evening run** -- schedule trigger, 10pm WAT, runs scrape -> qualify -> queue
   - **Morning run** -- schedule trigger, 9am WAT (or your delivery time), runs deliver
5. Add this repository to both routines.
6. Under each routine's Connectors section, include the tools that stage needs: the evening
   routine needs Apify, GetLeads.io, Icypeas, Prospeo, PredictLeads, and lemlist; the morning
   routine needs whatever you use for delivery (Slack connector, or SLACK_WEBHOOK_URL as an
   environment variable if you're using a plain webhook instead).
7. If a routine needs to reach a host outside the default allowlist, set the environment's
   network access to Custom and add that domain -- but note MCP connector traffic already routes
   through Anthropic's servers, so none of the six connectors above need this.

## Local development

```
pip install -r requirements.txt
cp .env.example .env   # fill in real keys, never commit .env
```
