"""
Example 1: Basic Migration Setup (Python)
==========================================

This shows the absolute basics of setting up a migration in Python.
NO mapping, NO filtering - just the bare minimum to understand the structure.
"""

from tableau_migration import (
    MigrationManifest,
    MigrationManifestEditor,
    TableauCloudSiteConnectionConfiguration,
    TableauServerConnectionConfiguration
)
from tableau_migration.migration import PyMigrationPlanBuilder
import asyncio


async def basic_migration():
    """
    Simplest possible migration setup.
    Migrates everything from Server to Cloud with no customization.
    """

    # STEP 1: Create a migration plan builder
    plan_builder = PyMigrationPlanBuilder()

    # STEP 2: Configure SOURCE (where content comes from)
    plan_builder = plan_builder.from_source_tableau_server(
        server_url="https://tableau-server.company.com",
        site_content_url="marketing",  # Site name on Server
        access_token_name="my-server-token-name",
        access_token="my-server-token-secret"
    )

    # STEP 3: Configure DESTINATION (where content goes to)
    plan_builder = plan_builder.to_destination_tableau_cloud(
        pod_url="https://10ax.online.tableau.com",
        site_content_url="corporate",  # Different site name in Cloud!
        access_token_name="my-cloud-token-name",
        access_token="my-cloud-token-secret"
    )

    # STEP 4: Build the plan
    plan = plan_builder.build()

    # STEP 5: Execute the migration
    print("Starting migration...")
    result = await plan.execute_async()

    # STEP 6: Check results
    if result.status == "Completed":
        print("✅ Migration completed successfully!")
    else:
        print(f"❌ Migration failed: {result.status}")
        for error in result.errors:
            print(f"   Error: {error}")


if __name__ == "__main__":
    # Run the async migration
    asyncio.run(basic_migration())


"""
WHAT HAPPENS WHEN THIS RUNS:

1. SDK connects to source (Tableau Server)
2. SDK reads ALL content types:
   - Users
   - Groups
   - Projects
   - Data Sources
   - Workbooks
   - Extract Refresh Tasks
   - Subscriptions

3. SDK migrates everything to destination (Tableau Cloud)
4. Because we didn't add any mappings, it assumes names stay the same

PROBLEM: What if project names are different? What if emails changed?
That's where MAPPING comes in (see next example)

KEY PYTHON DIFFERENCES FROM C#:
- Uses async/await (same concept, cleaner syntax)
- No dependency injection needed (simpler!)
- from_source_tableau_server() instead of FromSourceTableauServer()
- snake_case instead of PascalCase
- Much less boilerplate code!
"""
