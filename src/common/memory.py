"""Peak memory measurement using the standard library."""

from __future__ import annotations

import tracemalloc


class MemoryProbe:
    """Track peak Python allocations for a pipeline stage."""

    def __init__(self) -> None:
        self._started = False

    def start(self) -> None:
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        self._started = True

    def reset_peak(self) -> None:
        if not self._started:
            self.start()
        tracemalloc.reset_peak()

    def snapshot(self) -> float:
        """Return current/peak allocation in MB."""

        if not self._started:
            return 0.0
        current, peak = tracemalloc.get_traced_memory()
        return round(max(current, peak) / (1024 * 1024), 2)
