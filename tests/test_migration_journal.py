#!/usr/bin/env python3
"""
Tests for migration_journal module
"""

import os
import sys
import json
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from migration_journal import MigrationJournal, JournalEntry


class TestJournalEntry:
    """Tests for JournalEntry class."""
    
    def test_entry_creation(self):
        """Test creating a journal entry."""
        entry = JournalEntry(
            content="Test content",
            tags=["tag1", "tag2"],
            category="decision",
            related_files=["file1.py"],
            author="TestAuthor"
        )
        
        assert entry.content == "Test content"
        assert entry.tags == ["tag1", "tag2"]
        assert entry.category == "decision"
        assert entry.related_files == ["file1.py"]
        assert entry.author == "TestAuthor"
        assert entry.id.startswith("entry_")
        assert entry.timestamp is not None
    
    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = JournalEntry("Test content", tags=["tag1"])
        data = entry.to_dict()
        
        assert isinstance(data, dict)
        assert data['content'] == "Test content"
        assert data['tags'] == ["tag1"]
        assert 'id' in data
        assert 'timestamp' in data
    
    def test_entry_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            'id': 'test_id',
            'timestamp': '2024-01-01T10:00:00',
            'content': 'Test content',
            'tags': ['tag1'],
            'category': 'issue',
            'related_files': ['file.py'],
            'author': 'TestAuthor'
        }
        
        entry = JournalEntry.from_dict(data)
        
        assert entry.id == 'test_id'
        assert entry.timestamp == '2024-01-01T10:00:00'
        assert entry.content == 'Test content'
        assert entry.category == 'issue'
    
    def test_entry_matches_filter(self):
        """Test entry filtering."""
        entry = JournalEntry(
            "Test content with keyword",
            tags=["tag1", "tag2"],
            category="decision",
            author="Alice"
        )
        
        assert entry.matches_filter(search_term="keyword")
        assert entry.matches_filter(tags=["tag1"])
        assert entry.matches_filter(category="decision")
        assert entry.matches_filter(author="Alice")
        assert not entry.matches_filter(search_term="notfound")
        assert not entry.matches_filter(tags=["nonexistent"])


