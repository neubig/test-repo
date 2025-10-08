#!/usr/bin/env python3
"""
Migration Export/Import Manager

Package and share migration configurations, state, and learnings across teams
and projects. Create portable migration packages that can be imported to
bootstrap new migrations or share strategies.
"""

import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MigrationExporter:
    """Export migration configuration and state to shareable packages."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def export_package(
        self,
        output_path: Optional[str] = None,
        include_config: bool = True,
        include_recipes: bool = True,
        include_state: bool = True,
        include_journal: bool = True,
        include_stats: bool = True,
        include_backups: bool = False,
        backup_pattern: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Export migration package to a tarball.
        
        Args:
            output_path: Output file path (default: migration_export_TIMESTAMP.tar.gz)
            include_config: Include configuration files
            include_recipes: Include custom recipes
            include_state: Include migration state
            include_journal: Include journal entries
            include_stats: Include statistics snapshots
            include_backups: Include backup files
            backup_pattern: Pattern to filter backups (if including backups)
            description: Package description
            tags: Tags for categorizing the package
            
        Returns:
            Path to created package
        """
        if output_path is None:
            output_path = f"migration_export_{self.timestamp}.tar.gz"
        
        output_path = Path(output_path).resolve()
        
        # Create temporary directory for staging
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir) / "migration_package"
            staging_dir.mkdir()
            
            # Create manifest
            manifest = self._create_manifest(
                include_config=include_config,
                include_recipes=include_recipes,
                include_state=include_state,
                include_journal=include_journal,
                include_stats=include_stats,
                include_backups=include_backups,
                description=description,
                tags=tags or []
            )
            
            # Export each component
            exported_files = []
            
            if include_config:
                exported_files.extend(self._export_config(staging_dir))
                
            if include_recipes:
                exported_files.extend(self._export_recipes(staging_dir))
                
            if include_state:
                exported_files.extend(self._export_state(staging_dir))
                
            if include_journal:
                exported_files.extend(self._export_journal(staging_dir))
                
            if include_stats:
                exported_files.extend(self._export_stats(staging_dir))
                
            if include_backups:
                exported_files.extend(
                    self._export_backups(staging_dir, backup_pattern)
                )
            
            # Update manifest with actual exported files
            manifest["files"] = exported_files
            manifest["file_count"] = len(exported_files)
            
            # Write manifest
            manifest_path = staging_dir / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            
            # Create tarball
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(staging_dir, arcname="migration_package")
            
        return str(output_path)
    
    def _create_manifest(
        self,
        include_config: bool,
        include_recipes: bool,
        include_state: bool,
        include_journal: bool,
        include_stats: bool,
        include_backups: bool,
        description: Optional[str],
        tags: List[str]
    ) -> Dict:
        """Create package manifest."""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "description": description or "Migration package export",
            "tags": tags,
            "components": {
                "config": include_config,
                "recipes": include_recipes,
                "state": include_state,
                "journal": include_journal,
                "stats": include_stats,
                "backups": include_backups
            },
            "files": [],
            "file_count": 0
        }
    
    def _export_config(self, staging_dir: Path) -> List[str]:
        """Export configuration files."""
        exported = []
        config_dir = staging_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Project config
        project_config = self.project_path / ".py2to3.config.json"
        if project_config.exists():
            shutil.copy2(project_config, config_dir / "project_config.json")
            exported.append("config/project_config.json")
        
        # User config (optional)
        user_config = Path.home() / ".py2to3.config.json"
        if user_config.exists():
            shutil.copy2(user_config, config_dir / "user_config.json")
            exported.append("config/user_config.json")
        
        # Todo config
        todo_config = self.project_path / "todo_config.json"
        if todo_config.exists():
            shutil.copy2(todo_config, config_dir / "todo_config.json")
            exported.append("config/todo_config.json")
        
        return exported
    
    def _export_recipes(self, staging_dir: Path) -> List[str]:
        """Export custom recipes."""
        exported = []
        recipes_dir = staging_dir / "recipes"
        recipes_dir.mkdir(exist_ok=True)
        
        # Look for recipes directory
        source_recipes = self.project_path / ".migration_recipes"
        if source_recipes.exists() and source_recipes.is_dir():
            for recipe_file in source_recipes.glob("*.json"):
                shutil.copy2(recipe_file, recipes_dir / recipe_file.name)
                exported.append(f"recipes/{recipe_file.name}")
        
        return exported
    
    def _export_state(self, staging_dir: Path) -> List[str]:
        """Export migration state."""
        exported = []
        state_dir = staging_dir / "state"
        state_dir.mkdir(exist_ok=True)
        
        # Migration state database
        state_db = self.project_path / ".migration_state.json"
        if state_db.exists():
            shutil.copy2(state_db, state_dir / "migration_state.json")
            exported.append("state/migration_state.json")
        
        return exported
    
    def _export_journal(self, staging_dir: Path) -> List[str]:
        """Export journal entries."""
        exported = []
        journal_dir = staging_dir / "journal"
        journal_dir.mkdir(exist_ok=True)
        
        # Journal file
        journal_file = self.project_path / ".migration_journal.json"
        if journal_file.exists():
            shutil.copy2(journal_file, journal_dir / "migration_journal.json")
            exported.append("journal/migration_journal.json")
        
        return exported
    
    def _export_stats(self, staging_dir: Path) -> List[str]:
        """Export statistics snapshots."""
        exported = []
        stats_dir = staging_dir / "stats"
        stats_dir.mkdir(exist_ok=True)
        
        # Stats directory
        source_stats = self.project_path / ".migration_stats"
        if source_stats.exists() and source_stats.is_dir():
            for stat_file in source_stats.glob("*.json"):
                shutil.copy2(stat_file, stats_dir / stat_file.name)
                exported.append(f"stats/{stat_file.name}")
        
        return exported
    
    def _export_backups(
        self,
        staging_dir: Path,
        pattern: Optional[str]
    ) -> List[str]:
        """Export backup files (with optional pattern filtering)."""
        exported = []
        backups_dir = staging_dir / "backups"
        backups_dir.mkdir(exist_ok=True)
        
        # Backups directory
        source_backups = self.project_path / ".py2to3_backups"
        if source_backups.exists() and source_backups.is_dir():
            backup_files = (
                source_backups.glob(f"*{pattern}*") if pattern
                else source_backups.glob("*")
            )
            
            for backup_file in backup_files:
                if backup_file.is_file():
                    shutil.copy2(backup_file, backups_dir / backup_file.name)
                    exported.append(f"backups/{backup_file.name}")
        
        return exported


