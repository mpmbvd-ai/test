"""
Configuration for Tableau Migration
Load credentials from a JSON configuration file.
"""

import json
from pathlib import Path
from tableau_migration.migration import PyMigrationPlanBuilder


def load_config(config_path='config.json'):
    """
    Load credentials from JSON file.

    1. Copy config.json.template to config.json
    2. Edit config.json with your credentials
    3. Add config.json to .gitignore (IMPORTANT!)
    """
    config_file = Path(config_path)

    if not config_file.exists():
        print(f"❌ Config file not found: {config_path}")
        print(f"\n1. Copy the template:")
        print(f"   cp config.json.template config.json")
        print(f"\n2. Edit config.json with your credentials")
        print(f"\n3. Make sure config.json is in .gitignore!")
        return None

    with open(config_file, 'r') as f:
        config = json.load(f)

    return config


def validate_config(config):
    """Check that config has all required fields."""
    if not config:
        return False

    required_source = ['server_url', 'site_content_url', 'access_token_name', 'access_token']
    required_dest = ['pod_url', 'site_content_url', 'access_token_name', 'access_token']

    missing = []

    for field in required_source:
        if field not in config.get('source', {}) or not config['source'][field]:
            missing.append(f"source.{field}")

    for field in required_dest:
        if field not in config.get('destination', {}) or not config['destination'][field]:
            missing.append(f"destination.{field}")

    if missing:
        print("❌ Missing or empty fields in config.json:")
        for m in missing:
            print(f"   - {m}")
        return False

    return True


async def example_with_json_config():
    """Run migration using JSON config file for credentials."""

    # Load config
    config = load_config('config.json')

    if not config or not validate_config(config):
        return

    print("✓ Config loaded successfully")

    # Build plan
    plan_builder = PyMigrationPlanBuilder()

    plan_builder = (
        plan_builder
        .from_source_tableau_server(**config['source'])
        .to_destination_tableau_cloud(**config['destination'])
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
    asyncio.run(example_with_json_config())
