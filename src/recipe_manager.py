#!/usr/bin/env python3
"""
Migration Recipe Manager

Provides reusable migration recipes/templates for different project types.
Recipes include recommended configurations, fix priorities, and best practices
for specific frameworks and project types (Django, Flask, CLI tools, etc.).
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class Recipe:
    """Represents a migration recipe with configuration and metadata."""
    
    def __init__(self, name: str, description: str, author: str = "py2to3",
                 config: Optional[Dict[str, Any]] = None,
                 fix_order: Optional[List[str]] = None,
                 ignore_patterns: Optional[List[str]] = None,
                 notes: Optional[List[str]] = None,
                 tags: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.author = author
        self.config = config or {}
        self.fix_order = fix_order or []
        self.ignore_patterns = ignore_patterns or []
        self.notes = notes or []
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "config": self.config,
            "fix_order": self.fix_order,
            "ignore_patterns": self.ignore_patterns,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """Create recipe from dictionary."""
        recipe = cls(
            name=data["name"],
            description=data["description"],
            author=data.get("author", "py2to3"),
            config=data.get("config", {}),
            fix_order=data.get("fix_order", []),
            ignore_patterns=data.get("ignore_patterns", []),
            notes=data.get("notes", []),
            tags=data.get("tags", [])
        )
        recipe.created_at = data.get("created_at", recipe.created_at)
        return recipe


class RecipeManager:
    """Manages migration recipes - save, load, list, and apply."""
    
    def __init__(self, recipes_dir: Optional[str] = None):
        if recipes_dir:
            self.recipes_dir = Path(recipes_dir)
        else:
            # Use ~/.py2to3/recipes by default
            home = Path.home()
            self.recipes_dir = home / ".py2to3" / "recipes"
        
        # Also check for bundled recipes in the package
        self.bundled_recipes_dir = Path(__file__).parent / "data" / "recipes"
        
        # Ensure directories exist
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
    
    def get_recipe_path(self, name: str) -> Path:
        """Get path to recipe file."""
        safe_name = name.replace(" ", "_").replace("/", "_")
        return self.recipes_dir / f"{safe_name}.json"
    
    def get_bundled_recipe_path(self, name: str) -> Path:
        """Get path to bundled recipe file."""
        safe_name = name.replace(" ", "_").replace("/", "_")
        return self.bundled_recipes_dir / f"{safe_name}.json"
    
    def save_recipe(self, recipe: Recipe, overwrite: bool = False) -> bool:
        """Save a recipe to disk."""
        recipe_path = self.get_recipe_path(recipe.name)
        
        if recipe_path.exists() and not overwrite:
            print(f"Recipe '{recipe.name}' already exists. Use --force to overwrite.")
            return False
        
        try:
            with open(recipe_path, 'w') as f:
                json.dump(recipe.to_dict(), f, indent=2)
            print(f"✓ Recipe '{recipe.name}' saved to {recipe_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to save recipe: {e}")
            return False
    
    def load_recipe(self, name: str) -> Optional[Recipe]:
        """Load a recipe from disk."""
        # Try user recipes first
        recipe_path = self.get_recipe_path(name)
        if recipe_path.exists():
            return self._load_recipe_file(recipe_path)
        
        # Try bundled recipes
        bundled_path = self.get_bundled_recipe_path(name)
        if bundled_path.exists():
            return self._load_recipe_file(bundled_path)
        
        print(f"✗ Recipe '{name}' not found")
        return None
    
    def _load_recipe_file(self, path: Path) -> Optional[Recipe]:
        """Load recipe from a file path."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return Recipe.from_dict(data)
        except Exception as e:
            print(f"✗ Failed to load recipe from {path}: {e}")
            return None
    
    def list_recipes(self, include_bundled: bool = True) -> List[Recipe]:
        """List all available recipes."""
        recipes = []
        
        # Load user recipes
        if self.recipes_dir.exists():
            for recipe_file in self.recipes_dir.glob("*.json"):
                recipe = self._load_recipe_file(recipe_file)
                if recipe:
                    recipes.append(recipe)
        
        # Load bundled recipes
        if include_bundled and self.bundled_recipes_dir.exists():
            for recipe_file in self.bundled_recipes_dir.glob("*.json"):
                recipe = self._load_recipe_file(recipe_file)
                if recipe:
                    recipes.append(recipe)
        
        return recipes
    
    def delete_recipe(self, name: str) -> bool:
        """Delete a recipe."""
        recipe_path = self.get_recipe_path(name)
        
        if not recipe_path.exists():
            print(f"✗ Recipe '{name}' not found")
            return False
        
        try:
            recipe_path.unlink()
            print(f"✓ Recipe '{name}' deleted")
            return True
        except Exception as e:
            print(f"✗ Failed to delete recipe: {e}")
            return False
    
    def apply_recipe(self, name: str, target_dir: str = ".") -> bool:
        """Apply a recipe to a project."""
        recipe = self.load_recipe(name)
        if not recipe:
            return False
        
        print(f"\n📋 Applying recipe: {recipe.name}")
        print(f"   {recipe.description}")
        print()
        
        # Apply configuration
        if recipe.config:
            config_path = Path(target_dir) / ".py2to3.config.json"
            
            # Merge with existing config if present
            existing_config = {}
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        existing_config = json.load(f)
                except Exception:
                    pass
            
            # Merge configs (recipe config takes precedence)
            merged_config = {**existing_config, **recipe.config}
            
            try:
                with open(config_path, 'w') as f:
                    json.dump(merged_config, f, indent=2)
                print(f"✓ Configuration applied to {config_path}")
            except Exception as e:
                print(f"✗ Failed to apply configuration: {e}")
                return False
        
        # Display additional information
        if recipe.notes:
            print("\n📝 Important notes for this recipe:")
            for i, note in enumerate(recipe.notes, 1):
                print(f"   {i}. {note}")
        
        if recipe.fix_order:
            print("\n🔧 Recommended fix order:")
            for i, fix_type in enumerate(recipe.fix_order, 1):
                print(f"   {i}. {fix_type}")
        
        if recipe.ignore_patterns:
            print("\n🚫 Ignore patterns configured:")
            for pattern in recipe.ignore_patterns:
                print(f"   - {pattern}")
        
        print("\n✓ Recipe applied successfully!")
        print(f"\nNext steps:")
        print(f"  1. Review configuration: py2to3 config show")
        print(f"  2. Run preflight check: py2to3 preflight {target_dir}")
        print(f"  3. Start migration: py2to3 fix {target_dir}")
        
        return True
    
    def create_from_current(self, name: str, description: str, 
                          config_file: Optional[str] = None) -> bool:
        """Create a new recipe from current project configuration."""
        config = {}
        
        # Load config from file if specified
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"✗ Failed to load config from {config_file}: {e}")
                return False
        
        # Create recipe
        recipe = Recipe(
            name=name,
            description=description,
            author="custom",
            config=config
        )
        
        return self.save_recipe(recipe)
    
    def export_recipe(self, name: str, output_path: str) -> bool:
        """Export a recipe to a file."""
        recipe = self.load_recipe(name)
        if not recipe:
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(recipe.to_dict(), f, indent=2)
            print(f"✓ Recipe '{name}' exported to {output_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to export recipe: {e}")
            return False
    
    def import_recipe(self, input_path: str, overwrite: bool = False) -> bool:
        """Import a recipe from a file."""
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            recipe = Recipe.from_dict(data)
            return self.save_recipe(recipe, overwrite=overwrite)
        except Exception as e:
            print(f"✗ Failed to import recipe: {e}")
            return False


