"""
Example 4: Username to Email Mapping (Python)
==============================================

THE MOST COMMON CLOUD MIGRATION SCENARIO

Server uses simple usernames: "john.smith", "jsmith", "alice.jones"
Cloud requires email addresses: "john.smith@company.com", etc.

This mapping is CRITICAL for subscriptions to work!
"""

from tableau_migration import PyUser
from tableau_migration.migration import PyMigrationPlanBuilder
from tableau_migration.migration_engine_hooks_mappings import PyContentMappingContext
import asyncio


# APPROACH 1: Simple domain append
class UsernameToEmailMapping:
    """Convert simple usernames to emails by appending domain."""

    EMAIL_DOMAIN = "@company.com"

    def map(self, ctx: PyContentMappingContext[PyUser]) -> PyContentMappingContext[PyUser]:
        user = ctx.content_item
        username = user.name

        print(f"👤 Processing user: {username}")

        # Check if it's already an email (has @ symbol)
        if "@" in username:
            print(f"   ✓ Already an email: {username}")
            return ctx  # Already an email, no change needed

        # Convert username to email by appending domain
        email = f"{username}{self.EMAIL_DOMAIN}"
        print(f"   📧 Converting: {username} → {email}")

        # Map to new email address
        return ctx.map_to(user.location.with_username(email))


# APPROACH 2: Username lookup table (for non-standard mappings)
class UsernameLookupMapping:
    """
    Use a dictionary for abbreviated/special usernames.
    Falls back to appending domain for standard usernames.
    """

    # Lookup table for usernames that don't map directly
    USERNAME_MAPPINGS = {
        # Format: "Server Username": "Cloud Email"
        "jsmith": "john.smith@company.com",          # Abbreviated
        "ajones": "alice.jones@company.com",         # Abbreviated
        "bob.wilson": "robert.wilson@company.com",   # Different first name
        "admin": "admin.tableau@company.com",        # Special accounts
        "service_account": "svc.tableau@company.com" # Service accounts
    }

    DEFAULT_DOMAIN = "@company.com"

    def map(self, ctx: PyContentMappingContext[PyUser]) -> PyContentMappingContext[PyUser]:
        user = ctx.content_item
        username = user.name

        # Skip if already an email
        if "@" in username:
            return ctx

        # First, check lookup table for specific mappings
        if username in self.USERNAME_MAPPINGS:
            mapped_email = self.USERNAME_MAPPINGS[username]
            print(f"👤 Lookup mapping: {username} → {mapped_email}")
            return ctx.map_to(user.location.with_username(mapped_email))

        # Otherwise, append default domain
        default_email = f"{username}{self.DEFAULT_DOMAIN}"
        print(f"👤 Default mapping: {username} → {default_email}")
        return ctx.map_to(user.location.with_username(default_email))


async def migration_with_username_mapping():
    """Run migration converting usernames to emails."""

    print("=================================================")
    print("  SERVER USERNAME → CLOUD EMAIL MIGRATION")
    print("=================================================\n")

    plan_builder = PyMigrationPlanBuilder()

    print("Building migration plan...\n")

    plan_builder = (
        plan_builder
        # SOURCE: Tableau Server (uses simple usernames)
        .from_source_tableau_server(
            server_url="https://tableau-server.company.com",
            site_content_url="default",
            access_token_name="server-token",
            access_token="server-secret"
        )
        # DESTINATION: Tableau Cloud (requires email addresses)
        .to_destination_tableau_cloud(
            pod_url="https://10ax.online.tableau.com",
            site_content_url="production",
            access_token_name="cloud-token",
            access_token="cloud-secret"
        )
    )

    # ⭐ KEY: Register username → email mapping
    plan_builder.mappings.add(UsernameLookupMapping())

    plan = plan_builder.build()

    print("Starting migration...\n")
    result = await plan.execute_async()

    print("\n=================================================")
    print("  MIGRATION RESULTS")
    print("=================================================\n")

    if result.status == "Completed":
        print("✅ Migration completed successfully!\n")

        manifest = result.manifest
        print(f"📊 Users migrated: {len(manifest.entries.get_by_type('User'))}")
        print(f"📊 Subscriptions migrated: {len(manifest.entries.get_by_type('Subscription'))}\n")
    else:
        print(f"❌ Migration failed: {result.status}\n")
        for error in result.errors:
            print(f"   Error: {error}")

    print("=================================================\n")


if __name__ == "__main__":
    asyncio.run(migration_with_username_mapping())


"""
REAL-WORLD SCENARIO:

SOURCE (Tableau Server - Simple Usernames):
├── Users:
│   ├── jsmith            ← Just a username
│   ├── ajones            ← Just a username
│   └── bob.wilson        ← Just a username
├── Workbook: "Sales Dashboard"
└── Subscriptions:
    ├── jsmith → "Sales Dashboard" (Every Monday)
    └── ajones → "Sales Dashboard" (Every Friday)

WITHOUT MAPPING (Migration would fail!):
Cloud sees: "jsmith"
Cloud says: ❌ Invalid user - not an email address!

WITH MAPPING (Migration succeeds!):

DESTINATION (Tableau Cloud - Email Addresses):
├── Users:
│   ├── john.smith@company.com    ← Mapped from "jsmith"
│   ├── alice.jones@company.com   ← Mapped from "ajones"
│   └── robert.wilson@company.com ← Mapped from "bob.wilson"
├── Workbook: "Sales Dashboard"
└── Subscriptions:
    ├── john.smith@company.com → "Sales Dashboard" (Every Monday)
    └── alice.jones@company.com → "Sales Dashboard" (Every Friday)

WHAT THE SDK DOES:
1. Reads user "jsmith" from Server
2. Applies mapping: "jsmith" → "john.smith@company.com"
3. Creates user "john.smith@company.com" in Cloud
4. Reads subscription for "jsmith"
5. Looks up mapping: "jsmith" → "john.smith@company.com"
6. Creates subscription for "john.smith@company.com" in Cloud

THE SUBSCRIPTION AUTOMATICALLY USES THE MAPPED EMAIL!

PYTHON ADVANTAGES:
- Simple dictionary for lookups
- Clear, readable code
- No complicated configuration
- Easy to test and debug

COMMON PATTERNS:

Pattern 1: Simple append
"john.smith" → "john.smith@company.com"
Use: UsernameToEmailMapping

Pattern 2: Abbreviated usernames
"jsmith" → "john.smith@company.com"
Use: UsernameLookupMapping with dictionary

Pattern 3: Mixed (most common)
Most users: append domain
Special cases: lookup table
Use: UsernameLookupMapping (checks table first, then appends)
"""
