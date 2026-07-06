"""
Referral badge + priority-matching tier logic.

Kept separate from bot/handlers/referral.py so that queue_manager.py
and matching.py (which have nothing to do with the /invite UI) can
import just the pure tier calculation without pulling in Telegram
handler code.
"""
from bot import config


def get_badge(referral_count: int):
    """Returns (emoji, translation_key) for the highest badge earned
    at this referral count, or None if the user hasn't hit the first
    tier yet. Badges are cumulative (e.g. 12 referrals -> Community
    Builder, not Ambassador), so we scan highest-threshold-first."""
    for threshold, emoji, name_key in config.REFERRAL_BADGES:
        if referral_count >= threshold:
            return emoji, name_key
    return None


def get_priority_tier(referral_count: int) -> int:
    """0 = no matchmaking boost. Each badge tier crossed adds +1,
    so a Legend (tier 4) is preferred over a Community Builder
    (tier 2) who is preferred over someone with 1-2 referrals (tier 0).
    Mirrors the existing `premium` boost in queue_manager's sort keys,
    just one notch below it in priority."""
    tier = 0
    for threshold, _, _ in sorted(config.REFERRAL_BADGES, key=lambda b: b[0]):
        if referral_count >= threshold:
            tier += 1
    return tier