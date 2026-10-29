"""Encounter terrain only. It neither interprets nor authorizes."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Encounter:
    day: int
    index: int
    place: int
    truncated: bool


class Terrain:
    def __init__(self):
        self._history: deque[Encounter] = deque()
        self.encounters_seen = 0
        self.last_day = 0

    def observe(self, encounter: Encounter) -> None:
        if encounter.day < self.last_day:
            raise ValueError("encounters must arrive in chronological order")
        if encounter.place not in range(4):
            raise ValueError("unknown place")
        self._history.append(encounter)
        self.last_day = encounter.day
        self.encounters_seen += 1
        while self._history and self._history[0].day < encounter.day - 179:
            self._history.popleft()

    def snapshot(self, day: int) -> tuple[Encounter, ...]:
        return tuple(e for e in self._history if day - 179 <= e.day <= day)
