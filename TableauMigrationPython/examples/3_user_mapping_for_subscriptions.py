"""
Example 3: User Mapping for Subscriptions (Python)
===================================================

Shows how to map users when email domains change.
This is CRITICAL for subscriptions to work after migration.
"""

from tableau_migration import PyUser
from tableau_migration.migration import PyMigrationPlanBuilder
from tableau_migration.migration_engine_hooks_mappings import PyContentMappingContext
import asyncio


class EmailDomainMapping:
    """Change email domain for all users."""

    OLD_DOMAIN = "@oldcompany.com"
    NEW_DOMAIN = "@newcompany.com"

    def map(self, ctx: PyContentMappingContext[PyUser]) -> PyContentMappingContext[PyUser]:
        user = ctx.content_item
        current_email = user.email

        print(f"👤 Processing user: {user.name}")
        print(f"   Current email: {current_email}")

        # If email uses old domain, change it
        if current_email.endswith(self.OLD_DOMAIN):
            new_email = current_email.replace(self.OLD_DOMAIN, self.NEW_DOMAIN)
            print(f"   📧 Updating email: {current_email} → {new_email}")

            # Map to new location with updated email
            return ctx.map_to(user.location.with_username(new_email))

        print(f"   ✓ Email unchanged")
        return ctx


class SpecificUserMapping:
    """Handle specific user renames using a dictionary."""

    # Some users might have completely different usernames
    USERNAME_MAPPINGS = {
        "john.smith@oldcompany.com": "j.smith@newcompany.com",
        "sarah.jones@oldcompany.com": "jones.s@newcompany.com",
    }

    def map(self, ctx: PyContentMappingContext[PyUser]) -> PyContentMappingContext[PyUser]:
        user = ctx.content_item
        current_email = user.email

        if current_email in self.USERNAME_MAPPINGS:
            new_email = self.USERNAME_MAPPINGS[current_email]
            print(f"👤 Specific mapping: {current_email} → {new_email}")
            return ctx.map_to(user.location.with_username(new_email))

        return ctx  # No specific mapping


async def migration_with_user_mapping():
    """Run migration with user email mapping."""

    plan_builder = PyMigrationPlanBuilder()

    plan_builder = (
        plan_builder
        .from_source_tableau_server(
            server_url="https://tableau-server.company.com",
            site_content_url="marketing",
            access_token_name="server-token",
            access_token="server-secret"
        )
        .to_destination_tableau_cloud(
            pod_url="https://10ax.online.tableau.com",
            site_content_url="corporate",
            access_token_name="cloud-token",
            access_token="cloud-secret"
        )
    )

    # ⭐ Register BOTH user mappings
    # Order matters: specific mappings first, then domain mapping
    plan_builder.mappings.add(SpecificUserMapping())
    plan_builder.mappings.add(EmailDomainMapping())

    plan = plan_builder.build()

    print("Starting migration with user mapping...")
    result = await plan.execute_async()

    if result.status == "Completed":
        print("✅ Migration completed with user mapping!")
    else:
        print(f"❌ Migration failed: {result.status}")


if __name__ == "__main__":
    asyncio.run(migration_with_user_mapping())


"""
WHAT HAPPENS WITH SUBSCRIPTIONS:

SOURCE (Tableau Server):
├── User: john.smith@oldcompany.com
├── Workbook: "Q4 Dashboard"
└── Subscription:
    ├── To: john.smith@oldcompany.com
    ├── Content: "Q4 Dashboard"
    └── Schedule: Every Monday at 9 AM

MIGRATION PROCESS:
1. SDK migrates user → j.smith@newcompany.com (specific mapping)
2. SDK migrates workbook → "Q4 Dashboard"
3. SDK migrates subscription:
   ├── Finds user mapping: john.smith@oldcompany.com → j.smith@newcompany.com
   ├── Finds workbook: "Q4 Dashboard" (already migrated)
   └── Creates subscription with NEW user and NEW workbook reference

DESTINATION (Tableau Cloud):
├── User: j.smith@newcompany.com
├── Workbook: "Q4 Dashboard"
└── Subscription:
    ├── To: j.smith@newcompany.com  ← Updated!
    ├── Content: "Q4 Dashboard"
    └── Schedule: Every Monday at 9 AM

THE SDK AUTOMATICALLY:
- Tracks all user mappings
- Updates subscription references
- Adjusts schedules for Cloud compatibility
- Handles errors if users don't exist

YOU JUST PROVIDE THE MAPPING RULES!

PYTHON IS EASIER:
- No interfaces to implement
- Just create a class with map() method
- Add to plan_builder.mappings
- Done!
"""
