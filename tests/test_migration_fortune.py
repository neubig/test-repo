#!/usr/bin/env python3
"""
Tests for the migration_fortune module.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from migration_fortune import FORTUNES, MigrationFortune


class TestMigrationFortune:
    """Test suite for MigrationFortune"""

    def test_fortune_catalog_not_empty(self):
        """The fortune catalog should contain at least one fortune."""
        assert len(FORTUNES) > 0

    def test_count_matches_catalog(self):
        """The count property should reflect the catalog size."""
        fortune = MigrationFortune()
        assert fortune.count == len(FORTUNES)

    def test_get_fortune_returns_from_catalog(self):
        """get_fortune should always return a known fortune string."""
        fortune = MigrationFortune()
        assert fortune.get_fortune() in FORTUNES

    def test_deterministic_with_seed(self):
        """Same seed should produce the same sequence of fortunes."""
        first = MigrationFortune(seed=42)
        second = MigrationFortune(seed=42)
        assert first.get_fortune() == second.get_fortune()
        assert first.get_fortune() == second.get_fortune()

    def test_different_seeds_usually_differ(self):
        """Different seeds should generally produce different fortunes."""
        results = {MigrationFortune(seed=s).get_fortune() for s in range(100)}
        assert len(results) > 1

    def test_return_type_is_str(self):
        """get_fortune should return a string."""
        fortune = MigrationFortune(seed=1)
        assert isinstance(fortune.get_fortune(), str)