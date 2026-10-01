# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Fail a pull request only on vulnerabilities the pull request introduces.

Compares two ``pip-audit -f json`` reports — one for the base branch lock file,
one for the head — and exits non-zero when the head carries a vulnerability the
base does not. Advisories published against dependencies already on the base
branch are left to the scheduled audit, so a fresh CVE never blocks unrelated
pull requests.

A vulnerability is identified by package name plus every ID it is known under
(the primary ID and its aliases), so a bump that keeps a package vulnerable to
the same advisory is not reported as new, even if the database switched the
primary ID between PYSEC, GHSA and CVE.

Usage::

    python scripts/audit_diff.py base.json head.json
"""

import json
import sys
from pathlib import Path
from typing import NotRequired, TypedDict


class Vulnerability(TypedDict):
    """One advisory entry of a pip-audit JSON report."""

    id: str
    aliases: list[str]
    fix_versions: list[str]


class Dependency(TypedDict):
    """One dependency entry of a pip-audit JSON report."""

    name: str
    version: str
    vulns: NotRequired[list[Vulnerability]]


def _load_dependencies(path: Path) -> list[Dependency]:
    report = json.loads(path.read_text(encoding="utf-8"))
    dependencies: list[Dependency] = report["dependencies"]
    return dependencies


def _known_ids(dependencies: list[Dependency]) -> set[tuple[str, str]]:
    return {
        (dependency["name"], vuln_id)
        for dependency in dependencies
        for vuln in dependency.get("vulns", [])
        for vuln_id in (vuln["id"], *vuln["aliases"])
    }


def main(argv: list[str]) -> int:
    """Print vulnerabilities present in the head report but not in the base.

    Args:
        argv: Paths to the base and the head pip-audit JSON reports.

    Returns:
        1 when the head introduces at least one vulnerability, 0 otherwise.
    """
    base_path, head_path = (Path(arg) for arg in argv)
    known = _known_ids(_load_dependencies(base_path))
    introduced = [
        (dependency, vuln)
        for dependency in _load_dependencies(head_path)
        for vuln in dependency.get("vulns", [])
        if not any(
            (dependency["name"], vuln_id) in known
            for vuln_id in (vuln["id"], *vuln["aliases"])
        )
    ]
    for dependency, vuln in introduced:
        fixes = ", ".join(vuln["fix_versions"]) or "no fix released"
        print(f"{dependency['name']} {dependency['version']}: {vuln['id']} ({fixes})")
    return 1 if introduced else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
