"""
Example 2: Project Mapping (Python)
====================================

Shows how to RENAME projects during migration.
This is essential when your Cloud site has different naming conventions.
"""

from tableau_migration import PyContentReference, PyProject
from tableau_migration.migration import PyMigrationPlanBuilder
from tableau_migration.migration_engine_hooks_mappings import PyContentMappingContext
import asyncio


class CustomProjectMapping:
    """
    Custom mapping class to rename projects during migration.
    Python approach: Simple class with a map() method.
    """

    # Dictionary of project name mappings
    # Key = Source project name
    # Value = Destination project name
    PROJECT_MAPPINGS = {
        "Campaign Analytics": "Marketing - Campaigns",
        "Sales Metrics": "Sales - Metrics",
        "Finance Reports": "Finance - Monthly Reports"
    }

    def map(self, ctx: PyContentMappingContext[PyProject]) -> PyContentMappingContext[PyProject]:
        """
        Called for EACH project during migration.

        Args:
            ctx: Context containing the project being migrated

        Returns:
            Updated context with new project name, or original context
        """
        project = ctx.content_item
        current_name = project.location.name

        print(f"🔍 Checking project: {current_name}")

        # Check if we have a mapping rule for this project
        if current_name in self.PROJECT_MAPPINGS:
            new_name = self.PROJECT_MAPPINGS[current_name]
            print(f"  ✏️  Renaming: {current_name} → {new_name}")

            # Create new location with the new name
            new_location = project.location.rename(new_name)

            # Return mapped context with new location
            return ctx.map_to(new_location)

        # No mapping needed, keep the same name
        print(f"  ✓ Keeping name: {current_name}")
        return ctx


async def migration_with_project_mapping():
    """
    Run a migration with project renaming.
    """

    plan_builder = PyMigrationPlanBuilder()

    # Configure source and destination
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

    # ⭐ HERE'S THE KEY: Register the project mapping
    plan_builder.mappings.add(CustomProjectMapping())

    # Build and execute
    plan = plan_builder.build()

    print("Starting migration with project mapping...")
    result = await plan.execute_async()

    if result.status == "Completed":
        print("✅ Migration completed with project renaming!")
    else:
        print(f"❌ Migration failed: {result.status}")


if __name__ == "__main__":
    asyncio.run(migration_with_project_mapping())


"""
WHAT HAPPENS NOW:

SOURCE (Tableau Server - "marketing" site):
├── Campaign Analytics
│   └── Q4 Dashboard.twbx
└── Sales Metrics
    └── Revenue Report.twbx

DESTINATION (Tableau Cloud - "corporate" site):
├── Marketing - Campaigns  ← Renamed!
│   └── Q4 Dashboard.twbx
└── Sales - Metrics  ← Renamed!
    └── Revenue Report.twbx

IMPORTANT: Workbooks automatically follow to the new project names!
You don't need to map workbooks separately - SDK handles that.

WHAT ABOUT SUBSCRIPTIONS?
- If "Q4 Dashboard.twbx" had a subscription on the source,
- The SDK will create a subscription for "Q4 Dashboard.twbx" in "Marketing - Campaigns"
- BUT we still need to map USERS (see next example)

PYTHON ADVANTAGES:
- Much simpler than C#! No dependency injection needed
- Just create a class with a map() method
- Add it with .mappings.add(YourMapping())
- That's it!
"""
