"""
Example 6: Complete Subscription Migration (Python)
====================================================

Puts everything together: Projects + Users + Subscriptions
This is a production-ready example with all the pieces.
"""

from tableau_migration import PyUser, PyProject, PySubscription
from tableau_migration.migration import PyMigrationPlanBuilder
from tableau_migration.migration_engine_hooks_mappings import PyContentMappingContext
from tableau_migration.migration_engine_hooks_filters import PyContentFilterContext
import asyncio
import csv
from pathlib import Path


# PROJECT MAPPING: Rename projects for Cloud
class CloudProjectMapping:
    """Rename projects during migration."""

    PROJECT_MAPPINGS = {
        "Marketing Campaigns": "Cloud - Marketing",
        "Sales Analytics": "Cloud - Sales",
        "Finance Reports": "Cloud - Finance"
    }

    def map(self, ctx: PyContentMappingContext[PyProject]) -> PyContentMappingContext[PyProject]:
        project = ctx.content_item
        project_name = project.location.name

        if project_name in self.PROJECT_MAPPINGS:
            new_name = self.PROJECT_MAPPINGS[project_name]
            print(f"📁 Project: {project_name} → {new_name}")
            return ctx.map_to(project.location.rename(new_name))

        return ctx


# USER MAPPING: Convert usernames to emails (CSV-based)
class CloudUserMapping:
    """Load user mappings from CSV, or use default domain append."""

    def __init__(self, csv_path: str = None, default_domain: str = "@company.com"):
        self.default_domain = default_domain
        self.mappings = {}

        if csv_path and Path(csv_path).exists():
            self.mappings = self._load_csv(csv_path)

    def _load_csv(self, csv_path: str) -> dict:
        """Load mappings from CSV."""
        mappings = {}
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row.get('ServerUsername', '').strip()
                email = row.get('CloudEmail', '').strip()
                if username and email:
                    mappings[username.lower()] = email
        print(f"📄 Loaded {len(mappings)} user mappings from CSV")
        return mappings

    def map(self, ctx: PyContentMappingContext[PyUser]) -> PyContentMappingContext[PyUser]:
        user = ctx.content_item
        username = user.name

        # Already an email?
        if "@" in username:
            return ctx

        # Check CSV first
        if username.lower() in self.mappings:
            email = self.mappings[username.lower()]
            print(f"👤 User (CSV): {username} → {email}")
            return ctx.map_to(user.location.with_username(email))

        # Default: append domain
        email = f"{username}{self.default_domain}"
        print(f"👤 User (default): {username} → {email}")
        return ctx.map_to(user.location.with_username(email))


# FILTER: Skip test subscriptions
class ExcludeTestSubscriptionsFilter:
    """Filter out subscriptions with 'TEST' in the subject."""

    def should_migrate(self, ctx: PyContentFilterContext[PySubscription]) -> bool:
        subscription = ctx.item

        # Check if subscription subject contains "TEST"
        if subscription.subject and "TEST" in subscription.subject.upper():
            print(f"⏭️  Skipping test subscription: {subscription.subject}")
            return False  # Don't migrate

        return True  # Migrate this subscription


