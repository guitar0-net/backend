<!--
SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Send a report to **guitar0.app@gmail.com** with:

- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Affected versions (if known)

You will receive an acknowledgement within **48 hours** and a status update within **7 days**.

Once the issue is confirmed and fixed, a patch release will be made and you will be credited in the release notes (unless you prefer to remain anonymous).

## Scope

In scope:
- Authentication and authorisation bypasses
- SQL injection, XSS, CSRF
- Sensitive data exposure via the REST API
- Dependency vulnerabilities with a known exploit

Out of scope:
- Issues requiring physical access to the server
- Social engineering attacks
- Denial-of-service without a realistic attack vector
