"""
Stage 9: delivery + daily volume reporting.

Volume logic (see CLAUDE.md) -- target is informational only, never a cap:
    overshoot(day-1) = max(0, sent_yesterday - 100)
    target(day)      = max(0, 100 - overshoot(day-1))
Every qualified contact goes out every day; nothing is ever held back or dropped for volume.
"""
import os

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def get_sent_count(for_date) -> int:
    """TODO: read yesterday's delivered-count from the persistent store (data/README.md)."""
    raise NotImplementedError


def compute_target(today) -> int:
    from datetime import timedelta
    yesterday = today - timedelta(days=1)
    sent_yesterday = get_sent_count(yesterday)
    overshoot = max(0, sent_yesterday - 100)
    return max(0, 100 - overshoot)


def write_to_sheet(qualified_contacts: list[dict]) -> None:
    """TODO: append rows to the Google Sheet -- one row per contact, full field set from spec
    (name, LinkedIn URL, company, enrichment fields, outreach_signal, full_message, etc.)."""
    raise NotImplementedError


def post_to_slack(qualified_contacts: list[dict], target: int) -> None:
    """TODO: post the daily summary to Slack via SLACK_WEBHOOK_URL."""
    count = len(qualified_contacts)
    lines = [f"{count} contacts sent today (target was {target})"]
    if target == 0:
        lines.append(
            "Target hit 0 today due to yesterday's overshoot -- still sending all "
            f"{count} qualified contacts."
        )
    message = "\n".join(lines)
    raise NotImplementedError


def deliver(qualified_contacts: list[dict], today) -> None:
    target = compute_target(today)
    write_to_sheet(qualified_contacts)
    post_to_slack(qualified_contacts, target)
