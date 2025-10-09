#!/usr/bin/env python3
"""
Custom Rules Manager for Python 2 to 3 Migration

This module allows users to define, manage, and apply custom migration rules
beyond the built-in patterns. Perfect for organization-specific coding standards
and project-specific patterns.
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class CustomRule:
    """Represents a single custom migration rule."""
    
    def __init__(self, rule_id: str, name: str, description: str,
                 pattern: str, replacement: str, category: str = "custom",
                 enabled: bool = True, regex: bool = True,
                 whole_word: bool = False, case_sensitive: bool = True):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.pattern = pattern
        self.replacement = replacement
        self.category = category
        self.enabled = enabled
        self.regex = regex
        self.whole_word = whole_word
        self.case_sensitive = case_sensitive
        self.created_at = datetime.now().isoformat()
        self.applied_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary format."""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'pattern': self.pattern,
            'replacement': self.replacement,
            'category': self.category,
            'enabled': self.enabled,
            'regex': self.regex,
            'whole_word': self.whole_word,
            'case_sensitive': self.case_sensitive,
            'created_at': self.created_at,
            'applied_count': self.applied_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomRule':
        """Create rule from dictionary."""
        rule = cls(
            rule_id=data['rule_id'],
            name=data['name'],
            description=data['description'],
            pattern=data['pattern'],
            replacement=data['replacement'],
            category=data.get('category', 'custom'),
            enabled=data.get('enabled', True),
            regex=data.get('regex', True),
            whole_word=data.get('whole_word', False),
            case_sensitive=data.get('case_sensitive', True)
        )
        rule.created_at = data.get('created_at', rule.created_at)
        rule.applied_count = data.get('applied_count', 0)
        return rule
    
    def apply(self, content: str) -> Tuple[str, int]:
        """
        Apply this rule to the given content.
        
        Returns:
            Tuple of (modified_content, number_of_changes)
        """
        if not self.enabled:
            return content, 0
        
        original_content = content
        flags = 0 if self.case_sensitive else re.IGNORECASE
        
        if self.regex:
            if self.whole_word:
                pattern = r'\b' + self.pattern + r'\b'
            else:
                pattern = self.pattern
            
            try:
                content = re.sub(pattern, self.replacement, content, flags=flags)
            except re.error as e:
                print(f"Warning: Invalid regex pattern in rule '{self.name}': {e}")
                return original_content, 0
        else:
            # Simple string replacement
            if self.case_sensitive:
                content = content.replace(self.pattern, self.replacement)
            else:
                # Case-insensitive simple replacement
                pattern = re.compile(re.escape(self.pattern), re.IGNORECASE)
                content = pattern.sub(self.replacement, content)
        
        # Count changes (approximate)
        if content != original_content:
            # Count occurrences of the replacement that differ from original
            changes = len(content.split(self.replacement)) - len(original_content.split(self.replacement))
            return content, max(abs(changes), 1)
        
        return content, 0


