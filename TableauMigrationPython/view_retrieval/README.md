# View Retrieval

Scripts to retrieve views from Tableau Server using the [Tableau Server Client (TSC)](https://tableau.github.io/server-client-python/) library.

## Prerequisites

```bash
pip install tableauserverclient
```

## Configuration

These scripts read from the existing `config.json` in the parent `TableauMigrationPython/` directory.
Copy the template if you haven't already:

```bash
cp ../config.json.template ../config.json
# then edit ../config.json with your credentials
```

The `source` block is used:

```json
{
  "source": {
    "server_url": "https://your-tableau-server.com",
    "site_content_url": "",
    "access_token_name": "your-token-name",
    "access_token": "your-token-secret"
  }
}
```

## Scripts

### `view_retrieval.py`

Retrieves all views from your source Tableau Server.

```bash
# List all views
python view_retrieval.py

# Filter by project
python view_retrieval.py --project "Finance"

# Filter by workbook
python view_retrieval.py --workbook "Sales Dashboard"

# Export to CSV
python view_retrieval.py --output views.csv

# Use a different config file location
python view_retrieval.py --config /path/to/config.json
```

### Output

Prints a table of matching views to stdout:

```
Found 42 view(s):

Name                                     Project                   Content URL
------------------------------------------------------------------------------------------
Sales Overview                           Finance                   views/SalesDash/Overview
...
```

With `--output`, saves a CSV with columns:
`id, name, content_url, workbook_id, owner_id, project_name, created_at, updated_at`
