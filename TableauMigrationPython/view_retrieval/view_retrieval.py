"""
View Retrieval using Tableau Server Client (TSC)

Connects to the source Tableau Server defined in config.json
and retrieves all views, optionally filtering by workbook or project.

Usage:
    python view_retrieval.py
    python view_retrieval.py --project "My Project"
    python view_retrieval.py --workbook "My Workbook"
    python view_retrieval.py --output views.csv

Requires:
    pip install tableauserverclient

Config:
    Uses the 'source' block from config.json in the parent directory.
"""

import json
import csv
import argparse
from pathlib import Path

import tableauserverclient as TSC


def load_config(config_path: str = '../config.json') -> dict:
    """
    Load source credentials from config.json.

    Expected format (source block):
        {
          "source": {
            "server_url": "https://your-tableau-server.com",
            "site_content_url": "",
            "access_token_name": "your-token-name",
            "access_token": "your-token-secret"
          }
        }
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_file.resolve()}\n"
            "Copy config.json.template to config.json and fill in your credentials."
        )

    with open(config_file, 'r') as f:
        config = json.load(f)

    if 'source' not in config:
        raise KeyError("'source' block missing from config.json")

    return config['source']


def connect(source: dict) -> TSC.Server:
    """Sign in to Tableau Server and return an authenticated Server object."""
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=source['access_token_name'],
        personal_access_token=source['access_token'],
        site_id=source.get('site_content_url', ''),
    )

    server = TSC.Server(source['server_url'], use_server_version=True)
    server.auth.sign_in(tableau_auth)
    return server


def get_all_views(
    server: TSC.Server,
    project_name: str = None,
    workbook_name: str = None,
) -> list[dict]:
    """
    Retrieve views from the server, with optional filters.

    Args:
        server:        Authenticated TSC Server object.
        project_name:  If set, only return views in this project.
        workbook_name: If set, only return views in this workbook.

    Returns:
        List of dicts with view metadata.
    """
    req_options = TSC.RequestOptions(pagesize=1000)
    all_views, _ = server.views.get(req_options)

    results = []
    for view in all_views:
        # Populate owner/workbook details
        if view.owner_id:
            try:
                server.views.populate_image(view)
            except Exception:
                pass

        row = {
            'id': view.id,
            'name': view.name,
            'content_url': view.content_url,
            'workbook_id': view.workbook_id,
            'owner_id': view.owner_id,
            'project_name': view.project_name if hasattr(view, 'project_name') else '',
            'created_at': str(view.created_at) if view.created_at else '',
            'updated_at': str(view.updated_at) if view.updated_at else '',
        }

        if project_name and row['project_name'] != project_name:
            continue

        results.append(row)

    # Workbook filter: fetch workbooks and cross-reference
    if workbook_name:
        wb_options = TSC.RequestOptions(pagesize=1000)
        all_workbooks, _ = server.workbooks.get(wb_options)
        matching_wb_ids = {
            wb.id for wb in all_workbooks if wb.name == workbook_name
        }
        results = [r for r in results if r['workbook_id'] in matching_wb_ids]

    return results


def print_views(views: list[dict]) -> None:
    """Pretty-print view summary to stdout."""
    if not views:
        print("No views found.")
        return

    print(f"\nFound {len(views)} view(s):\n")
    print(f"{'Name':<40} {'Project':<25} {'Content URL'}")
    print("-" * 90)
    for v in views:
        print(f"{v['name']:<40} {v['project_name']:<25} {v['content_url']}")


def save_to_csv(views: list[dict], output_path: str) -> None:
    """Write views to a CSV file."""
    if not views:
        print("Nothing to write.")
        return

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=views[0].keys())
        writer.writeheader()
        writer.writerows(views)

    print(f"Saved {len(views)} view(s) to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Retrieve views from Tableau Server')
    parser.add_argument('--config', default='../config.json', help='Path to config.json')
    parser.add_argument('--project', default=None, help='Filter by project name')
    parser.add_argument('--workbook', default=None, help='Filter by workbook name')
    parser.add_argument('--output', default=None, help='Save results to CSV file')
    args = parser.parse_args()

    source = load_config(args.config)
    print(f"Connecting to {source['server_url']} ...")

    server = connect(source)
    try:
        views = get_all_views(
            server,
            project_name=args.project,
            workbook_name=args.workbook,
        )
        print_views(views)

        if args.output:
            save_to_csv(views, args.output)
    finally:
        server.auth.sign_out()
        print("\nSigned out.")


if __name__ == '__main__':
    main()
