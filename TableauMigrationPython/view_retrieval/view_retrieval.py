"""
View Retrieval using Tableau Server Client (TSC)

Retrieves all views from a specific workbook and downloads them as PNGs.

Usage:
    python view_retrieval.py
    python view_retrieval.py --output views.csv

Requires:
    pip install tableauserverclient
"""

import csv
import argparse
from pathlib import Path

import tableauserverclient as TSC


# -- Credentials ---------------------------------------------------------------
SERVER_URL = "https://your-tableau-server.com"
SITE_CONTENT_URL = ""                # leave empty string for Default site
ACCESS_TOKEN_NAME = "your-token-name"
ACCESS_TOKEN = "your-token-secret"
# -- Target workbook -----------------------------------------------------------
WORKBOOK_NAME = "Your Workbook Name"  # exact name as it appears in Tableau
# -- Output --------------------------------------------------------------------
IMAGE_OUTPUT_DIR = r"C:\path\to\your\output\images"
# ------------------------------------------------------------------------------


def connect() -> TSC.Server:
    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=ACCESS_TOKEN_NAME,
        personal_access_token=ACCESS_TOKEN,
        site_id=SITE_CONTENT_URL,
    )
    server = TSC.Server(SERVER_URL, use_server_version=True)
    server.auth.sign_in(tableau_auth)
    return server


def get_workbook(server: TSC.Server) -> TSC.WorkbookItem:
    """Find the target workbook by name. Raises if not found."""
    req = TSC.RequestOptions(pagesize=1000)
    req.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                              TSC.RequestOptions.Operator.Equals,
                              WORKBOOK_NAME))
    workbooks, _ = server.workbooks.get(req)

    if not workbooks:
        raise ValueError(f"Workbook '{WORKBOOK_NAME}' not found on {SERVER_URL}")

    return workbooks[0]


def get_views(server: TSC.Server, workbook: TSC.WorkbookItem) -> list:
    """Get all views belonging to the workbook."""
    server.workbooks.populate_views(workbook)
    return workbook.views


def download_images(server: TSC.Server, views: list) -> None:
    """Download a high-res PNG for each view and save to IMAGE_OUTPUT_DIR."""
    out = Path(IMAGE_OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    image_req = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High)

    for view in views:
        try:
            server.views.populate_image(view, image_req)
            safe_name = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in view.name).strip()
            file_path = out / f"{safe_name}.png"
            file_path.write_bytes(view.image)
            print(f"  Saved: {file_path}")
        except Exception as e:
            print(f"  Failed to download image for '{view.name}': {e}")


def save_to_csv(views: list, output_path: str) -> None:
    rows = [
        {
            'id': v.id,
            'name': v.name,
            'content_url': v.content_url,
            'owner_id': v.owner_id,
        }
        for v in views
    ]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} view(s) to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Retrieve views from a Tableau workbook')
    parser.add_argument('--output', default=None, help='Save view metadata to CSV file')
    args = parser.parse_args()

    print(f"Connecting to {SERVER_URL} ...")
    server = connect()
    try:
        print(f"Looking for workbook '{WORKBOOK_NAME}' ...")
        workbook = get_workbook(server)
        print(f"Found workbook: {workbook.name} (id: {workbook.id})")

        views = get_views(server, workbook)
        print(f"Found {len(views)} view(s): {[v.name for v in views]}")

        print(f"\nDownloading images to '{IMAGE_OUTPUT_DIR}' ...")
        download_images(server, views)

        if args.output:
            save_to_csv(views, args.output)
    finally:
        server.auth.sign_out()
        print("\nSigned out.")


if __name__ == '__main__':
    main()
