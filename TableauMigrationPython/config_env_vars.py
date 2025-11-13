"""
Configuration for Tableau Migration
Store your credentials securely using environment variables.
"""

import os
from tableau_migration.migration import PyMigrationPlanBuilder


def get_credentials():
    """
    Load credentials from environment variables.

    Set these environment variables before running:
    export TABLEAU_SERVER_URL="https://tableau-server.company.com"
    export TABLEAU_SERVER_SITE="marketing"
    export TABLEAU_SERVER_TOKEN_NAME="your-token-name"
    export TABLEAU_SERVER_TOKEN="your-token-secret"

    export TABLEAU_CLOUD_URL="https://10ax.online.tableau.com"
    export TABLEAU_CLOUD_SITE="production"
    export TABLEAU_CLOUD_TOKEN_NAME="your-token-name"
    export TABLEAU_CLOUD_TOKEN="your-token-secret"
    """
    return {
        'source': {
            'server_url': os.environ.get('TABLEAU_SERVER_URL'),
            'site_content_url': os.environ.get('TABLEAU_SERVER_SITE'),
            'access_token_name': os.environ.get('TABLEAU_SERVER_TOKEN_NAME'),
            'access_token': os.environ.get('TABLEAU_SERVER_TOKEN')
        },
        'destination': {
            'pod_url': os.environ.get('TABLEAU_CLOUD_URL'),
            'site_content_url': os.environ.get('TABLEAU_CLOUD_SITE'),
            'access_token_name': os.environ.get('TABLEAU_CLOUD_TOKEN_NAME'),
            'access_token': os.environ.get('TABLEAU_CLOUD_TOKEN')
        }
    }


def validate_credentials(creds):
    """Check that all required credentials are present."""
    missing = []

    for system, values in creds.items():
        for key, value in values.items():
            if not value:
                missing.append(f"{system}.{key}")

    if missing:
        print("❌ Missing credentials:")
        for m in missing:
            print(f"   - {m}")
        return False

    return True


async def example_with_env_vars():
    """Run migration using environment variables for credentials."""

    # Load credentials
    creds = get_credentials()

    # Validate
    if not validate_credentials(creds):
        print("\nSet environment variables first:")
        print("  export TABLEAU_SERVER_URL='...'")
        print("  export TABLEAU_SERVER_SITE='...'")
        print("  # etc.")
        return

    # Build plan
    plan_builder = PyMigrationPlanBuilder()

    plan_builder = (
        plan_builder
        .from_source_tableau_server(**creds['source'])
        .to_destination_tableau_cloud(**creds['destination'])
    )

    # Add your mappings here
    # plan_builder.mappings.add(...)

    plan = plan_builder.build()
    result = await plan.execute_async()

    if result.status == "Completed":
        print("✅ Migration completed!")
    else:
        print(f"❌ Migration failed: {result.status}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_with_env_vars())
