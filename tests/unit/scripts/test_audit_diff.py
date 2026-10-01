# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import secrets
from pathlib import Path

import pytest

from scripts import audit_diff


def _report(directory: Path, dependencies: list[audit_diff.Dependency]) -> str:
    path = directory / f"{secrets.token_hex(4)}.json"
    path.write_text(json.dumps({"dependencies": dependencies, "fixes": []}))
    return str(path)


def _dependency(name: str, vuln_id: str, aliases: list[str]) -> audit_diff.Dependency:
    return {
        "name": name,
        "version": f"{secrets.randbelow(9)}.{secrets.randbelow(99)}",
        "vulns": [{"id": vuln_id, "aliases": aliases, "fix_versions": []}],
    }


def test_main_fails_when_head_introduces_a_vulnerability(tmp_path: Path) -> None:
    head = [_dependency(f"пакет-{secrets.token_hex(3)}", secrets.token_hex(6), [])]
    assert audit_diff.main([_report(tmp_path, []), _report(tmp_path, head)]) == 1


def test_main_passes_when_vulnerability_already_exists_on_base(
    tmp_path: Path,
) -> None:
    name, vuln_id = f"пакет-{secrets.token_hex(3)}", secrets.token_hex(6)
    base = _report(tmp_path, [_dependency(name, vuln_id, [])])
    head = _report(tmp_path, [_dependency(name, vuln_id, [])])
    assert audit_diff.main([base, head]) == 0


def test_main_passes_when_base_knows_the_vulnerability_under_an_alias(
    tmp_path: Path,
) -> None:
    name, alias = f"пакет-{secrets.token_hex(3)}", secrets.token_hex(6)
    base = _report(tmp_path, [_dependency(name, alias, [])])
    head = _report(tmp_path, [_dependency(name, secrets.token_hex(6), [alias])])
    assert audit_diff.main([base, head]) == 0


def test_main_fails_when_known_vulnerability_appears_in_another_package(
    tmp_path: Path,
) -> None:
    vuln_id = secrets.token_hex(6)
    base = _report(tmp_path, [_dependency(f"α-{secrets.token_hex(3)}", vuln_id, [])])
    head = _report(tmp_path, [_dependency(f"β-{secrets.token_hex(3)}", vuln_id, [])])
    assert audit_diff.main([base, head]) == 1


def test_main_passes_when_head_dependency_carries_no_vulnerabilities(
    tmp_path: Path,
) -> None:
    head: list[audit_diff.Dependency] = [
        {"name": f"пакет-{secrets.token_hex(3)}", "version": secrets.token_hex(2)}
    ]
    assert audit_diff.main([_report(tmp_path, []), _report(tmp_path, head)]) == 0


def test_main_fails_when_a_report_is_missing(tmp_path: Path) -> None:
    missing = str(tmp_path / f"отчёт-{secrets.token_hex(4)}.json")
    with pytest.raises(FileNotFoundError):
        audit_diff.main([missing, _report(tmp_path, [])])
