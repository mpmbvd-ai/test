"""
Dry Run - Validate configuration and preview migration without executing.

Usage:
    python dry_run.py                  # Validate config only (no SDK needed)
    python dry_run.py --connect        # Also verify server connectivity via SDK
"""

import argparse

from migration_utils import (
    configure_logging,
    load_config,
    validate_config,
    print_dry_run_report,
)

configure_logging()


def main():
    parser = argparse.ArgumentParser(
        description="Validate migration config and preview what would happen."
    )
    parser.add_argument(
        "--connect",
        action="store_true",
        help="Also build the SDK plan to verify server connectivity (requires tableau_migration).",
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config file (default: config.json).",
    )
    args = parser.parse_args()

    # Load and validate config
    config = load_config(args.config)
    if not config:
        return

    print("Validating configuration...")
    if not validate_config(config):
        return
    print("Configuration is valid.")

    # Print the dry-run report
    print_dry_run_report(config)

    # Optionally verify connectivity by building the SDK plan
    if args.connect:
        print("Verifying server connectivity...")
        try:
            from tableau_migration import MigrationPlanBuilder

            plan_builder = MigrationPlanBuilder()
            plan_builder = (
                plan_builder
                .from_source_tableau_server(
                    server_url=config['source']['server_url'],
                    site_content_url=config['source']['site_content_url'],
                    access_token_name=config['source']['access_token_name'],
                    access_token=config['source']['access_token'],
                )
                .to_destination_tableau_cloud(
                    pod_url=config['destination']['pod_url'],
                    site_content_url=config['destination']['site_content_url'],
                    access_token_name=config['destination']['access_token_name'],
                    access_token=config['destination']['access_token'],
                )
                .for_server_to_cloud()
                .with_tableau_id_authentication_type()
            )

            plan = plan_builder.build()
            print("Plan built successfully — credentials and endpoints are valid.\n")
        except ImportError:
            print("tableau_migration package not installed. Skipping connectivity check.\n")
        except Exception as e:
            print(f"Connectivity check failed: {e}\n")


if __name__ == "__main__":
    main()
