# Tableau Server-to-Cloud Migration Toolkit

Migrate data sources, workbooks, and subscriptions from Tableau Server to Tableau Cloud using the [Tableau Migration SDK](https://help.tableau.com/current/api/migration_sdk/en-us/).

## What gets migrated

| Content type | Script | Configurable |
|---|---|---|
| Data Sources | `content_migration.py` | Yes (`migration_scope`) |
| Workbooks | `content_migration.py` | Yes (`migration_scope`) |
| Subscriptions | `subscriptions/simple_subscription_migration.py` | - |

Users, groups, and projects are **always skipped** — they must already exist in your Cloud site.

## Prerequisites

- Python 3.8+
- [Tableau Migration SDK](https://pypi.org/project/tableau-migration/): `pip install tableau-migration`
- A personal access token for both Server and Cloud
- Users and projects pre-created in Tableau Cloud

## Quick start

### 1. Configure credentials

```bash
cp config.json.template config.json
# Edit config.json with your actual values
```

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for field-by-field guidance.

### 2. Preview with dry run

```bash
# Works without the SDK installed
python dry_run.py

# Or preview through the migration scripts
python content_migration.py --dry-run
python subscriptions/simple_subscription_migration.py --dry-run
```

### 3. Run the migration

```bash
# Migrate data sources and workbooks
python content_migration.py

# Migrate subscriptions (run separately, after content)
python subscriptions/simple_subscription_migration.py
```

## Configuration

`config.json` fields:

| Field | Description |
|---|---|
| `source.server_url` | Tableau Server URL |
| `source.site_content_url` | Site name (empty string `""` for default site) |
| `source.access_token_name` / `access_token` | Server PAT credentials |
| `destination.pod_url` | Cloud pod URL (e.g. `https://10ax.online.tableau.com`) |
| `destination.site_content_url` | Cloud site name |
| `destination.access_token_name` / `access_token` | Cloud PAT credentials |
| `default_content_owner` | Cloud email to own content when original owner is missing |
| `default_email_domain` | Domain appended to bare usernames (e.g. `@yourcompany.com`) |
| `migration_scope.data_sources` | `true`/`false` — migrate data sources (default: `true`) |
| `migration_scope.workbooks` | `true`/`false` — migrate workbooks (default: `true`) |

## Dry-run mode

All three entry points support a preview mode that validates config and shows what would happen, without touching either server:

```
python dry_run.py                  # Config validation only (no SDK needed)
python dry_run.py --connect        # Also verify credentials via SDK
python content_migration.py --dry-run
```

## Project structure

```
content_migration.py               # Migrate data sources & workbooks
dry_run.py                         # Standalone config validator
migration_utils.py                 # Shared config, filters, mapping, reporting
config.json.template               # Config template (safe to commit)
subscriptions/
  simple_subscription_migration.py # Migrate subscriptions only
tests/                             # pytest suite (49 tests)
docs/                              # Additional guides and reference
```

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

Tests run without the Tableau Migration SDK installed — stub base classes in `migration_utils.py` allow all pure-Python logic to be tested independently.

## Security

`config.json` contains sensitive credentials and is listed in `.gitignore`. Never commit it — only commit `config.json.template`.
