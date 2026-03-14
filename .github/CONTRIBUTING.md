<!--
SPDX-FileCopyrightText: 2025-2026 Andrey Kotlyar <guitar0.app@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Contributing to guitar0.net/server

Django + DRF REST API for a guitar education platform. Python, PDM, pytest.

## Getting Started

```bash
# Install dependencies
pdm install
pdm run pre-commit install

# Copy and fill in env vars (edit the file after copying)
cp .env.example .env.development

# Apply migrations and start the dev server
make run
```

`make run` runs pending migrations and starts the development server.

Or with Docker (no env setup needed):

```bash
docker compose up
```

Before opening a PR, make sure the tests pass:

```bash
make test
```

## Branching

Branch names determine the PR label, which determines the release category. Use these prefixes:

| Prefix                         | Label          | Release category  |
| ------------------------------ | -------------- | ----------------- |
| `feat/`                        | feature        | 🚀 Features       |
| `fix/`, `hotfix/`              | bug            | 🐛 Bug Fixes      |
| `security/`                    | security       | 🔒 Security       |
| `infra/`, `ci/`, `deploy/`     | infrastructure | 🏗 Infrastructure |
| `chore/`, `refactor/`, `docs/` | chore          | 🧹 Maintenance    |

Example: `feat/chord-diagram`, `fix/login-redirect`.

## Commits

The project uses [Conventional Commits](https://www.conventionalcommits.org/) enforced by commitizen:

```
feat: add chord diagram to lesson page
fix: resolve login redirect loop
chore: update dependencies
```

Run `pdm run cz commit` for an interactive prompt.

## Issues

Before starting significant work, open an issue to discuss the approach. For small bug fixes or typos a PR without an issue is fine.

## Pull Requests

- One concern per PR
- **Edit the PR title before merging** — it appears verbatim in the GitHub Release changelog
- We use **Squash and Merge** — the PR title becomes the single commit message on `main`

## Architecture

Strict layered architecture — never skip or merge layers:

- `models.py` — schema only, no query logic
- `selectors.py` — all DB reads (returns `QuerySet` or `Model | None`)
- `services.py` — mutations and side effects
- `api/v1/views.py` — HTTP layer, calls selectors/services only

Views never call `Model.objects` directly.

## Code Style

```bash
# Lint and format
pdm run ruff check .
pdm run ruff format .

# Type checking
pdm run mypy .
```

Every `.py` file must have an SPDX license header. If you're creating a new file, use your own name and the current year:

```python
# SPDX-FileCopyrightText: <year> <Your Name> <your@email.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
```

If you're modifying an existing file, add your line below the existing one:

```python
# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
# SPDX-FileCopyrightText: <year> <Your Name> <your@email.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
```

Pre-commit hooks enforce this automatically — install once with:

```bash
pdm run pre-commit install
```

## Testing

```bash
# Run all tests
make test

# Run specific app
pdm run pytest apps/<name>/tests/ -v

# With coverage
pdm run pytest --cov=apps/<name> apps/<name>/tests/
```

Coverage threshold: **90%**. Tests use `pytest`, `factory_boy`, and real DB (no mocks).
