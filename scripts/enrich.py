"""
Stage 3: Enrichment waterfall.

Fixed order for BOTH contact and company enrichment: GetLeads.io -> Icypeas -> Prospeo.
Move to the next tool only when the previous one returns no data or is out of credits.
Needed fields: company name, domain, HQ location, employee count, annual revenue estimate,
job title, role start date (for the newly-hired-leader signal).

All three are official hosted MCP connectors, authenticated via claude.ai Connectors -- call
them as tools inside a Claude Code session, not as raw HTTP requests. No API keys needed here.
"""


def enrich_via_getleads(linkedin_url: str) -> dict | None:
    """
    TODO: call the GetLeads.io MCP tool(s) for contact + company enrichment.
    Return None (not an error) if no match is found, so the waterfall can continue.
    """
    raise NotImplementedError


def enrich_via_icypeas(linkedin_url: str) -> dict | None:
    """
    Icypeas tools confirmed live (21 total; relevant ones for this pipeline):
      - profile-scraper(linkedin_url) -> full profile data (job title, work history/dates)
      - company-search(name_or_domain) -> resolves to the company's LinkedIn page URL
      - company-scraper(company_linkedin_url) -> full company data (headcount, industry, etc.)
      - bulk-profile-scraper / bulk-company-scraper -> same, batched (use these once records
        are processed in batches rather than one at a time, to cut down tool-call volume)
    Revenue is not reliably on a LinkedIn company page -- if company-scraper doesn't return it,
    that's expected; GetLeads.io/Prospeo higher in the waterfall are the more likely source.

    TODO: call profile-scraper for contact data. If a company LinkedIn URL isn't already known,
    call company-search first, then company-scraper. Return None if no match is found.
    """
    raise NotImplementedError


def enrich_via_prospeo(linkedin_url: str) -> dict | None:
    """
    TODO: call the Prospeo MCP tool(s) -- enrich_person / enrich_company -- for contact +
    company enrichment. Return None if no match is found.
    """
    raise NotImplementedError


def enrich_contact(linkedin_url: str) -> dict | None:
    """Runs the fixed waterfall in order, returns the first successful result plus its source."""
    for source_name, fn in [
        ("GetLeads.io", enrich_via_getleads),
        ("Icypeas", enrich_via_icypeas),
        ("Prospeo", enrich_via_prospeo),
    ]:
        result = fn(linkedin_url)
        if result:
            result["enrichment_source"] = source_name
            return result
    return None  # all three tools missed -> caller must exclude at company-fit stage


if __name__ == "__main__":
    import sys
    print(enrich_contact(sys.argv[1]) if len(sys.argv) > 1 else "usage: enrich.py <linkedin_url>")
