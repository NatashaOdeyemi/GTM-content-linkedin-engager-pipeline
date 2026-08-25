"""
Stages 1-7: runs one scraped record through post classification, topic extraction, enrichment,
company/contact fit, dedup, campaign check, and comment substantivity -- using the rules in
.claude/skills/classification-qualification.md as the model's operating instructions.

This script is the orchestrator; the actual classification/qualification reasoning is a Claude
call using the skill file as its system prompt, not hardcoded logic here.
"""
from enrich import enrich_contact
from signals import detect_signal
from datetime import date


def already_seen(linkedin_url: str) -> bool:
    """TODO: check the persistent dedup store (see data/README.md) for this person."""
    raise NotImplementedError


def in_any_lemlist_campaign(email_or_linkedin_url: str) -> bool:
    """
    TODO: call the lemlist MCP connector's contact search to check if this person exists in
    ANY campaign, ever -- not limited to currently-active sequences.
    """
    raise NotImplementedError


def classify_and_qualify(record: dict) -> dict:
    """
    TODO: send `record` (post content + engagement) to Claude with the classification-
    qualification skill as system prompt. Expect the JSON shape documented at the end of that
    skill file back. Then:
      1. If post category excluded -> stop, return excluded record.
      2. If already_seen(record['linkedin_url']) -> stop, excluded_reason = 'dedup'.
      3. Enrich via enrich_contact(record['linkedin_url']).
      4. If enrichment returned None -> excluded_reason = 'no company match'.
      5. Apply company fit + contact fit checks from the skill's Stage 4-5 rules.
      6. If in_any_lemlist_campaign(...) -> excluded_reason = 'already in lemlist'.
      7. For comments, run substantivity check; for reactions (and downgraded comments),
         call detect_signal() from signals.py.
      8. Attach problem_area and follow_up_insight via the fixed lookup table.
    """
    raise NotImplementedError


if __name__ == "__main__":
    pass
