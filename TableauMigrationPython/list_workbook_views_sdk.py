"""
List Workbooks and View Visibility using Migration SDK
Uses the Tableau Migration SDK to read workbooks (including hidden views) without migrating.
The SDK downloads workbooks to analyze them, but filters prevent actual migration.
"""

import json
import logging
from pathlib import Path
from tableau_migration import (
    Migrator,
    MigrationPlanBuilder,
    ContentFilterBase,
    ContentTransformerBase,
    IPublishableWorkbook,
    IDataSource,
    IUser,
    IProject,
    IGroup
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Silence noisy SDK loggers
logging.getLogger('System.Net.Http.HttpClient.DefaultHttpClient.LogicalHandler').setLevel(logging.CRITICAL)
logging.getLogger('System.Net.Http.HttpClient.DefaultHttpClient.ClientHandler').setLevel(logging.CRITICAL)
logging.getLogger('Tableau.Migration.Net.Logging.HttpActivityLogger').setLevel(logging.CRITICAL)
logging.getLogger('Tableau.Migration.Engine.Conversion.Schedules.ServerToCloudScheduleConverter').setLevel(logging.CRITICAL)
logging.getLogger('Tableau.Migration.Engine.Hooks.Transformers').setLevel(logging.CRITICAL)
logging.getLogger('Polly').setLevel(logging.CRITICAL)
logging.getLogger('System.Net.Http.HttpClient').setLevel(logging.CRITICAL)
logging.getLogger('tableauserverclient').setLevel(logging.CRITICAL)
logging.getLogger('Tableau.Migration.Engine').setLevel(logging.WARNING)


# =============================================================================
# CONFIGURATION
# =============================================================================

def load_config(config_path='config.json'):
    """Load credentials from config.json file."""
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"❌ Config file not found: {config_path}")
        print(f"\n📋 Setup instructions:")
        print(f"   1. Copy the template: cp config.json.template config.json")
        print(f"   2. Edit config.json with your actual credentials")
        print(f"   3. Run this script again\n")
        return None

    with open(config_file, 'r') as f:
        return json.load(f)


# =============================================================================
# FILTERS - Skip everything (analysis only, no migration)
# =============================================================================

class SkipAllWorkbooks(ContentFilterBase[IPublishableWorkbook]):
    """Skip migrating workbooks - we only want to analyze them."""
    def should_migrate(self, item):
        return False

class SkipAllDataSources(ContentFilterBase[IDataSource]):
    """Skip migrating data sources."""
    def should_migrate(self, item):
        return False

class SkipAllUsers(ContentFilterBase[IUser]):
    """Skip migrating users."""
    def should_migrate(self, item):
        return False

class SkipAllGroups(ContentFilterBase[IGroup]):
    """Skip migrating groups."""
    def should_migrate(self, item):
        return False

class SkipAllProjects(ContentFilterBase[IProject]):
    """Skip migrating projects."""
    def should_migrate(self, item):
        return False


# =============================================================================
# TRANSFORMER - Analyze workbook views and hidden status
# =============================================================================