class MigrationImporter:
    """Import migration packages into a project."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
    
    def import_package(
        self,
        package_path: str,
        import_config: bool = True,
        import_recipes: bool = True,
        import_state: bool = True,
        import_journal: bool = True,
        import_stats: bool = True,
        import_backups: bool = False,
        merge: bool = True,
        dry_run: bool = False
    ) -> Dict:
        """
        Import migration package.
        
        Args:
            package_path: Path to package file
            import_config: Import configuration files
            import_recipes: Import custom recipes
            import_state: Import migration state
            import_journal: Import journal entries
            import_stats: Import statistics snapshots
            import_backups: Import backup files
            merge: Merge with existing data (vs overwrite)
            dry_run: Preview what would be imported without making changes
            
        Returns:
            Import report with details of imported files
        """
        package_path = Path(package_path).resolve()
        
        if not package_path.exists():
            raise FileNotFoundError(f"Package not found: {package_path}")
        
        report = {
            "package": str(package_path),
            "imported_at": datetime.now().isoformat(),
            "dry_run": dry_run,
            "files_imported": [],
            "files_skipped": [],
            "errors": []
        }
        
        # Extract to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(tmpdir)
            
            pkg_dir = Path(tmpdir) / "migration_package"
            
            # Read manifest
            manifest_path = pkg_dir / "manifest.json"
            if not manifest_path.exists():
                raise ValueError("Invalid package: manifest.json not found")
            
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            report["manifest"] = manifest
            
            # Import components
            if import_config:
                self._import_config(pkg_dir, merge, dry_run, report)
            
            if import_recipes:
                self._import_recipes(pkg_dir, merge, dry_run, report)
            
            if import_state:
                self._import_state(pkg_dir, merge, dry_run, report)
            
            if import_journal:
                self._import_journal(pkg_dir, merge, dry_run, report)
            
            if import_stats:
                self._import_stats(pkg_dir, merge, dry_run, report)
            
            if import_backups:
                self._import_backups(pkg_dir, dry_run, report)
        
        return report
    
    def _import_config(
        self,
        pkg_dir: Path,
        merge: bool,
        dry_run: bool,
        report: Dict
    ):
        """Import configuration files."""
        config_dir = pkg_dir / "config"
        if not config_dir.exists():
            return
        
        # Project config
        source = config_dir / "project_config.json"
        if source.exists():
            dest = self.project_path / ".py2to3.config.json"
            if not dry_run:
                if merge and dest.exists():
                    self._merge_json_files(source, dest)
                else:
                    shutil.copy2(source, dest)
            report["files_imported"].append(str(dest))
        
        # Todo config
        source = config_dir / "todo_config.json"
        if source.exists():
            dest = self.project_path / "todo_config.json"
            if not dry_run:
                if merge and dest.exists():
                    self._merge_json_files(source, dest)
                else:
                    shutil.copy2(source, dest)
            report["files_imported"].append(str(dest))
    
    def _import_recipes(
        self,
        pkg_dir: Path,
        merge: bool,
        dry_run: bool,
        report: Dict
    ):
        """Import custom recipes."""
        recipes_dir = pkg_dir / "recipes"
        if not recipes_dir.exists():
            return
        
        dest_dir = self.project_path / ".migration_recipes"
        if not dry_run:
            dest_dir.mkdir(exist_ok=True)
        
        for recipe_file in recipes_dir.glob("*.json"):
            dest = dest_dir / recipe_file.name
            if not dry_run:
                if not merge or not dest.exists():
                    shutil.copy2(recipe_file, dest)
                else:
                    report["files_skipped"].append(
                        f"{dest} (already exists, merge enabled)"
                    )
                    continue
            report["files_imported"].append(str(dest))
    
    def _import_state(
        self,
        pkg_dir: Path,
        merge: bool,
        dry_run: bool,
        report: Dict
    ):
        """Import migration state."""
        state_dir = pkg_dir / "state"
        if not state_dir.exists():
            return
        
        source = state_dir / "migration_state.json"
        if source.exists():
            dest = self.project_path / ".migration_state.json"
            if not dry_run:
                if merge and dest.exists():
                    self._merge_json_files(source, dest)
                else:
                    shutil.copy2(source, dest)
            report["files_imported"].append(str(dest))
    
    def _import_journal(
        self,
        pkg_dir: Path,
        merge: bool,
        dry_run: bool,
        report: Dict
    ):
        """Import journal entries."""
        journal_dir = pkg_dir / "journal"
        if not journal_dir.exists():
            return
        
        source = journal_dir / "migration_journal.json"
        if source.exists():
            dest = self.project_path / ".migration_journal.json"
            if not dry_run:
                if merge and dest.exists():
                    self._merge_journal_files(source, dest)
                else:
                    shutil.copy2(source, dest)
            report["files_imported"].append(str(dest))
    
    def _import_stats(
        self,
        pkg_dir: Path,
        merge: bool,
        dry_run: bool,
        report: Dict
    ):
        """Import statistics snapshots."""
        stats_dir = pkg_dir / "stats"
        if not stats_dir.exists():
            return
        
        dest_dir = self.project_path / ".migration_stats"
        if not dry_run:
            dest_dir.mkdir(exist_ok=True)
        
        for stat_file in stats_dir.glob("*.json"):
            dest = dest_dir / stat_file.name
            if not dry_run:
                if not merge or not dest.exists():
                    shutil.copy2(stat_file, dest)
                else:
                    report["files_skipped"].append(
                        f"{dest} (already exists, merge enabled)"
                    )
                    continue
            report["files_imported"].append(str(dest))
    
    def _import_backups(
        self,
        pkg_dir: Path,
        dry_run: bool,
        report: Dict
    ):
        """Import backup files."""
        backups_dir = pkg_dir / "backups"
        if not backups_dir.exists():
            return
        
        dest_dir = self.project_path / ".py2to3_backups"
        if not dry_run:
            dest_dir.mkdir(exist_ok=True)
        
        for backup_file in backups_dir.glob("*"):
            if backup_file.is_file():
                dest = dest_dir / backup_file.name
                if not dry_run:
                    shutil.copy2(backup_file, dest)
                report["files_imported"].append(str(dest))
    
    def _merge_json_files(self, source: Path, dest: Path):
        """Merge two JSON files."""
        with open(source) as f:
            source_data = json.load(f)
        
        with open(dest) as f:
            dest_data = json.load(f)
        
        # Simple merge strategy: update dest with source
        if isinstance(dest_data, dict) and isinstance(source_data, dict):
            dest_data.update(source_data)
        
        with open(dest, "w") as f:
            json.dump(dest_data, f, indent=2)
    
    def _merge_journal_files(self, source: Path, dest: Path):
        """Merge journal files (append entries)."""
        with open(source) as f:
            source_data = json.load(f)
        
        with open(dest) as f:
            dest_data = json.load(f)
        
        # Append source entries to dest
        if isinstance(dest_data, dict) and isinstance(source_data, dict):
            if "entries" in dest_data and "entries" in source_data:
                dest_data["entries"].extend(source_data["entries"])
        
        with open(dest, "w") as f:
            json.dump(dest_data, f, indent=2)


def list_packages(directory: str = ".") -> List[Dict]:
    """
    List all migration packages in a directory.
    
    Args:
        directory: Directory to search for packages
        
    Returns:
        List of package info dictionaries
    """
    directory = Path(directory)
    packages = []
    
    for package_file in directory.glob("migration_export_*.tar.gz"):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with tarfile.open(package_file, "r:gz") as tar:
                    tar.extractall(tmpdir)
                
                manifest_path = Path(tmpdir) / "migration_package" / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                    
                    packages.append({
                        "file": str(package_file),
                        "size": package_file.stat().st_size,
                        "created_at": manifest.get("created_at"),
                        "description": manifest.get("description"),
                        "tags": manifest.get("tags", []),
                        "file_count": manifest.get("file_count", 0),
                        "components": manifest.get("components", {})
                    })
        except Exception:
            continue
    
    return sorted(packages, key=lambda x: x["created_at"], reverse=True)


if __name__ == "__main__":
    # Example usage
    print("Migration Export/Import Manager")
    print("=" * 50)
    print("\nExport example:")
    print("  exporter = MigrationExporter('.')")
    print("  package = exporter.export_package(")
    print("      include_backups=False,")
    print("      description='My migration template'")
    print("  )")
    print("\nImport example:")
    print("  importer = MigrationImporter('.')")
    print("  report = importer.import_package('migration_export_20240115_120000.tar.gz')")
