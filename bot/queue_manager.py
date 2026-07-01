"""
In-memory matching engine for the MVP.

For an MVP single-process deployment, an in-memory queue + lock is
simpler and faster than round-tripping to Postgres on every tick.
If you outgrow a single process, swap this for a Redis-backed queue
with the same public interface (find_match / add_to_queue / remove).

Active chats are also tracked here (telegram_id -> partner telegram_id,
match_id) so message relaying doesn't need a DB lookup per message.
"""
import asyncio
from dataclasses import dataclass, field
from time import time
from typing import Optional


@dataclass
class QueueEntry:
    telegram_id: int
    native_language: str
    learning_language: str
    level: str
    gender: str
    interests: set
    premium: bool
    filter_gender: Optional[str] = None   # premium-only filter
    filter_interests: set = field(default_factory=set)  # premium-only filter
    joined_at: float = field(default_factory=time)


class MatchingEngine:
    def __init__(self):
        self._queue: dict[int, QueueEntry] = {}
        self._active_chats: dict[int, dict] = {}  # telegram_id -> {partner_id, match_id}
        self._lock = asyncio.Lock()

    # ---------------- Queue management ----------------
    async def add_to_queue(self, entry: QueueEntry) -> "Optional[QueueEntry]":
        """Adds user to queue and immediately tries to find a match.
        Returns the matched partner's QueueEntry if a match was made
        and removes both from the queue. Returns None if no match yet
        (user stays queued)."""
        async with self._lock:
            partner = self._find_best_match(entry)
            if partner:
                del self._queue[partner.telegram_id]
                return partner
            self._queue[entry.telegram_id] = entry
            return None

    async def remove_from_queue(self, telegram_id: int) -> None:
        async with self._lock:
            self._queue.pop(telegram_id, None)

    def is_in_queue(self, telegram_id: int) -> bool:
        return telegram_id in self._queue

    def _find_best_match(self, entry: QueueEntry) -> "Optional[QueueEntry]":
        candidates = list(self._queue.values())

        def passes_filters(a: QueueEntry, b: QueueEntry) -> bool:
            if a.filter_gender and b.gender != a.filter_gender:
                return False
            if b.filter_gender and a.gender != b.filter_gender:
                return False
            if a.filter_interests and not (a.filter_interests & b.interests):
                return False
            if b.filter_interests and not (b.filter_interests & a.interests):
                return False
            return True

        # Priority 1: native <-> learning exact match
        for c in candidates:
            if (
                c.native_language == entry.learning_language
                and c.learning_language == entry.native_language
                and passes_filters(entry, c)
            ):
                return c

        # Priority 2: same learning language (language exchange peers)
        same_learning = [
            c
            for c in candidates
            if c.learning_language == entry.learning_language
            and c.telegram_id != entry.telegram_id
            and passes_filters(entry, c)
        ]
        if same_learning:
            # Priority 3: closest level among same_learning
            order = ["A1", "A2", "B1", "B2", "C1", "C2", "native"]

            def level_idx(level: str) -> int:
                return order.index(level) if level in order else len(order) // 2

            same_learning.sort(key=lambda c: abs(level_idx(c.level) - level_idx(entry.level)))
            return same_learning[0]

        return None

    # ---------------- Active chat management ----------------
    async def start_chat(self, telegram_id_a: int, telegram_id_b: int, match_id: int) -> None:
        async with self._lock:
            self._active_chats[telegram_id_a] = {"partner_id": telegram_id_b, "match_id": match_id}
            self._active_chats[telegram_id_b] = {"partner_id": telegram_id_a, "match_id": match_id}

    def get_chat(self, telegram_id: int) -> Optional[dict]:
        return self._active_chats.get(telegram_id)

    async def end_chat(self, telegram_id: int) -> "Optional[dict]":
        """Ends the chat for both participants. Returns the chat info
        that was removed (containing the partner id), or None."""
        async with self._lock:
            info = self._active_chats.pop(telegram_id, None)
            if info:
                self._active_chats.pop(info["partner_id"], None)
            return info

    def is_in_chat(self, telegram_id: int) -> bool:
        return telegram_id in self._active_chats


# Singleton instance shared by all handlers
engine = MatchingEngine()