class TestMigrationJournal:
    """Tests for MigrationJournal class."""
    
    @pytest.fixture
    def temp_journal(self):
        """Create a temporary journal for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        journal = MigrationJournal(temp_path)
        yield journal
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_journal_creation(self, temp_journal):
        """Test creating a journal."""
        assert isinstance(temp_journal, MigrationJournal)
        assert len(temp_journal.entries) == 0
    
    def test_add_entry(self, temp_journal):
        """Test adding an entry."""
        entry = temp_journal.add_entry(
            content="Test content",
            tags=["tag1"],
            category="decision"
        )
        
        assert entry in temp_journal.entries
        assert len(temp_journal.entries) == 1
        assert entry.content == "Test content"
    
    def test_invalid_category(self, temp_journal):
        """Test adding entry with invalid category."""
        with pytest.raises(ValueError):
            temp_journal.add_entry("Test", category="invalid_category")
    
    def test_get_entries(self, temp_journal):
        """Test retrieving entries."""
        temp_journal.add_entry("Entry 1", tags=["tag1"], category="decision")
        temp_journal.add_entry("Entry 2", tags=["tag2"], category="issue")
        temp_journal.add_entry("Entry 3", tags=["tag1"], category="solution")
        
        all_entries = temp_journal.get_entries()
        assert len(all_entries) == 3
        
        tag1_entries = temp_journal.get_entries(tags=["tag1"])
        assert len(tag1_entries) == 2
        
        decision_entries = temp_journal.get_entries(category="decision")
        assert len(decision_entries) == 1
    
    def test_get_entry_by_id(self, temp_journal):
        """Test getting entry by ID."""
        entry = temp_journal.add_entry("Test content")
        
        retrieved = temp_journal.get_entry_by_id(entry.id)
        assert retrieved is not None
        assert retrieved.id == entry.id
        assert retrieved.content == "Test content"
        
        not_found = temp_journal.get_entry_by_id("nonexistent_id")
        assert not_found is None
    
    def test_delete_entry(self, temp_journal):
        """Test deleting an entry."""
        entry = temp_journal.add_entry("Test content")
        
        assert len(temp_journal.entries) == 1
        
        success = temp_journal.delete_entry(entry.id)
        assert success is True
        assert len(temp_journal.entries) == 0
        
        success = temp_journal.delete_entry("nonexistent")
        assert success is False
    
    def test_get_statistics(self, temp_journal):
        """Test getting journal statistics."""
        temp_journal.add_entry("Entry 1", tags=["tag1"], category="decision", author="Alice")
        temp_journal.add_entry("Entry 2", tags=["tag2"], category="issue", author="Bob")
        temp_journal.add_entry("Entry 3", tags=["tag1"], category="decision", author="Alice")
        
        stats = temp_journal.get_statistics()
        
        assert stats['total_entries'] == 3
        assert stats['by_category']['decision'] == 2
        assert stats['by_category']['issue'] == 1
        assert stats['by_author']['Alice'] == 2
        assert stats['by_author']['Bob'] == 1
        assert 'tag1' in stats['unique_tags']
        assert 'tag2' in stats['unique_tags']
    
    def test_export_import_json(self, temp_journal):
        """Test JSON export and import."""
        temp_journal.add_entry("Entry 1", tags=["tag1"])
        temp_journal.add_entry("Entry 2", tags=["tag2"])
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            export_path = f.name
        
        try:
            temp_journal.export_json(export_path)
            assert os.path.exists(export_path)
            
            with open(export_path, 'r') as f:
                data = json.load(f)
            
            assert 'entries' in data
            assert len(data['entries']) == 2
            
            # Test import
            new_journal_path = export_path.replace('.json', '_new.json')
            new_journal = MigrationJournal(new_journal_path)
            count = new_journal.import_entries(export_path)
            
            assert count == 2
            assert len(new_journal.entries) == 2
            
            if os.path.exists(new_journal_path):
                os.unlink(new_journal_path)
        
        finally:
            if os.path.exists(export_path):
                os.unlink(export_path)
    
    def test_export_markdown(self, temp_journal):
        """Test Markdown export."""
        temp_journal.add_entry("Entry 1", tags=["tag1"], category="decision")
        temp_journal.add_entry("Entry 2", tags=["tag2"], category="issue")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            export_path = f.name
        
        try:
            temp_journal.export_markdown(export_path)
            assert os.path.exists(export_path)
            
            with open(export_path, 'r') as f:
                content = f.read()
            
            assert '# Migration Journal' in content
            assert 'Entry 1' in content
            assert 'Entry 2' in content
            assert '## Decision' in content
            assert '## Issue' in content
        
        finally:
            if os.path.exists(export_path):
                os.unlink(export_path)
    
    def test_tag_cloud(self, temp_journal):
        """Test tag cloud generation."""
        temp_journal.add_entry("Entry 1", tags=["tag1", "common"])
        temp_journal.add_entry("Entry 2", tags=["tag2", "common"])
        temp_journal.add_entry("Entry 3", tags=["tag3", "common"])
        
        tag_cloud = temp_journal.get_tag_cloud()
        
        assert tag_cloud['common'] == 3
        assert tag_cloud['tag1'] == 1
        assert tag_cloud['tag2'] == 1
        assert tag_cloud['tag3'] == 1
    
    def test_persistence(self, temp_journal):
        """Test that entries persist across journal instances."""
        journal_path = temp_journal.journal_path
        
        temp_journal.add_entry("Entry 1")
        temp_journal.add_entry("Entry 2")
        
        new_journal = MigrationJournal(journal_path)
        assert len(new_journal.entries) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
