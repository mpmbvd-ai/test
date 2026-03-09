"""
Quick Workbook List - Using TSC for Complete Pagination
Lists ALL workbooks with view counts using tableauserverclient (which handles pagination correctly).
"""

import json
import logging
from pathlib import Path
import tableauserverclient as TSC

# Suppress TSC debug logs
logging.basicConfig(level=logging.WARNING)


def load_config(config_path='config.json'):
    """Load credentials from config.json file."""
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"❌ Config file not found: {config_path}")
        return None

    with open(config_file, 'r') as f:
        return json.load(f)


def list_all_workbooks():
    """List ALL workbooks using TSC with proper pagination."""

    config = load_config()
    if not config:
        return

    source = config.get('source', {})

    print("="*80)
    print("📊 COMPLETE WORKBOOK LIST (Using TSC with Pagination)")
    print("="*80)
    print(f"Server: {source['server_url']}")
    print(f"Site: {source.get('site_content_url', 'Default')}")
    print("="*80)
    print()

    try:
        # Create authentication
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=source['access_token_name'],
            personal_access_token=source['access_token'],
            site_id=source.get('site_content_url', '')
        )

        # Connect to server
        server = TSC.Server(source['server_url'], use_server_version=True)

        with server.auth.sign_in(tableau_auth):
            print("✅ Connected to server")
            print("📥 Fetching ALL workbooks (with pagination)...\n")

            # TSC.Pager automatically handles pagination
            all_workbooks = list(TSC.Pager(server.workbooks))

            print(f"📊 Found {len(all_workbooks)} total workbooks\n")
            print("="*80)

            # List each workbook with basic info
            for idx, workbook in enumerate(all_workbooks, 1):
                # Get size if available
                size_str = f"({workbook.size / (1024*1024):.1f} MB)" if workbook.size else "(size unknown)"

                print(f"[{idx}] {workbook.name}")
                print(f"    Project: {workbook.project_name}")
                print(f"    Owner: {workbook.owner_id}")
                print(f"    Size: {size_str}")

                # Get view count (without downloading)
                if hasattr(workbook, 'views') and workbook.views:
                    print(f"    Views: {len(workbook.views)}")

                print()

            print("="*80)
            print(f"✅ Total: {len(all_workbooks)} workbooks")
            print("="*80)

            # Show size distribution
            workbooks_with_size = [wb for wb in all_workbooks if wb.size]
            if workbooks_with_size:
                sizes_mb = [wb.size / (1024*1024) for wb in workbooks_with_size]
                print(f"\n📊 Size Statistics:")
                print(f"   Smallest: {min(sizes_mb):.1f} MB")
                print(f"   Largest: {max(sizes_mb):.1f} MB")
                print(f"   Average: {sum(sizes_mb)/len(sizes_mb):.1f} MB")
                print(f"   Over 50MB: {len([s for s in sizes_mb if s > 50])}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    list_all_workbooks()