async def complete_subscription_migration():
    """
    Complete production-ready subscription migration.
    Includes project mapping, user mapping, and subscription filtering.
    """

    print("=================================================")
    print("  COMPLETE SUBSCRIPTION MIGRATION TO CLOUD")
    print("=================================================\n")

    # Optional CSV path (if you have one)
    csv_path = "user_mappings.csv"

    if not Path(csv_path).exists():
        print(f"ℹ️  No CSV found at {csv_path}")
        print(f"   Using default domain append for users\n")
        csv_path = None

    print("Building migration plan...\n")

    plan_builder = PyMigrationPlanBuilder()

    plan_builder = (
        plan_builder
        # SOURCE: On-premises Tableau Server
        .from_source_tableau_server(
            server_url="https://tableau-server.company.com",
            site_content_url="marketing",
            access_token_name="onprem-token",
            access_token="onprem-secret"
        )
        # DESTINATION: Tableau Cloud
        .to_destination_tableau_cloud(
            pod_url="https://10ax.online.tableau.com",
            site_content_url="production",
            access_token_name="cloud-token",
            access_token="cloud-secret"
        )
    )

    # ⭐ MAPPINGS: Transform content during migration
    plan_builder.mappings.add(CloudProjectMapping())
    plan_builder.mappings.add(CloudUserMapping(csv_path, "@company.com"))

    # ⭐ FILTERS: Exclude test content (optional)
    plan_builder.filters.add(ExcludeTestSubscriptionsFilter())

    print("✓ Plan built successfully\n")

    plan = plan_builder.build()

    # EXECUTE MIGRATION
    print("Starting migration...\n")
    result = await plan.execute_async()

    # REPORT RESULTS
    print("\n=================================================")
    print("  MIGRATION RESULTS")
    print("=================================================\n")

    if result.status == "Completed":
        print("✅ Migration completed successfully!\n")

        manifest = result.manifest

        print(f"📊 Migration Summary:")
        print(f"   Users:         {len(manifest.entries.get_by_type('User'))}")
        print(f"   Groups:        {len(manifest.entries.get_by_type('Group'))}")
        print(f"   Projects:      {len(manifest.entries.get_by_type('Project'))}")
        print(f"   Data Sources:  {len(manifest.entries.get_by_type('DataSource'))}")
        print(f"   Workbooks:     {len(manifest.entries.get_by_type('Workbook'))}")
        print(f"   Subscriptions: {len(manifest.entries.get_by_type('Subscription'))}")
        print()
    else:
        print(f"❌ Migration failed: {result.status}\n")

        # Show errors if any
        if result.errors:
            for error in result.errors:
                print(f"   Error: {error}")

    print("=================================================\n")


if __name__ == "__main__":
    asyncio.run(complete_subscription_migration())


"""
REAL-WORLD SCENARIO:

SOURCE (Tableau Server - On-Premises):
├── Site: "marketing"
├── Users:
│   ├── jsmith                           (username)
│   └── ajones                           (username)
├── Projects:
│   ├── Marketing Campaigns
│   └── Sales Analytics
├── Workbooks:
│   ├── "Q4 Campaign Report" (in Marketing Campaigns)
│   └── "Revenue Dashboard" (in Sales Analytics)
└── Subscriptions:
    ├── jsmith → "Q4 Campaign Report" (Every Monday)
    ├── ajones → "Revenue Dashboard" (Every Friday)
    └── test_user → "TEST Dashboard" (Filtered out!)

AFTER MIGRATION (Tableau Cloud):
├── Site: "production"
├── Users:
│   ├── john.smith@company.com           ← Mapped!
│   └── alice.jones@company.com          ← Mapped!
├── Projects:
│   ├── Cloud - Marketing                ← Renamed!
│   └── Cloud - Sales                    ← Renamed!
├── Workbooks:
│   ├── "Q4 Campaign Report" (in Cloud - Marketing)
│   └── "Revenue Dashboard" (in Cloud - Sales)
└── Subscriptions:
    ├── john.smith@company.com → "Q4 Campaign Report" (Every Monday)
    └── alice.jones@company.com → "Revenue Dashboard" (Every Friday)
    (Test subscription was filtered out)

THE SDK AUTOMATICALLY:
1. Migrates users with new emails (from CSV or default domain)
2. Migrates projects with new names
3. Migrates workbooks to new project locations
4. Migrates subscriptions with updated user references
5. Adjusts schedules for Cloud compatibility
6. Filters out test subscriptions
7. Handles errors gracefully

WHAT YOU CONTROL:
- Mapping rules (CSV or code)
- Filters (what to exclude)
- Transformations (optional modifications)
- Error handling and logging

PYTHON ADVANTAGES:
✅ Simpler than C# - no dependency injection
✅ Built-in CSV support - no extra libraries
✅ Clear, readable code
✅ Easy to test and debug
✅ Familiar to most data teams
✅ Can integrate with pandas for complex mappings

YOUR WORKFLOW:
1. Export users to CSV
2. Edit CSV with correct emails
3. Update PROJECT_MAPPINGS dict in code
4. Run this script
5. Review results
6. Done!
"""