# Default bundled recipes
DEFAULT_RECIPES = {
    "django": Recipe(
        name="django",
        description="Migration recipe for Django web applications",
        tags=["web", "framework", "django"],
        config={
            "fix_rules": {
                "print_statements": True,
                "imports": True,
                "exceptions": True,
                "string_handling": True,
                "iterators": True
            },
            "backup_enabled": True,
            "create_report": True
        },
        fix_order=[
            "print_statements",
            "imports (especially urllib, urllib2)",
            "string_handling (unicode issues in templates)",
            "exceptions",
            "iterators (dict methods)",
            "settings configuration",
            "URL patterns"
        ],
        ignore_patterns=[
            "*/migrations/*",
            "*/static/*",
            "*/media/*",
            "*/venv/*",
            "*/node_modules/*"
        ],
        notes=[
            "Django 2.0+ requires Python 3.5+",
            "Check third-party packages compatibility first (use py2to3 deps)",
            "Pay special attention to unicode in templates and forms",
            "Update DATABASE settings if using MySQL",
            "Review URL patterns - url() was deprecated in Django 3.1",
            "Test all admin customizations thoroughly"
        ]
    ),
    
    "flask": Recipe(
        name="flask",
        description="Migration recipe for Flask web applications",
        tags=["web", "framework", "flask"],
        config={
            "fix_rules": {
                "print_statements": True,
                "imports": True,
                "exceptions": True,
                "string_handling": True,
                "iterators": True
            },
            "backup_enabled": True,
            "create_report": True
        },
        fix_order=[
            "print_statements",
            "imports",
            "string_handling",
            "exceptions",
            "iterators",
            "request/response handling"
        ],
        ignore_patterns=[
            "*/static/*",
            "*/venv/*",
            "*/node_modules/*",
            "*.pyc"
        ],
        notes=[
            "Flask 2.0+ requires Python 3.6+",
            "Check Flask extension compatibility (use py2to3 deps)",
            "Review string encoding in request/response handling",
            "Test file upload/download functionality",
            "Verify JSON serialization works correctly",
            "Check cookie and session handling"
        ]
    ),
    
    "cli": Recipe(
        name="cli",
        description="Migration recipe for command-line tools",
        tags=["cli", "tool"],
        config={
            "fix_rules": {
                "print_statements": True,
                "imports": True,
                "exceptions": True,
                "string_handling": True,
                "iterators": True
            },
            "backup_enabled": True,
            "create_report": True
        },
        fix_order=[
            "print_statements (affects output)",
            "imports (especially argparse, configparser)",
            "string_handling (input/output encoding)",
            "exceptions",
            "file I/O operations"
        ],
        ignore_patterns=[
            "*/venv/*",
            "*/build/*",
            "*/dist/*",
            "*.egg-info/*"
        ],
        notes=[
            "Test all command-line arguments and options",
            "Verify input/output encoding (especially for non-ASCII)",
            "Check file I/O operations with various file types",
            "Test error messages and exit codes",
            "Update shebang lines to python3",
            "Consider using click or typer for modern CLI"
        ]
    ),
    
    "data-science": Recipe(
        name="data-science",
        description="Migration recipe for data science and ML projects",
        tags=["data", "ml", "science"],
        config={
            "fix_rules": {
                "print_statements": True,
                "imports": True,
                "exceptions": True,
                "string_handling": True,
                "iterators": True,
                "division": True
            },
            "backup_enabled": True,
            "create_report": True
        },
        fix_order=[
            "division (/ vs //)",
            "imports (especially numpy, pandas, sklearn)",
            "print_statements",
            "iterators (zip, map, filter return iterators)",
            "string_handling",
            "pickle compatibility"
        ],
        ignore_patterns=[
            "*/data/*",
            "*/models/*",
            "*/checkpoints/*",
            "*.ipynb_checkpoints/*",
            "*/venv/*"
        ],
        notes=[
            "Integer division changed (/ now returns float)",
            "Check numpy, pandas, scikit-learn versions (use py2to3 deps)",
            "Pickle files may need regeneration",
            "map, filter, zip now return iterators (not lists)",
            "Test all data loading and preprocessing pipelines",
            "Verify model serialization/deserialization",
            "Re-run experiments to ensure reproducibility"
        ]
    ),
    
    "library": Recipe(
        name="library",
        description="Migration recipe for Python libraries/packages",
        tags=["library", "package"],
        config={
            "fix_rules": {
                "print_statements": True,
                "imports": True,
                "exceptions": True,
                "string_handling": True,
                "iterators": True,
                "division": True
            },
            "backup_enabled": True,
            "create_report": True
        },
        fix_order=[
            "imports",
            "string_handling",
            "exceptions",
            "iterators",
            "print_statements",
            "division"
        ],
        ignore_patterns=[
            "*/tests/*",
            "*/docs/*",
            "*/build/*",
            "*/dist/*",
            "*.egg-info/*"
        ],
        notes=[
            "Update setup.py to specify python_requires='>=3.6'",
            "Update classifiers in setup.py",
            "Maintain backward compatibility if needed",
            "Update documentation and README",
            "Add type hints for better IDE support",
            "Run full test suite with multiple Python 3 versions",
            "Update CI/CD to test Python 3.7, 3.8, 3.9, 3.10, 3.11",
            "Consider using tox for multi-version testing"
        ]
    )
}


def create_bundled_recipes():
    """Create bundled recipe files in the package data directory."""
    script_dir = Path(__file__).parent
    recipes_dir = script_dir / "data" / "recipes"
    recipes_dir.mkdir(parents=True, exist_ok=True)
    
    for recipe_name, recipe in DEFAULT_RECIPES.items():
        recipe_path = recipes_dir / f"{recipe_name}.json"
        with open(recipe_path, 'w') as f:
            json.dump(recipe.to_dict(), f, indent=2)
        print(f"Created bundled recipe: {recipe_path}")


if __name__ == "__main__":
    # Create bundled recipes when run directly
    create_bundled_recipes()