class CustomRulesManager:
    """Manager for custom migration rules."""
    
    def __init__(self, rules_file: str = None):
        """
        Initialize the rules manager.
        
        Args:
            rules_file: Path to the rules JSON file. If None, uses default location.
        """
        if rules_file is None:
            rules_file = os.path.join(os.getcwd(), '.py2to3_custom_rules.json')
        
        self.rules_file = Path(rules_file)
        self.rules: List[CustomRule] = []
        self.load_rules()
    
    def load_rules(self) -> None:
        """Load rules from the JSON file."""
        if not self.rules_file.exists():
            # Create default rules file
            self._create_default_rules()
            return
        
        try:
            with open(self.rules_file, 'r') as f:
                data = json.load(f)
                self.rules = [CustomRule.from_dict(rule_data) for rule_data in data.get('rules', [])]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading rules file: {e}")
            self.rules = []
    
    def save_rules(self) -> None:
        """Save rules to the JSON file."""
        data = {
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'rules': [rule.to_dict() for rule in self.rules]
        }
        
        with open(self.rules_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_default_rules(self) -> None:
        """Create a default rules file with examples."""
        example_rules = [
            CustomRule(
                rule_id='custom_logger_py3',
                name='Logger Module Migration',
                description='Replace custom logger.logMessage() with logger.log_message()',
                pattern=r'\.logMessage\(',
                replacement='.log_message(',
                category='custom',
                regex=True
            ),
            CustomRule(
                rule_id='legacy_database_connect',
                name='Legacy Database Connection',
                description='Update legacy database.connect() to database.create_connection()',
                pattern=r'database\.connect\(',
                replacement='database.create_connection(',
                category='custom',
                regex=True
            ),
            CustomRule(
                rule_id='old_config_import',
                name='Old Config Import',
                description='Replace old_config module with new_config',
                pattern=r'from old_config import',
                replacement='from new_config import',
                category='imports',
                regex=False
            ),
        ]
        
        self.rules = example_rules
        self.save_rules()
        print(f"Created default rules file: {self.rules_file}")
    
    def add_rule(self, rule: CustomRule) -> bool:
        """
        Add a new rule.
        
        Returns:
            True if rule was added, False if rule_id already exists.
        """
        if any(r.rule_id == rule.rule_id for r in self.rules):
            return False
        
        self.rules.append(rule)
        self.save_rules()
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a rule by ID.
        
        Returns:
            True if rule was removed, False if not found.
        """
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.rule_id != rule_id]
        
        if len(self.rules) < original_count:
            self.save_rules()
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[CustomRule]:
        """Get a rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
            self.save_rules()
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
            self.save_rules()
            return True
        return False
    
    def list_rules(self, category: Optional[str] = None, 
                   enabled_only: bool = False) -> List[CustomRule]:
        """
        List all rules, optionally filtered.
        
        Args:
            category: Filter by category (optional)
            enabled_only: Only return enabled rules
        
        Returns:
            List of matching rules
        """
        filtered_rules = self.rules
        
        if category:
            filtered_rules = [r for r in filtered_rules if r.category == category]
        
        if enabled_only:
            filtered_rules = [r for r in filtered_rules if r.enabled]
        
        return filtered_rules
    
    def apply_rules(self, content: str, rule_ids: Optional[List[str]] = None) -> Tuple[str, Dict[str, int]]:
        """
        Apply rules to content.
        
        Args:
            content: The content to transform
            rule_ids: List of specific rule IDs to apply (None = apply all enabled)
        
        Returns:
            Tuple of (modified_content, changes_by_rule_id)
        """
        if rule_ids:
            rules_to_apply = [r for r in self.rules if r.rule_id in rule_ids]
        else:
            rules_to_apply = [r for r in self.rules if r.enabled]
        
        changes = {}
        modified_content = content
        
        for rule in rules_to_apply:
            modified_content, change_count = rule.apply(modified_content)
            if change_count > 0:
                changes[rule.rule_id] = change_count
                rule.applied_count += change_count
        
        if changes:
            self.save_rules()  # Save updated applied_count
        
        return modified_content, changes
    
    def test_rule(self, rule_id: str, test_content: str) -> Tuple[str, int]:
        """
        Test a rule on sample content without saving changes.
        
        Returns:
            Tuple of (modified_content, number_of_changes)
        """
        rule = self.get_rule(rule_id)
        if not rule:
            return test_content, 0
        
        return rule.apply(test_content)
    
    def export_rules(self, output_file: str, rule_ids: Optional[List[str]] = None) -> None:
        """
        Export rules to a file for sharing.
        
        Args:
            output_file: Path to output file
            rule_ids: List of specific rule IDs to export (None = export all)
        """
        if rule_ids:
            rules_to_export = [r for r in self.rules if r.rule_id in rule_ids]
        else:
            rules_to_export = self.rules
        
        data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'rules': [rule.to_dict() for rule in rules_to_export]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Exported {len(rules_to_export)} rules to {output_file}")
    
    def import_rules(self, input_file: str, overwrite: bool = False) -> Tuple[int, int]:
        """
        Import rules from a file.
        
        Args:
            input_file: Path to input file
            overwrite: If True, overwrite existing rules with same ID
        
        Returns:
            Tuple of (imported_count, skipped_count)
        """
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        imported = 0
        skipped = 0
        
        for rule_data in data.get('rules', []):
            rule = CustomRule.from_dict(rule_data)
            
            existing_rule = self.get_rule(rule.rule_id)
            if existing_rule:
                if overwrite:
                    self.remove_rule(rule.rule_id)
                    self.rules.append(rule)
                    imported += 1
                else:
                    skipped += 1
            else:
                self.rules.append(rule)
                imported += 1
        
        if imported > 0:
            self.save_rules()
        
        return imported, skipped
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the rules."""
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules if r.enabled])
        disabled_rules = total_rules - enabled_rules
        
        categories = {}
        for rule in self.rules:
            categories[rule.category] = categories.get(rule.category, 0) + 1
        
        total_applications = sum(r.applied_count for r in self.rules)
        
        return {
            'total_rules': total_rules,
            'enabled_rules': enabled_rules,
            'disabled_rules': disabled_rules,
            'categories': categories,
            'total_applications': total_applications,
            'rules_file': str(self.rules_file)
        }


def apply_custom_rules_to_file(file_path: str, manager: CustomRulesManager,
                                 backup: bool = True) -> Dict[str, Any]:
    """
    Apply custom rules to a file.
    
    Args:
        file_path: Path to the file to modify
        manager: CustomRulesManager instance
        backup: Whether to create a backup before modifying
    
    Returns:
        Dictionary with results
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {'error': f'File not found: {file_path}'}
    
    # Read original content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except UnicodeDecodeError:
        return {'error': f'Unable to read file (encoding issue): {file_path}'}
    
    # Create backup if requested
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
    
    # Apply rules
    modified_content, changes = manager.apply_rules(original_content)
    
    # Write modified content if there were changes
    if changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
    
    return {
        'file': str(file_path),
        'changes': changes,
        'total_changes': sum(changes.values()),
        'backup': str(backup_path) if backup and changes else None
    }


def main():
    """Command-line interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Custom Rules Manager')
    parser.add_argument('--rules-file', help='Path to rules file')
    parser.add_argument('--list', action='store_true', help='List all rules')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    manager = CustomRulesManager(args.rules_file)
    
    if args.list:
        print(f"\nCustom Rules ({len(manager.rules)} total):\n")
        for rule in manager.rules:
            status = "✓" if rule.enabled else "✗"
            print(f"{status} [{rule.rule_id}] {rule.name}")
            print(f"   Category: {rule.category}")
            print(f"   Pattern: {rule.pattern}")
            print(f"   Replacement: {rule.replacement}")
            print(f"   Applied: {rule.applied_count} times\n")
    
    if args.stats:
        stats = manager.get_statistics()
        print("\nCustom Rules Statistics:")
        print(f"  Total Rules: {stats['total_rules']}")
        print(f"  Enabled: {stats['enabled_rules']}")
        print(f"  Disabled: {stats['disabled_rules']}")
        print(f"  Total Applications: {stats['total_applications']}")
        print(f"\nCategories:")
        for category, count in stats['categories'].items():
            print(f"  {category}: {count}")
        print(f"\nRules File: {stats['rules_file']}")


if __name__ == '__main__':
    main()
