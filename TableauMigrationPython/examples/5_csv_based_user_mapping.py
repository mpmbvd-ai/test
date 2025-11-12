"""
Example 5: CSV-Based User Mapping (Python)
===========================================

THE PRACTICAL APPROACH - Load user mappings from a CSV file

This is how you'll actually do migrations in real life:
1. Export users from Server to CSV
2. Add a column for Cloud email
3. Load CSV in your migration code
4. SDK uses the mappings automatically
"""

from tableau_migration import PyUser
from tableau_migration.migration import PyMigrationPlanBuilder
from tableau_migration.migration_engine_hooks_mappings import PyContentMappingContext
import asyncio
import csv
from pathlib import Path


class CsvUserMapping:
    """
    Load user mappings from a CSV file.

    CSV Format:
        ServerUsername,CloudEmail,Notes
        jsmith,john.smith@company.com,Sales Manager
        ajones,alice.jones@company.com,Marketing Director
    """

    def __init__(self, csv_file_path: str, default_domain: str = "@company.com"):
        """
        Initialize the mapping by loading from CSV.

        Args:
            csv_file_path: Path to CSV file with mappings
            default_domain: Default domain to append if user not in CSV
        """
        self.default_domain = default_domain
        self.mappings = self._load_csv(csv_file_path)

        print(f"📄 Loaded {len(self.mappings)} user mappings from CSV")

    def _load_csv(self, csv_path: str) -> dict:
        """Load mappings from CSV file into a dictionary."""
        mappings = {}

        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    server_username = row.get('ServerUsername', '').strip()
                    cloud_email = row.get('CloudEmail', '').strip()

                    # Skip empty rows
                    if not server_username or not cloud_email:
                        continue

                    # Add to mapping dictionary (case-insensitive)
                    mappings[server_username.lower()] = cloud_email

            print(f"✓ Successfully loaded {len(mappings)} mappings")

        except FileNotFoundError:
            print(f"❌ CSV file not found: {csv_path}")
            print(f"   Create a CSV with columns: ServerUsername,CloudEmail,Notes")
            raise

        except Exception as ex:
            print(f"❌ Error loading CSV: {ex}")
            raise

        return mappings

    def map(self, ctx: PyContentMappingContext[PyUser]) -> PyContentMappingContext[PyUser]:
        """Map user from Server username to Cloud email."""
        user = ctx.content_item
        username = user.name

        # Skip if already an email
        if "@" in username:
            print(f"👤 {username} - already an email")
            return ctx

        # Check CSV mappings first (case-insensitive)
        username_lower = username.lower()
        if username_lower in self.mappings:
            email = self.mappings[username_lower]
            print(f"👤 {username} → {email} (from CSV)")
            return ctx.map_to(user.location.with_username(email))

        # Fallback: append default domain
        default_email = f"{username}{self.default_domain}"
        print(f"👤 {username} → {default_email} (default)")
        return ctx.map_to(user.location.with_username(default_email))


async def migration_with_csv_mapping():
    """Run migration using CSV file for user mappings."""

    print("=================================================")
    print("  CSV-BASED USER MAPPING MIGRATION")
    print("=================================================\n")

    # Path to your CSV file
    csv_path = "user_mappings.csv"

    # Validate CSV exists
    if not Path(csv_path).exists():
        print(f"❌ CSV file not found: {csv_path}")
        print(f"   Create a CSV with columns: ServerUsername,CloudEmail,Notes")
        print(f"\n   Example:")
        print(f"   ServerUsername,CloudEmail,Notes")
        print(f"   jsmith,john.smith@company.com,Sales Manager")
        print(f"   ajones,alice.jones@company.com,Marketing Director")
        return

    print("Building migration plan...\n")

    plan_builder = PyMigrationPlanBuilder()

    plan_builder = (
        plan_builder
        .from_source_tableau_server(
            server_url="https://tableau-server.company.com",
            site_content_url="default",
            access_token_name="server-token",
            access_token="server-secret"
        )
        .to_destination_tableau_cloud(
            pod_url="https://10ax.online.tableau.com",
            site_content_url="production",
            access_token_name="cloud-token",
            access_token="cloud-secret"
        )
    )

    # ⭐ Register CSV-based mapping
    csv_mapping = CsvUserMapping(csv_path, default_domain="@company.com")
    plan_builder.mappings.add(csv_mapping)

    plan = plan_builder.build()

    print("\nStarting migration...\n")
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


def create_sample_csv():
    """Helper function to create a sample CSV template."""
    sample_csv = """ServerUsername,CloudEmail,Notes
jsmith,john.smith@company.com,Sales Manager - abbreviated username
ajones,alice.jones@company.com,Marketing Director - abbreviated username
bob.wilson,bob.wilson@company.com,Finance - already full name
admin,admin.tableau@company.com,Admin account - special email
service_account,svc.tableau@company.com,Service account for scheduled extracts
"""

    with open('user_mappings_template.csv', 'w') as f:
        f.write(sample_csv)

    print("✓ Created user_mappings_template.csv")
    print("  Edit this file and save as user_mappings.csv")


if __name__ == "__main__":
    # Uncomment to create a sample CSV:
    # create_sample_csv()

    # Run the migration
    asyncio.run(migration_with_csv_mapping())


"""
YOUR WORKFLOW:

STEP 1: Export users from Server to CSV
----------------------------------------
Export from Tableau Server admin UI or use SQL to get user list.

You'll get something like:
ServerUsername
jsmith
ajones
bob.wilson
admin

STEP 2: Add CloudEmail column in Excel/Google Sheets
----------------------------------------------------
Open in Excel, add CloudEmail column:

ServerUsername | CloudEmail                  | Notes
---------------|-----------------------------|-----------------
jsmith         | john.smith@company.com      | Abbreviated
ajones         | alice.jones@company.com     | Abbreviated
bob.wilson     | bob.wilson@company.com      | Standard
admin          | admin.tableau@company.com   | Special

You can use Excel formula: =A2&"@company.com" for most users,
then manually fix the abbreviated ones.

STEP 3: Save as user_mappings.csv
----------------------------------
Save your edited file as user_mappings.csv

STEP 4: Run migration
----------------------
csv_mapping = CsvUserMapping("user_mappings.csv")
plan_builder.mappings.add(csv_mapping)

STEP 5: SDK does everything!
-----------------------------
✅ Loads CSV
✅ Maps all users
✅ Updates all subscriptions automatically
✅ Done!

ADVANTAGES OF CSV APPROACH:

✅ Easy to review - open in Excel
✅ Easy to edit - no code changes needed
✅ Team collaboration - share CSV for review
✅ Reusable - save for future migrations
✅ Auditable - track what was mapped
✅ Version control - commit CSV to git

PYTHON ADVANTAGES OVER C#:

✅ Built-in csv module - no extra libraries needed
✅ Simpler code - just read CSV into dict
✅ No dependency injection complexity
✅ More readable and maintainable

CSV FORMAT REQUIREMENTS:

Required columns:
- ServerUsername: Username from Tableau Server
- CloudEmail: Email address for Tableau Cloud

Optional columns:
- Notes: Any comments for your tracking

HANDLING ERRORS:

If a user in Server isn't in the CSV:
- Falls back to appending default domain
- Example: "newuser" → "newuser@company.com"

If CloudEmail is invalid:
- Migration will fail for that user
- Check logs to see which user
- Fix CSV and re-run

TESTING:

1. Create small test CSV with 5-10 users
2. Run migration to test Cloud site
3. Verify users created correctly
4. Check subscriptions work
5. Then use full CSV for production
"""
