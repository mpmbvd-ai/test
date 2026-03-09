"""
List Workbooks and View Visibility
Connects to Tableau Server and lists all workbooks with their views and hidden status.
Does NOT perform migration - just exploration.
"""

import json
import logging
from pathlib import Path
import tableauserverclient as TSC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Suppress TSC debug logs
logging.getLogger('tableauserverclient').setLevel(logging.WARNING)


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


def list_workbook_views():
    """List all workbooks on the server with their views and hidden status."""

    # Load configuration
    config = load_config()
    if not config:
        return

    source = config.get('source', {})
    server_url = source.get('server_url', '')
    site_id = source.get('site_content_url', '')
    token_name = source.get('access_token_name', '')
    token_value = source.get('access_token', '')

    if not all([server_url, token_name, token_value]):
        print("❌ Missing source server configuration in config.json")
        return

    print("="*80)
    print("📊 WORKBOOK VIEW ANALYSIS")
    print("="*80)
    print(f"Server: {server_url}")
    print(f"Site: {site_id if site_id else 'Default'}")
    print("="*80)
    print()

    try:
        # Create authentication
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=token_name,
            personal_access_token=token_value,
            site_id=site_id
        )

        # Connect to server
        server = TSC.Server(server_url, use_server_version=True)

        with server.auth.sign_in(tableau_auth):
            print("✅ Connected to Tableau Server\n")
            print("Fetching workbooks...\n")

            # Get all workbooks
            all_workbooks = list(TSC.Pager(server.workbooks))

            if not all_workbooks:
                print("No workbooks found on the server.")
                return

            print(f"Found {len(all_workbooks)} workbook(s)\n")
            print("="*80)

            # Track overall statistics
            total_views = 0
            total_hidden = 0
            total_visible = 0

            # Process each workbook
            for idx, workbook in enumerate(all_workbooks, 1):
                # Populate the workbook with views
                server.workbooks.populate_views(workbook)

                views = workbook.views if workbook.views else []
                view_count = len(views)
                total_views += view_count

                # Count hidden vs visible views
                hidden_views = [v for v in views if v.hidden]
                visible_views = [v for v in views if not v.hidden]

                hidden_count = len(hidden_views)
                visible_count = len(visible_views)

                total_hidden += hidden_count
                total_visible += visible_count

                # Print workbook header
                print(f"\n[{idx}] 📊 Workbook: {workbook.name}")
                print(f"    Project: {workbook.project_name}")
                print(f"    Owner: {workbook.owner_id}")
                print(f"    Total Views: {view_count} ({visible_count} visible, {hidden_count} hidden)")

                if not views:
                    print("    ⚠️  No views in this workbook")
                    continue

                # Print visible views
                if visible_views:
                    print(f"\n    ✅ VISIBLE VIEWS ({visible_count}):")
                    for view in visible_views:
                        print(f"       • {view.name}")

                # Print hidden views
                if hidden_views:
                    print(f"\n    🔒 HIDDEN VIEWS ({hidden_count}):")
                    for view in hidden_views:
                        print(f"       • {view.name}")

                print("    " + "-"*76)

            # Print summary
            print("\n" + "="*80)
            print("📊 SUMMARY")
            print("="*80)
            print(f"Total Workbooks: {len(all_workbooks)}")
            print(f"Total Views: {total_views}")
            print(f"  ✅ Visible Views: {total_visible} ({total_visible/total_views*100:.1f}%)" if total_views > 0 else "  ✅ Visible Views: 0")
            print(f"  🔒 Hidden Views: {total_hidden} ({total_hidden/total_views*100:.1f}%)" if total_views > 0 else "  🔒 Hidden Views: 0")
            print("="*80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    list_workbook_views()
