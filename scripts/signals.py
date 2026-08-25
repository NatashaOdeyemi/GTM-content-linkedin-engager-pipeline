"""
Stage 8: Signal detection, checked in this fixed order:

1. Newly Hired Sales/RevOps Leader -- title matches leadership list AND
   (today - role_start_date).days < 90. role_start_date comes from the enrichment waterfall.
2. Company Hiring Sales/RevOps Roles -- PredictLeads job search, last 30 days, same city/state/
   country as the contact, matching titles/categories from the skill file. A stale posting
   (no longer live) cannot be used -- fall through to the next check.
3. Post Engagers - Like -- default.

PredictLeads is an official hosted MCP connector (mcp.predictleads.com), authenticated via
claude.ai Connectors using the OAuth2 client-credentials flow (recommended for unattended
routine runs over quick header auth). Call it as a tool, not a raw HTTP request.
"""
from datetime import date

LEADERSHIP_TITLES = {
    "cro", "chief revenue officer", "chief of sales",
    "head of sales", "vp of sales", "vice president of sales", "director of sales",
    "vp of revops", "vp of revenue operations", "vice president of revops",
    "vice president of revenue operations",
}


def is_newly_hired_leader(job_title: str, role_start_date: date | None, today: date) -> bool:
    """
    role_start_date should come from the ANCHORED role (see classification-qualification skill,
    Stage 5) when a contact holds multiple concurrent roles -- not just any current role.
    Enrichment sources may only return month+year precision (no exact day); treat results near
    the 90-day boundary as approximate rather than exact.
    """
    if not role_start_date or job_title.strip().lower() not in LEADERSHIP_TITLES:
        return False
    return (today - role_start_date).days < 90


CATEGORY_PRIORITY = [
    "sales management & leadership",   # Sales Manager/Director, VP/Head of Sales
    "deal closing",                    # Account Executive
    "revops & enablement",             # RevOps, Sales Ops, GTM Ops, Deal Desk, Sales Enablement
    "top-of-funnel pipeline generation",  # SDR, BDR
    "renewal/expansion csm",
]


def find_hiring_signal(company_domain: str, contact_location: str) -> dict | None:
    """
    Query PredictLeads for ALL open roles at company_domain posted in the last 30 days (the MCP
    search does not pre-filter by location -- apply that filter here). Keep only postings that:
      - match contact_location on exact city, exact state, OR exact country (any one is enough)
      - fall into one of the categories in CATEGORY_PRIORITY
      - are still live (discard stale/expired postings)
    Rank survivors by CATEGORY_PRIORITY (highest first), then by most recent posted date as the
    tie-break within the same priority tier. Return only the single top-ranked match.

    TODO: implement the PredictLeads MCP call, location filter, category classification, and
    the ranking described above.
    Returns: {"hiring_detail": str, "job_url": str, "category": str} or None.
    """
    raise NotImplementedError


def extract_atomic_processes(job_url: str) -> list[str]:
    """
    TODO: fetch the job posting at job_url and extract exactly 3 atomic, sales/revenue-
    prioritized processes per the rules in the classification-qualification skill file.
    """
    raise NotImplementedError


def detect_signal(job_title: str, role_start_date, company_domain: str, contact_location: str,
                   today: date) -> dict:
    if is_newly_hired_leader(job_title, role_start_date, today):
        return {"outreach_signal": "Newly Hired Sales/RevOps Leader"}

    hiring = find_hiring_signal(company_domain, contact_location)
    if hiring:
        processes = extract_atomic_processes(hiring["job_url"])
        return {
            "outreach_signal": "Company Hiring Sales/RevOps Roles",
            "hiring_detail": hiring["hiring_detail"],
            "process_1": processes[0], "process_2": processes[1], "process_3": processes[2],
        }

    return {"outreach_signal": "Post Engagers - Like"}
