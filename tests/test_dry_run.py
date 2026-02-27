"""Tests for dry-run report and email mapping preview."""

import pytest

from migration_utils import (
    preview_email_mapping,
    print_dry_run_report,
    SAMPLE_USERNAMES,
)


class TestPreviewEmailMapping:
    """Tests for the preview_email_mapping helper."""

    def test_plain_username_gets_domain(self):
        assert preview_email_mapping("jsmith", "@test.com") == "jsmith@test.com"

    def test_email_passes_through(self):
        assert preview_email_mapping("bob@existing.com", "@test.com") == "bob@existing.com"

    def test_domain_without_at_sign(self):
        assert preview_email_mapping("alice", "example.com") == "alice@example.com"

    def test_domain_with_at_sign(self):
        assert preview_email_mapping("alice", "@example.com") == "alice@example.com"

    def test_empty_username(self):
        assert preview_email_mapping("", "@test.com") == "@test.com"


class TestSampleUsernames:
    """Verify sample usernames cover key edge cases."""

    def test_samples_include_plain_username(self):
        assert any("@" not in u for u in SAMPLE_USERNAMES)

    def test_samples_include_email(self):
        assert any("@" in u for u in SAMPLE_USERNAMES)


class TestPrintDryRunReport:
    """Tests for print_dry_run_report output."""

    def test_report_prints_without_error(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert "DRY-RUN REPORT" in output
        assert "DRY RUN COMPLETE" in output

    def test_report_shows_source_url(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert valid_config['source']['server_url'] in output

    def test_report_shows_destination_url(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert valid_config['destination']['pod_url'] in output

    def test_report_shows_default_owner(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert valid_config['default_content_owner'] in output

    def test_report_shows_migration_scope(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert "WILL MIGRATE" in output

    def test_report_shows_skipped_types(self, valid_config, capsys):
        valid_config['migration_scope'] = {'data_sources': False, 'workbooks': False}
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert "SKIP" in output

    def test_report_shows_mapping_preview(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        # Should show sample username mapped with configured domain
        assert "jsmith@test.com" in output

    def test_report_shows_email_passthrough(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        # bob@existing.com should pass through unchanged
        assert "bob@existing.com" in output

    def test_report_always_skips_users_groups_projects(self, valid_config, capsys):
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert "Users: SKIP (always)" in output
        assert "Groups: SKIP (always)" in output
        assert "Projects: SKIP (always)" in output

    def test_report_with_default_site(self, valid_config, capsys):
        valid_config['source']['site_content_url'] = ''
        print_dry_run_report(valid_config)
        output = capsys.readouterr().out
        assert "Default" in output
