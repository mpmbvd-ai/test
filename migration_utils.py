"""
Shared Utilities for Tableau Migration Scripts
Common logging, configuration, filters, and mapping logic
used by both content_migration.py and subscription migration.
"""

import logging
import json
from pathlib import Path

try:
    from tableau_migration import (
        TableauCloudUsernameMappingBase,
        ContentFilterBase,
        IUser,
        IGroup,
        IProject,
        IDataSource,
        IWorkbook
    )
except ImportError:
    # SDK not available (e.g., testing without .NET runtime).
    # Provide stub base classes so pure-Python utilities remain importable.
    class TableauCloudUsernameMappingBase:
        pass

    class _ContentFilterBaseMeta(type):
        def __getitem__(cls, item):
            return cls

    class ContentFilterBase(metaclass=_ContentFilterBaseMeta):
        pass

    IUser = IGroup = IProject = IDataSource = IWorkbook = None


# =============================================================================
# LOGGING SETUP
# =============================================================================

def configure_logging():
    """Configure logging - show migration progress but suppress verbose HTTP/retry logs."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    # Silence the noisy loggers (HTTP requests, retries, etc.)
    noisy_loggers = [
        'System.Net.Http.HttpClient.DefaultHttpClient.LogicalHandler',
        'System.Net.Http.HttpClient.DefaultHttpClient.ClientHandler',
        'Tableau.Migration.Net.Logging.HttpActivityLogger',
        'Tableau.Migration.Engine.Conversion.Schedules.ServerToCloudScheduleConverter',
        'Tableau.Migration.Engine.Hooks.Transformers',
        'Polly',
        'System.Net.Http.HttpClient',
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL)

    # Keep migration engine at INFO to see content creation messages
    logging.getLogger('Tableau.Migration.Engine').setLevel(logging.INFO)


# =============================================================================
# CONFIGURATION - Load and validate config.json
# =============================================================================

# Default migration scope when not specified in config
DEFAULT_MIGRATION_SCOPE = {
    'data_sources': True,
    'workbooks': True,
}


def load_config(config_path='config.json'):
    """Load credentials from config.json file."""
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"Config file not found: {config_path}")
        print(f"\nSetup instructions:")
        print(f"   1. Copy the template: cp config.json.template config.json")
        print(f"   2. Edit config.json with your actual credentials")
        print(f"   3. Run this script again\n")
        return None

    with open(config_file, 'r') as f:
        return json.load(f)


def validate_config(config):
    """Validate that config has all required fields."""
    if not config:
        return False

    required_fields = {
        'source': ['server_url', 'site_content_url', 'access_token_name', 'access_token'],
        'destination': ['pod_url', 'site_content_url', 'access_token_name', 'access_token']
    }

    # Fields where empty string is a valid value (e.g., default site)
    allow_empty = {'site_content_url'}

    missing = []

    for section, fields in required_fields.items():
        if section not in config:
            missing.append(f"Missing '{section}' section")
            continue
        for field in fields:
            if field not in config[section]:
                missing.append(f"{section}.{field}")
            elif not config[section][field] and field not in allow_empty:
                missing.append(f"{section}.{field}")

    if 'default_content_owner' not in config or not config['default_content_owner']:
        missing.append("default_content_owner (email of user to own content when original owner doesn't exist)")

    if 'default_email_domain' not in config or not config['default_email_domain']:
        missing.append("default_email_domain (e.g., '@yourcompany.com' - appended to usernames without '@')")

    if missing:
        print("Missing or empty fields in config.json:")
        for m in missing:
            print(f"   - {m}")
        return False

    return True


def get_migration_scope(config):
    """
    Parse migration_scope from config with sensible defaults.

    Returns a dict like {'data_sources': True, 'workbooks': True}.
    If migration_scope is missing from config, all content types
    default to True (migrate everything).
    """
    scope = config.get('migration_scope', {})
    return {key: scope.get(key, default) for key, default in DEFAULT_MIGRATION_SCOPE.items()}


# =============================================================================
# FILTERS - Skip content types that should not be migrated
# =============================================================================

class SkipUserMigration(ContentFilterBase[IUser]):
    """Don't migrate users - they should already exist in Cloud."""

    def should_migrate(self, item):
        return False


class SkipGroupMigration(ContentFilterBase[IGroup]):
    """Don't migrate groups - they should already exist in Cloud."""

    def should_migrate(self, item):
        return False


class SkipProjectMigration(ContentFilterBase[IProject]):
    """Don't migrate projects - they should already exist in Cloud."""

    def should_migrate(self, item):
        return False


class SkipDataSourceMigration(ContentFilterBase[IDataSource]):
    """Don't migrate data sources - they should already exist in Cloud."""

    def should_migrate(self, item):
        return False


