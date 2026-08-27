"""
Stage 3: Enrichment waterfall.

Fixed order for BOTH contact and company enrichment: HarvestAPI -> Prospeo -> Icypeas.
Move to the next tool only when the previous one returns no data or is out of credits.
Needed fields: company name, domain, HQ location, employee count, annual revenue estimate,
job title, role start date (for the newly-hired-leader signal).

Prospeo and Icypeas are official hosted MCP connectors, authenticated via claude.ai Connectors --
call them as tools inside a Claude Code session, not as raw HTTP requests. HarvestAPI is a raw
API (harvestapi.io) -- requires a HARVESTAPI_KEY environment variable, not an MCP connector, and
is unrelated to the harvestapi Apify actor used for scraping in Stage 1.

GetLeads.io has been removed from the waterfall entirely (not temporarily skipped) -- its former
implementation is commented out below rather than deleted, so it's still visible in history.

Reaction-row fallback (Stage 0b in classification-qualification.md): Apify's "like" rows carry
an opaque Sales Navigator URN as linkedinUrl instead of a resolvable public profile URL, so they
can't go straight into the waterfall below. Resolve those via a Serper (google.serper.dev) search
first -- requires a SERPER_API_KEY environment variable, not an MCP connector. Query template and
corroboration rule are specified in Stage 0b; both were validated this session against two real
engager records: a clean single-candidate resolution (name + company, corroborated by an
independent source), and a 7-way name-collision case with no employer in the headline, where a
bare-name search was hopelessly ambiguous but the full Stage 0b query template (name + full
position text as a second quoted phrase) still resolved to one corroborated candidate. Only the
resolved public URL should be passed into enrich_contact() below.
"""


# Removed from the waterfall entirely (superseded by HarvestAPI, not a temporary skip) --
# left commented out rather than deleted so the prior implementation stays visible in history.
#
# def enrich_via_getleads(linkedin_url: str) -> dict | None:
#     """
#     TODO: call the GetLeads.io MCP tool(s) for contact + company enrichment.
#     Return None (not an error) if no match is found, so the waterfall can continue.
#     """
#     raise NotImplementedError


def enrich_via_harvestapi(linkedin_url: str) -> dict | None:
    """
    TODO: call harvestapi.io's own API (raw HTTP, HARVESTAPI_KEY env var -- not an MCP
    connector, and not the harvestapi Apify actor used for scraping in Stage 1) for contact +
    company enrichment. Return None (not an error) if no match is found, so the waterfall can
    continue.
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
    that's expected; HarvestAPI/Prospeo higher in the waterfall are the more likely source.

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
        ("HarvestAPI", enrich_via_harvestapi),
        ("Prospeo", enrich_via_prospeo),
        ("Icypeas", enrich_via_icypeas),
    ]:
        result = fn(linkedin_url)
        if result:
            result["enrichment_source"] = source_name
            return result
    return None  # all three tools missed -> caller must exclude at company-fit stage


if __name__ == "__main__":
    import sys
    print(enrich_contact(sys.argv[1]) if len(sys.argv) > 1 else "usage: enrich.py <linkedin_url>")
