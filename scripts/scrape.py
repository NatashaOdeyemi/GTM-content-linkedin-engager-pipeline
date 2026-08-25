"""
Stage 1: Scrape post engagers.

Actor: harvestapi/linkedin-profile-posts (LinkedIn Profile Posts Scraper, No Cookies)
Config (from spec): max 1 post per profile input, posted limit 24h, reactions on (max 100),
comments on (max 100, filtered to last week).

Apify is an official hosted MCP connector (mcp.apify.com), authenticated via claude.ai
Connectors using OAuth. Call it as a tool (start actor run, get run status/dataset), not a raw
HTTP request, inside a Claude Code session or routine.

Runs against every profile in config/tracked_profiles.json.
"""
import json

ACTOR_ID = "harvestapi/linkedin-profile-posts"


def load_tracked_profiles(path="config/tracked_profiles.json"):
    with open(path) as f:
        return json.load(f)


def run_actor_for_profile(profile_url: str) -> dict:
    """
    TODO: call the Apify MCP tool to start a run of ACTOR_ID for a single profile URL with the
    settings above, poll for completion (get run status), then fetch the dataset items (post +
    reactions + comments). Apify's MCP tools cover start/status/abort for a specific run, not a
    "list all recent runs" browse -- capture and hold the run ID returned at start time.
    """
    raise NotImplementedError


def scrape_all() -> list[dict]:
    """Returns a flat list of {post, engager, engagement_type} records across all tracked profiles."""
    config = load_tracked_profiles()
    owner = config["owner_profile"]
    records = []
    for profile_url in config["tracked_profiles"]:
        raw = run_actor_for_profile(profile_url)
        # TODO: flatten raw actor output into per-engager records, tagging
        # data_source = "My Post" if profile_url == owner else "Competitor Post"
        # engagement_type = "like" | "comment"
    return records


if __name__ == "__main__":
    results = scrape_all()
    print(f"Scraped {len(results)} raw engagement records")
