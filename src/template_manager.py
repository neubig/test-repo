#!/usr/bin/env python3
"""
Configuration Template Manager for py2to3 toolkit

Provides pre-configured templates for common project types to help users
get started quickly with best-practice migration configurations.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class TemplateManager:
    """
    Manages configuration templates for different project types.
    """

    # Built-in templates for common project types
    BUILTIN_TEMPLATES = {
        "django": {
            "name": "Django Web Application",
            "description": "Configuration optimized for Django web applications",
            "category": "web",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups",
                    "max_backups": 10
                },
                "fixer": {
                    "skip_patterns": [
                        "*/migrations/*",
                        "*/static/*",
                        "*/media/*",
                        "*/locale/*"
                    ],
                    "safe_mode": False,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True,
                    "check_syntax": True
                },
                "priorities": {
                    "models": "high",
                    "views": "high",
                    "urls": "medium",
                    "forms": "high",
                    "admin": "medium",
                    "settings": "critical",
                    "tests": "low"
                },
                "custom_rules": [
                    {
                        "name": "django_unicode_literals",
                        "pattern": "from __future__ import unicode_literals",
                        "action": "remove",
                        "note": "No longer needed in Python 3"
                    }
                ]
            },
            "tips": [
                "Start with models.py and forms.py - they're usually straightforward",
                "Test database migrations thoroughly after conversion",
                "Check middleware compatibility - some changed in Django 2.x+",
                "Update settings.py last after everything else works"
            ]
        },
        "flask": {
            "name": "Flask Web Application",
            "description": "Configuration optimized for Flask web applications",
            "category": "web",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups",
                    "max_backups": 5
                },
                "fixer": {
                    "skip_patterns": [
                        "*/static/*",
                        "*/templates/*",
                        "*/uploads/*"
                    ],
                    "safe_mode": False,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True
                },
                "priorities": {
                    "routes": "high",
                    "models": "high",
                    "forms": "medium",
                    "views": "high",
                    "config": "critical"
                }
            },
            "tips": [
                "Flask's Python 3 support is excellent - migration is usually smooth",
                "Check extensions for Python 3 compatibility",
                "Test request/response handling thoroughly",
                "Update Jinja2 templates if using Python expressions"
            ]
        },
        "fastapi": {
            "name": "FastAPI Application",
            "description": "Configuration for FastAPI applications (Python 3.6+ only)",
            "category": "web",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups"
                },
                "fixer": {
                    "skip_patterns": ["*/static/*"],
                    "safe_mode": False,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True,
                    "check_syntax": True,
                    "check_type_hints": True
                },
                "modernize": {
                    "use_async": True,
                    "use_type_hints": True,
                    "use_f_strings": True
                }
            },
            "tips": [
                "FastAPI requires Python 3.6+, perfect for modern Python 3",
                "Leverage type hints - FastAPI uses them extensively",
                "Consider using async/await for better performance",
                "FastAPI has no Python 2 support, so clean migration expected"
            ]
        },
        "data-science": {
            "name": "Data Science / ML Project",
            "description": "Configuration for data science and machine learning projects",
            "category": "data",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups"
                },
                "fixer": {
                    "skip_patterns": [
                        "*/data/*",
                        "*/datasets/*",
                        "*/models/*",
                        "*.ipynb",
                        "*.csv",
                        "*.pkl"
                    ],
                    "safe_mode": True,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": False,
                    "check_imports": True
                },
                "priorities": {
                    "notebooks": "low",
                    "preprocessing": "high",
                    "models": "high",
                    "utils": "medium"
                },
                "packages": {
                    "check_compatibility": [
                        "numpy",
                        "pandas",
                        "scipy",
                        "scikit-learn",
                        "matplotlib",
                        "tensorflow",
                        "pytorch"
                    ]
                }
            },
            "tips": [
                "NumPy and Pandas have excellent Python 3 support",
                "Check integer division carefully - behavior changed in Python 3",
                "Test data loading/saving - pickle compatibility may be affected",
                "Jupyter notebooks may need separate conversion",
                "Verify random number generator results for reproducibility"
            ]
        },
        "cli-tool": {
            "name": "Command-Line Tool",
            "description": "Configuration for CLI applications and tools",
            "category": "tool",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups"
                },
                "fixer": {
                    "skip_patterns": ["*/tests/*"],
                    "safe_mode": False,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True,
                    "check_syntax": True
                },
                "priorities": {
                    "cli": "high",
                    "commands": "high",
                    "utils": "medium"
                }
            },
            "tips": [
                "Test input/output handling - encoding behavior changed",
                "Check argument parsing - argparse is Python 3 compatible",
                "Verify file operations use proper encoding",
                "Test on different terminals and platforms"
            ]
        },
        "library": {
            "name": "Python Library/Package",
            "description": "Configuration for Python libraries and packages",
            "category": "library",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups"
                },
                "fixer": {
                    "skip_patterns": [
                        "*/tests/*",
                        "*/docs/*",
                        "setup.py"
                    ],
                    "safe_mode": True,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True,
                    "check_syntax": True,
                    "check_api_compatibility": True
                },
                "testing": {
                    "run_tests_after_fix": True,
                    "coverage_required": True
                },
                "priorities": {
                    "public_api": "critical",
                    "internal": "high",
                    "tests": "medium",
                    "examples": "low"
                }
            },
            "tips": [
                "Maintain backward compatibility if possible",
                "Update setup.py to support Python 3 only or both",
                "Test all public APIs thoroughly",
                "Update documentation with Python 3 examples",
                "Consider using 'python_requires' in setup.py"
            ]
        },
        "test-automation": {
            "name": "Test Automation Framework",
            "description": "Configuration for test automation projects",
            "category": "testing",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups"
                },
                "fixer": {
                    "skip_patterns": [
                        "*/test_data/*",
                        "*/fixtures/*",
                        "*/reports/*"
                    ],
                    "safe_mode": True,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True
                },
                "priorities": {
                    "test_runner": "critical",
                    "test_cases": "high",
                    "fixtures": "medium",
                    "reporters": "medium"
                }
            },
            "tips": [
                "Selenium and pytest have great Python 3 support",
                "Check test discovery - may behave differently",
                "Verify assertion messages still work correctly",
                "Test parallel execution if used"
            ]
        },
        "minimal": {
            "name": "Minimal Configuration",
            "description": "Minimal safe configuration for any project type",
            "category": "general",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups"
                },
                "fixer": {
                    "safe_mode": True,
                    "verify_after_fix": True
                },
                "verifier": {
                    "strict_mode": False
                }
            },
            "tips": [
                "Start with safe mode enabled",
                "Review all changes carefully",
                "Test incrementally",
                "Create backups before major changes"
            ]
        },
        "aggressive": {
            "name": "Aggressive Migration",
            "description": "Fast, comprehensive migration for well-tested codebases",
            "category": "general",
            "config": {
                "backup": {
                    "enabled": True,
                    "dir": "backups",
                    "max_backups": 3
                },
                "fixer": {
                    "safe_mode": False,
                    "verify_after_fix": True,
                    "auto_fix": True
                },
                "verifier": {
                    "strict_mode": True,
                    "check_imports": True,
                    "check_syntax": True
                },
                "modernize": {
                    "use_f_strings": True,
                    "use_pathlib": True,
                    "use_type_hints": False
                },
                "testing": {
                    "run_tests_after_fix": True
                }
            },
            "tips": [
                "Only use if you have comprehensive test coverage",
                "Review changes after migration",
                "Expect to fix some edge cases manually",
                "Have a rollback plan ready"
            ]
        }
    }

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template manager.

        Args:
            templates_dir: Directory for custom templates (default: .py2to3/templates)
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = Path.home() / ".py2to3" / "templates"

        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available templates.

        Args:
            category: Filter by category (web, data, tool, library, testing, general)

        Returns:
            List of template info dictionaries
        """
        templates = []

        # Add built-in templates
        for template_id, template_data in self.BUILTIN_TEMPLATES.items():
            if category is None or template_data.get("category") == category:
                templates.append({
                    "id": template_id,
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "category": template_data.get("category", "general"),
                    "source": "builtin"
                })

        # Add custom templates
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    if category is None or template_data.get("category") == category:
                        templates.append({
                            "id": template_file.stem,
                            "name": template_data.get("name", template_file.stem),
                            "description": template_data.get("description", "Custom template"),
                            "category": template_data.get("category", "general"),
                            "source": "custom"
                        })
            except Exception:
                continue

        return templates

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Template data dictionary or None if not found
        """
        # Check built-in templates first
        if template_id in self.BUILTIN_TEMPLATES:
            return self.BUILTIN_TEMPLATES[template_id].copy()

        # Check custom templates
        template_file = self.templates_dir / f"{template_id}.json"
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def apply_template(self, template_id: str, config_file: str = ".py2to3config.json",
                      merge: bool = True) -> bool:
        """
        Apply a template to a configuration file.

        Args:
            template_id: Template to apply
            config_file: Path to configuration file
            merge: If True, merge with existing config; if False, replace

        Returns:
            True if successful, False otherwise
        """
        template = self.get_template(template_id)
        if not template:
            return False

        config_path = Path(config_file)
        template_config = template.get("config", {})

        if merge and config_path.exists():
            # Merge with existing configuration
            try:
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
                merged_config = self._merge_configs(existing_config, template_config)
            except Exception:
                merged_config = template_config
        else:
            # Replace with template configuration
            merged_config = template_config

        # Write configuration
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(merged_config, f, indent=2)
            return True
        except Exception:
            return False

    def create_template(self, name: str, description: str, config_file: str,
                       category: str = "general", tips: Optional[List[str]] = None) -> bool:
        """
        Create a custom template from a configuration file.

        Args:
            name: Template name
            description: Template description
            config_file: Source configuration file
            category: Template category
            tips: Optional list of tips

        Returns:
            True if successful, False otherwise
        """
        config_path = Path(config_file)
        if not config_path.exists():
            return False

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            template_id = name.lower().replace(" ", "-").replace("_", "-")
            template_data = {
                "name": name,
                "description": description,
                "category": category,
                "config": config,
                "tips": tips or []
            }

            template_file = self.templates_dir / f"{template_id}.json"
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)

            return True
        except Exception:
            return False

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a custom template.

        Args:
            template_id: Template to delete

        Returns:
            True if successful, False otherwise
        """
        # Can't delete built-in templates
        if template_id in self.BUILTIN_TEMPLATES:
            return False

        template_file = self.templates_dir / f"{template_id}.json"
        if template_file.exists():
            try:
                template_file.unlink()
                return True
            except Exception:
                return False

        return False

    def export_template(self, template_id: str, output_file: str) -> bool:
        """
        Export a template to a file.

        Args:
            template_id: Template to export
            output_file: Output file path

        Returns:
            True if successful, False otherwise
        """
        template = self.get_template(template_id)
        if not template:
            return False

        try:
            with open(output_file, 'w') as f:
                json.dump(template, f, indent=2)
            return True
        except Exception:
            return False

    def import_template(self, template_file: str) -> Optional[str]:
        """
        Import a template from a file.

        Args:
            template_file: Path to template file

        Returns:
            Template ID if successful, None otherwise
        """
        try:
            with open(template_file, 'r') as f:
                template_data = json.load(f)

            name = template_data.get("name", "Imported Template")
            template_id = name.lower().replace(" ", "-").replace("_", "-")

            output_file = self.templates_dir / f"{template_id}.json"
            with open(output_file, 'w') as f:
                json.dump(template_data, f, indent=2)

            return template_id
        except Exception:
            return None

    @staticmethod
    def _merge_configs(base: Dict, override: Dict) -> Dict:
        """
        Deep merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Configuration to merge in

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = TemplateManager._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def get_categories(self) -> List[str]:
        """
        Get all available template categories.

        Returns:
            List of category names
        """
        categories = set()
        for template in self.list_templates():
            categories.add(template["category"])
        return sorted(categories)


def main():
    """Command-line interface for template manager."""
    import argparse

    parser = argparse.ArgumentParser(description="py2to3 Configuration Template Manager")
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    # List templates
    parser_list = subparsers.add_parser('list', help='List available templates')
    parser_list.add_argument('--category', help='Filter by category')

    # Show template details
    parser_show = subparsers.add_parser('show', help='Show template details')
    parser_show.add_argument('template_id', help='Template ID')

    # Apply template
    parser_apply = subparsers.add_parser('apply', help='Apply template to configuration')
    parser_apply.add_argument('template_id', help='Template ID')
    parser_apply.add_argument('--config', default='.py2to3config.json', help='Config file')
    parser_apply.add_argument('--replace', action='store_true', help='Replace instead of merge')

    # Create template
    parser_create = subparsers.add_parser('create', help='Create custom template')
    parser_create.add_argument('name', help='Template name')
    parser_create.add_argument('--description', required=True, help='Template description')
    parser_create.add_argument('--config', required=True, help='Source config file')
    parser_create.add_argument('--category', default='general', help='Template category')

    # Export template
    parser_export = subparsers.add_parser('export', help='Export template')
    parser_export.add_argument('template_id', help='Template ID')
    parser_export.add_argument('output', help='Output file')

    # Import template
    parser_import = subparsers.add_parser('import', help='Import template')
    parser_import.add_argument('file', help='Template file to import')

    args = parser.parse_args()
    manager = TemplateManager()

    if args.action == 'list':
        templates = manager.list_templates(category=args.category)
        for template in templates:
            print(f"{template['id']:20} - {template['name']} ({template['category']})")
            print(f"{'':20}   {template['description']}")
            print()

    elif args.action == 'show':
        template = manager.get_template(args.template_id)
        if template:
            print(json.dumps(template, indent=2))
        else:
            print(f"Template not found: {args.template_id}", file=sys.stderr)
            return 1

    elif args.action == 'apply':
        if manager.apply_template(args.template_id, args.config, merge=not args.replace):
            print(f"Template applied: {args.template_id}")
        else:
            print(f"Failed to apply template: {args.template_id}", file=sys.stderr)
            return 1

    elif args.action == 'create':
        if manager.create_template(args.name, args.description, args.config, args.category):
            template_id = args.name.lower().replace(" ", "-")
            print(f"Template created: {template_id}")
        else:
            print("Failed to create template", file=sys.stderr)
            return 1

    elif args.action == 'export':
        if manager.export_template(args.template_id, args.output):
            print(f"Template exported: {args.output}")
        else:
            print(f"Failed to export template: {args.template_id}", file=sys.stderr)
            return 1

    elif args.action == 'import':
        template_id = manager.import_template(args.file)
        if template_id:
            print(f"Template imported: {template_id}")
        else:
            print("Failed to import template", file=sys.stderr)
            return 1

    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
