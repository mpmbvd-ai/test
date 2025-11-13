"""
Simple Subscription Migration - Single File
Based on actual Tableau Migration SDK Python example.
"""

import asyncio
from tableau_migration import (
    Migrator,
    MigrationPlanBuilder
)


# =============================================================================
# CONFIGURATION - EDIT THESE
# =============================================================================

# SOURCE: Tableau Server
SOURCE_SERVER_URL = "https://your-tableau-server.com"
SOURCE_SITE = ""  # Empty string for default site, or "site-name"
SOURCE_TOKEN_NAME = "your-token-name"
SOURCE_TOKEN = "your-token-secret"

# DESTINATION: Tableau Cloud
DEST_CLOUD_URL = "https://10ax.online.tableau.com"  # Change pod: 10ax, 10ay, etc.
DEST_SITE = "your-cloud-site"
DEST_TOKEN_NAME = "your-cloud-token-name"
DEST_TOKEN = "your-cloud-token-secret"

# USER MAPPINGS - Server username → Cloud email
USER_MAPPINGS = {
    "jsmith": "john.smith@company.com",
    "ajones": "alice.jones@company.com",
    # Add more users here...
}

# Default email domain
EMAIL_DOMAIN = "@company.com"


# =============================================================================
# USERNAME MAPPING CLASS
# =============================================================================

class SimpleUsernameMapping:
    """Maps Server usernames to Cloud emails."""

    def __call__(self, username: str) -> str:
        """
        Called for each username during migration.

        Args:
            username: The Server username

        Returns:
            The Cloud email address
        """
        # Already an email? Return as-is
        if "@" in username:
            return username

        # Check mapping dict
        if username in USER_MAPPINGS:
            email = USER_MAPPINGS[username]
            print(f"👤 Mapping: {username} → {email}")
            return email

        # Default: append domain
        email = f"{username}{EMAIL_DOMAIN}"
        print(f"👤 Default: {username} → {email}")
        return email


# =============================================================================
# MIGRATION
# =============================================================================

def migrate_subscriptions():
    """Migrate subscriptions from Server to Cloud."""

    print("Starting subscription migration...")
    print(f"Source: {SOURCE_SERVER_URL} / {SOURCE_SITE if SOURCE_SITE else 'Default'}")
    print(f"Destination: {DEST_CLOUD_URL} / {DEST_SITE}\n")

    # Create migrator
    migration = Migrator()

    # Build plan
    plan_builder = MigrationPlanBuilder()

    plan_builder = (
        plan_builder
        .from_source_tableau_server(
            server_url=SOURCE_SERVER_URL,
            site_content_url=SOURCE_SITE,
            access_token_name=SOURCE_TOKEN_NAME,
            access_token=SOURCE_TOKEN
        )
        .to_destination_tableau_cloud(
            pod_url=DEST_CLOUD_URL,
            site_content_url=DEST_SITE,
            access_token_name=DEST_TOKEN_NAME,
            access_token=DEST_TOKEN
        )
        .for_server_to_cloud()
        .with_tableau_id_authentication_type()
        .with_tableau_cloud_usernames(SimpleUsernameMapping)  # Pass class, not instance
    )

    # Build and execute
    print("Building migration plan...")
    plan = plan_builder.build()

    print("Starting migration (this may take a while)...\n")
    result = migration.execute(plan)

    # Results
    print("\n" + "="*50)
    if result.status.name == "Completed":
        print("✅ Migration completed!")
        print(f"   Check your Cloud site for migrated content")
    else:
        print(f"❌ Migration failed: {result.status}")
        if hasattr(result, 'errors') and result.errors:
            for error in result.errors:
                print(f"   {error}")
    print("="*50)


if __name__ == "__main__":
    migrate_subscriptions()