class SkipWorkbookMigration(ContentFilterBase[IWorkbook]):
    """Don't migrate workbooks - they should already exist in Cloud."""

    def should_migrate(self, item):
        return False


# =============================================================================
# DRY-RUN REPORT - Preview migration without executing
# =============================================================================

# Sample usernames used to preview email mapping behavior
SAMPLE_USERNAMES = ["jsmith", "alice.jones", "bob@existing.com", "admin"]


def print_dry_run_report(config):
    """
    Print a pre-migration validation report.

    Shows configuration, migration scope, email mapping preview,
    and connectivity info — everything that would happen during
    migration, without actually migrating anything.
    """
    scope = get_migration_scope(config)
    email_domain = config.get('default_email_domain', '')
    default_owner = config.get('default_content_owner', '')

    print()
    print("=" * 60)
    print("  DRY-RUN REPORT")
    print("=" * 60)

    # 1. Connection info
    print("\n1. CONNECTION INFO")
    print("-" * 40)
    src = config.get('source', {})
    dst = config.get('destination', {})
    print(f"   Source:      {src.get('server_url', '?')}")
    print(f"   Source site: {src.get('site_content_url') or 'Default'}")
    print(f"   Dest:        {dst.get('pod_url', '?')}")
    print(f"   Dest site:   {dst.get('site_content_url', '?')}")
    print(f"   Token (src): {src.get('access_token_name', '?')}")
    print(f"   Token (dst): {dst.get('access_token_name', '?')}")

    # 2. Ownership
    print(f"\n2. CONTENT OWNERSHIP")
    print("-" * 40)
    print(f"   Default owner: {default_owner}")
    print(f"   Email domain:  {email_domain}")

    # 3. Migration scope
    print(f"\n3. MIGRATION SCOPE")
    print("-" * 40)
    for content_type, will_migrate in scope.items():
        label = content_type.replace('_', ' ').title()
        status = "WILL MIGRATE" if will_migrate else "SKIP"
        marker = ">>>" if will_migrate else "   "
        print(f"   {marker} {label}: {status}")
    print(f"       Users: SKIP (always)")
    print(f"       Groups: SKIP (always)")
    print(f"       Projects: SKIP (always)")

    # 4. Email mapping preview
    print(f"\n4. EMAIL MAPPING PREVIEW")
    print("-" * 40)
    for username in SAMPLE_USERNAMES:
        mapped = preview_email_mapping(username, email_domain)
        print(f"   {username:<30} -> {mapped}")

    # 5. What would happen
    items_to_migrate = [k for k, v in scope.items() if v]
    items_to_skip = [k for k, v in scope.items() if not v]

    print(f"\n5. SUMMARY")
    print("-" * 40)
    if items_to_migrate:
        print(f"   Will migrate: {', '.join(t.replace('_', ' ') for t in items_to_migrate)}")
    else:
        print(f"   Will migrate: (nothing)")
    skipped = [t.replace('_', ' ') for t in items_to_skip]
    skipped.extend(["users", "groups", "projects"])
    print(f"   Will skip:    {', '.join(skipped)}")

    print()
    print("=" * 60)
    print("  DRY RUN COMPLETE - no changes were made")
    print("=" * 60)
    print()


def preview_email_mapping(username, email_domain):
    """
    Preview how a username would be mapped to a Cloud email.

    Same logic as EmailDomainMapping.map() but without SDK context objects.
    """
    if "@" in username:
        return username
    domain = email_domain if email_domain.startswith('@') else f"@{email_domain}"
    return f"{username}{domain}"


# =============================================================================
# USERNAME MAPPING - Map Server usernames to Cloud emails
# =============================================================================

class EmailDomainMapping(TableauCloudUsernameMappingBase):
    """
    Map Server usernames to Cloud email addresses.

    If the username already contains '@', it is used as-is.
    Otherwise, the configured email domain is appended.

    Args:
        email_domain: Domain to append (e.g., '@yourcompany.com').
        default_owner: Optional fallback email for content ownership.
    """

    def __init__(self, email_domain, default_owner=None):
        self.email_domain = email_domain
        self.default_owner = default_owner
        super().__init__()

    def map(self, ctx):
        username = ctx.content_item.name
        _tableau_user_domain = ctx.mapped_location.parent()

        if "@" in username:
            mapped_email = username
        else:
            # Ensure domain starts with '@'
            domain = self.email_domain if self.email_domain.startswith('@') else f"@{self.email_domain}"
            mapped_email = f"{username}{domain}"

        print(f"Mapping: {username} -> {mapped_email}")
        return ctx.map_to(_tableau_user_domain.append(mapped_email))
