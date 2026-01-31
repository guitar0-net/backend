# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Thread-safe singleton for Prometheus CollectorRegistry."""

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prometheus_client import CollectorRegistry

_registry: "CollectorRegistry | None" = None
_lock = threading.Lock()


def get_registry() -> "CollectorRegistry":
    """Get or create the singleton CollectorRegistry.

    Uses double-checked locking for thread-safe lazy initialization.

    Returns:
        The singleton CollectorRegistry instance.
    """
    global _registry  # noqa: PLW0603

    if _registry is None:
        with _lock:
            if _registry is None:
                from prometheus_client import CollectorRegistry  # noqa: PLC0415

                _registry = CollectorRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the registry singleton. Only for testing."""
    global _registry  # noqa: PLW0603

    with _lock:
        _registry = None
