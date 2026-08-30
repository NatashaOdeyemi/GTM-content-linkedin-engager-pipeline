LinkedIn Engager Pipeline — Orchestrator
This is the entry point for running the LinkedIn engager pipeline on demand. It recognizes when the person wants a run, executes the full pipeline by delegating to the two detail skills, and delivers results to Google Sheets and Slack. This replaces the old automated Routine — there is no schedule; this only runs when explicitly invoked.
When to trigger
Recognize natural-language requests to run this pipeline, not just an exact phrase. Examples: "pull today's engagers," "run the LinkedIn pipeline," "get today's qualified contacts," "who engaged with our posts today." If the request is ambiguous whether it means this pipeline versus something else, ask rather than assume.
Configuration (fill in once, reuse every run)

* Google Sheet ID: `1Hxmr6Bnql4nAr1VQBsu0Fpu8jGCFe3yJDqS671Wm8BQ`
* Slack delivery channel ID: `C0BU100BT96`
* Tracked profiles: `config/tracked_profiles.json`
* Drive folder for daily CSV exports: `LinkedIn Engager Pipeline - Daily CSVs`, ID `1zc8otjzMCvaUdcKsQIi1ZAknxP1Sh5ue`

Run steps
1. Determine scope
Default scope is all profiles in `config/tracked_profiles.json`, most recent post per profile, last 24h window — same scope the old automated Routine used. If the person's request narrows this (e.g. "just my post," "just [name]'s post"), scope to that instead and say so back to them.
2. Scrape
Call the Apify actor (`harvestapi/linkedin-profile-posts`) per the config in `CLAUDE.md`: 1 post per profile, posted limit 24h, reactions on (max 100), comments on (max 100, filtered to last week).
3. Clean and classify
Run Stage 0 (self-likes, company-page engagers, like+comment collapse), then Stages 1-9 exactly as specified in `.claude/skills/classification-qualification.md`. This covers categorization, topic extraction, the HarvestAPI → Prospeo → Icypeas enrichment waterfall (including Stage 3's identity resolution for opaque reaction URNs via HarvestAPI's `profileId` param, with Serper as a fallback), company/contact fit, dedup, comment substantivity, signal detection, and problem-area mapping.
Dedup check: before processing a person, check the `_dedup_log` tab in the Google Sheet for their LinkedIn URL (the canonical one resolved in Stage 3, whichever method — HarvestAPI or the Serper fallback — actually resolved it). Skip anyone already present, regardless of how many times this skill has been invoked before, today or on any prior day.
4. Generate copy
For every contact that passes all qualification gates, generate their opener using `.claude/skills/copywriting.md`.
5. Compute today's volume numbers
Read `_daily_counts` for yesterday's date. Compute:

```
overshoot = max(0, sent_yesterday - 100)
target_today = max(0, 100 - overshoot)
```

This tracks by calendar day, not by invocation — if this skill runs multiple times in one day, all runs that day share the same target number, and the count accumulates across runs before being compared to yesterday's figure at the start of the next calendar day.
Send every qualified contact found — the target is informational only, never a cap (see `CLAUDE.md` for the full rule and the Slack-notification wording when target hits 0).
6. Write to the Sheet

* Append each new qualified contact as a row in the `Contacts` tab (all 33 columns per the header row already in place).
* Append each newly-contacted LinkedIn URL, name, today's date, and outreach signal to `_dedup_log`.
* Append today's date, the count actually sent this run, target_today, and the overshoot value used, to `_daily_counts`. If this skill runs more than once on the same calendar day, add a new row per run rather than overwriting — the total for the day is the sum of that day's rows.

7. Deliver to Slack
Two things, both required, delivered as one or two Slack messages:
a. Summary message (via the Slack MCP connector, `slack_send_message`, or the raw Bot Token API's `chat.postMessage` — either works, see note below): post to the configured channel ID. Include: count of contacts found this run, running total for today if this isn't the first run today, target_today, a direct link to the Google Sheet, and — if target_today is 0 — the required note explaining the overshoot per `CLAUDE.md`.
b. CSV delivery via Google Drive (NOT Slack file upload — Slack's native file-sharing is confirmed broken for this app/token: `files.completeUploadExternal` returns `ok: true` but silently never attaches the file to a channel, reproduced across 5 separate attempts with different parameter shapes and OAuth scopes; do not use `files.getUploadURLExternal` / PUT / `files.completeUploadExternal` for this — that whole mechanism is retired from this pipeline). Instead:

1. Build a CSV of this run's new contacts.
2. Upload it to the Drive folder above (`create_file`, `parentId` = the folder ID, `contentMimeType: text/csv`, `disableConversionToGoogleType: true` so it stays a real .csv rather than converting to a Google Sheet).
3. Call `share_file` on the uploaded file with `emailAddress: natasha@tashavirtually.com`, `role: reader`.
4. Verify the share actually took effect by calling `get_file_permissions` on the file afterward — don't assume success from the `share_file` response alone. Note: because the Drive connector is itself authenticated as `natasha@tashavirtually.com`, she already owns every file it creates, so this share call is typically a no-op (permissions will still show only the `owner` entry) — that's expected, not a failure, and the file is already fully accessible to her regardless. The verification step still matters for the day this pipeline shares with someone else's account, where a real `reader` permission should actually appear.
5. Get the file's `viewUrl` from the `create_file` (or `get_file_metadata`) response and post it via `chat.postMessage` to the configured channel — combine it with the summary message from step (a), or send as an immediate follow-up.

This intentionally shares to a specific known Google account rather than a public "anyone with the link" link — the Drive connector available to this pipeline has no `type: anyone` / public-link sharing option at all (confirmed: `share_file`'s schema only accepts a specific `emailAddress`, and passing `"anyone"` there is rejected outright as an invalid argument). Restricting to named accounts is also simply the right call here regardless, since this file contains prospect PII.
8. Confirm back to the person
In the chat where this skill was invoked, give a short summary: how many contacts were found and qualified, how many were excluded and why (grouped by reason, not one-by-one), confirmation that the Sheet and Slack message went out, and today's running total against the 100/day target.
Error handling
If any paid connector call fails outright (not just "no match" — an actual error), stop and tell the person what failed and at which contact, rather than silently skipping and continuing. This mirrors how testing was done throughout this project — always surface real failures for a decision, never guess past them.
