"""
Stage 8 (copy): generates the per-contact opener using .claude/skills/copywriting.md as the
system prompt. Only run this on records that passed every gate in qualify.py.
"""


def generate_message(qualified_record: dict) -> dict:
    """
    TODO: send qualified_record's outreach_signal, specific_point/topic, problem_area, and (where
    applicable) hiring_detail/process_1-3 to Claude with the copywriting skill as system prompt.
    Expect the strict-JSON shape documented at the end of that skill file back
    (option_a, option_b, implication, engaged_with, low_friction_offer, cta, full_message).
    """
    raise NotImplementedError


if __name__ == "__main__":
    pass