class WorkbookViewAnalyzer(ContentTransformerBase[IPublishableWorkbook]):
    """
    Analyzes workbook views and logs hidden vs visible views.
    The SDK downloads the workbook, giving us access to full view information.
    """

    def __init__(self):
        super().__init__()
        self.workbooks_analyzed = []
        self.total_views = 0
        self.total_hidden = 0
        self.total_visible = 0

    def transform(self, item: IPublishableWorkbook) -> IPublishableWorkbook:
        """Process each workbook and log its view information."""

        # Get all views and hidden view names
        all_views = list(item.views) if item.views else []
        hidden_names = set(item.hidden_view_names) if item.hidden_view_names else set()

        # Categorize views
        visible_views = []
        hidden_views = []

        for view in all_views:
            if view.name in hidden_names:
                hidden_views.append(view.name)
            else:
                visible_views.append(view.name)

        # Update statistics
        self.total_views += len(all_views)
        self.total_visible += len(visible_views)
        self.total_hidden += len(hidden_views)

        # Store workbook information
        workbook_info = {
            'name': item.name,
            'project': item.location.parent().name if item.location and item.location.parent() else 'Unknown',
            'owner': item.owner.name if item.owner else 'Unknown',
            'total_views': len(all_views),
            'visible_views': visible_views,
            'hidden_views': hidden_views
        }
        self.workbooks_analyzed.append(workbook_info)

        # Log the information
        print(f"\n📊 Workbook: {item.name}")
        print(f"   Project: {workbook_info['project']}")
        print(f"   Owner: {workbook_info['owner']}")
        print(f"   Total Views: {len(all_views)} ({len(visible_views)} visible, {len(hidden_views)} hidden)")

        if visible_views:
            print(f"\n   ✅ VISIBLE VIEWS ({len(visible_views)}):")
            for view_name in visible_views:
                print(f"      • {view_name}")

        if hidden_views:
            print(f"\n   🔒 HIDDEN VIEWS ({len(hidden_views)}):")
            for view_name in hidden_views:
                print(f"      • {view_name}")

        print("   " + "-"*76)

        # Return the item unchanged (though it won't be migrated due to filter)
        return item

    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"Total Workbooks Analyzed: {len(self.workbooks_analyzed)}")
        print(f"Total Views: {self.total_views}")
        if self.total_views > 0:
            print(f"  ✅ Visible Views: {self.total_visible} ({self.total_visible/self.total_views*100:.1f}%)")
            print(f"  🔒 Hidden Views: {self.total_hidden} ({self.total_hidden/self.total_views*100:.1f}%)")
        else:
            print(f"  ✅ Visible Views: 0")
            print(f"  🔒 Hidden Views: 0")
        print("="*80)


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_workbook_views():
    """
    Analyze workbooks using the Migration SDK without actually migrating.
    The SDK downloads and processes workbooks, giving us access to view details.
    """

    # Load configuration
    config = load_config()
    if not config:
        return

    source = config.get('source', {})
    # For analysis-only, we need a destination config but won't use it
    # Use a dummy Cloud URL if destination is not configured
    destination = config.get('destination', {})
    if not destination or not destination.get('pod_url'):
        print("⚠️  Note: Destination not configured in config.json")
        print("   Using dummy destination (required by SDK, but no migration will occur)\n")
        destination = {
            'pod_url': 'https://prod-useast-b.online.tableau.com',
            'site_content_url': 'dummy-site',
            'access_token_name': 'dummy',
            'access_token': 'dummy'
        }

    print("="*80)
    print("📊 WORKBOOK VIEW ANALYSIS (Using Migration SDK)")
    print("="*80)
    print(f"Source: {source.get('server_url', '')} / {source.get('site_content_url', 'Default')}")
    print("Mode: Analysis only - NO MIGRATION WILL OCCUR")
    print("="*80)
    print()

    # Create migrator and plan
    migration = Migrator()
    plan_builder = MigrationPlanBuilder()

    # Create analyzer transformer
    analyzer = WorkbookViewAnalyzer()

    # Configure plan
    plan_builder = (
        plan_builder
        .from_source_tableau_server(
            server_url=source['server_url'],
            site_content_url=source.get('site_content_url', ''),
            access_token_name=source['access_token_name'],
            access_token=source['access_token']
        )
        .to_destination_tableau_cloud(
            pod_url=destination['pod_url'],
            site_content_url=destination['site_content_url'],
            access_token_name=destination['access_token_name'],
            access_token=destination['access_token']
        )
        .for_server_to_cloud()
    )

    # Add filters to skip ALL migration (analysis only)
    print("⚙️  Configuring analysis mode (all migration disabled)...")
    plan_builder.filters.add(SkipAllUsers)
    plan_builder.filters.add(SkipAllGroups)
    plan_builder.filters.add(SkipAllProjects)
    plan_builder.filters.add(SkipAllDataSources)
    plan_builder.filters.add(SkipAllWorkbooks)  # Skip actual migration

    # Add transformer to analyze workbooks
    plan_builder.transformers.add(lambda: analyzer)

    # Build and execute
    print("🔍 Building analysis plan...")
    plan = plan_builder.build()

    print("\n📥 Downloading and analyzing workbooks from source...")
    print("   (Workbooks will be downloaded but NOT migrated)\n")

    result = migration.execute(plan)

    # Print summary
    analyzer.print_summary()

    # Print result status
    print(f"\n✅ Analysis complete - Status: {result.status.name}")
    if result.status.name != "Completed":
        print(f"⚠️  Note: Status is {result.status.name}, but this is normal for analysis-only mode")


if __name__ == "__main__":
    analyze_workbook_views()
