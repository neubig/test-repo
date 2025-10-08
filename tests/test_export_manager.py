import pytest
import tempfile
import shutil
from pathlib import Path
import json
import tarfile
from src.export_manager import ExportManager


class TestExportManager:
    """Test ExportManager functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    @pytest.fixture
    def project_dir(self, temp_dir):
        """Create a project directory with sample files."""
        project = temp_dir / "project"
        project.mkdir()
        
        # Create config
        config = {"version": "1.0", "test": True}
        (project / ".py2to3.config.json").write_text(json.dumps(config))
        
        # Create recipes directory
        recipes_dir = project / ".py2to3" / "recipes"
        recipes_dir.mkdir(parents=True)
        (recipes_dir / "custom.json").write_text(json.dumps({"name": "custom_recipe"}))
        
        # Create state
        state_dir = project / ".py2to3"
        (state_dir / "migration_state.json").write_text(json.dumps({"files": {}}))
        
        # Create journal
        (state_dir / "journal.json").write_text(json.dumps({"entries": []}))
        
        # Create stats
        stats_dir = state_dir / "stats"
        stats_dir.mkdir()
        (stats_dir / "snapshot.json").write_text(json.dumps({"timestamp": "2024-01-01"}))
        
        return project

    def test_create_export_basic(self, project_dir, temp_dir):
        """Test basic export creation."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        result = manager.create_export(
            output_path=str(output_file),
            description="Test export"
        )
        
        assert Path(result).exists()
        assert tarfile.is_tarfile(result)

    def test_create_export_with_components(self, project_dir, temp_dir):
        """Test export with specific components."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        result = manager.create_export(
            output_path=str(output_file),
            include_config=True,
            include_recipes=True,
            include_state=False,
            include_journal=False,
            include_stats=False
        )
        
        assert Path(result).exists()
        
        # Verify manifest
        with tarfile.open(result, "r:gz") as tar:
            manifest_member = tar.getmember("migration_package/manifest.json")
            manifest_file = tar.extractfile(manifest_member)
            manifest = json.loads(manifest_file.read().decode('utf-8'))
            
            assert manifest["components"]["config"] is True
            assert manifest["components"]["recipes"] is True
            assert manifest["components"]["state"] is False

    def test_create_export_with_tags(self, project_dir, temp_dir):
        """Test export with description and tags."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        result = manager.create_export(
            output_path=str(output_file),
            description="Test migration",
            tags=["test", "demo"]
        )
        
        with tarfile.open(result, "r:gz") as tar:
            manifest_member = tar.getmember("migration_package/manifest.json")
            manifest_file = tar.extractfile(manifest_member)
            manifest = json.loads(manifest_file.read().decode('utf-8'))
            
            assert manifest["description"] == "Test migration"
            assert "test" in manifest["tags"]
            assert "demo" in manifest["tags"]

    def test_list_packages(self, temp_dir, project_dir):
        """Test listing migration packages."""
        manager = ExportManager(project_dir)
        
        # Create a couple of packages
        output1 = temp_dir / "migration_export_test1.tar.gz"
        manager.create_export(
            output_path=str(output1),
            description="Package 1"
        )
        
        output2 = temp_dir / "migration_export_test2.tar.gz"
        manager.create_export(
            output_path=str(output2),
            description="Package 2"
        )
        
        # List packages
        packages = manager.list_packages(str(temp_dir))
        
        assert len(packages) == 2
        assert all("file" in pkg for pkg in packages)
        assert all("created_at" in pkg for pkg in packages)
        assert all("description" in pkg for pkg in packages)

    def test_import_package(self, project_dir, temp_dir):
        """Test importing a package."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        # Create export
        package_path = manager.create_export(
            output_path=str(output_file),
            description="Test import"
        )
        
        # Create new import directory
        import_dir = temp_dir / "import_test"
        import_dir.mkdir()
        
        # Import package
        imported_files = manager.import_package(
            package_path=package_path,
            target_path=str(import_dir)
        )
        
        assert len(imported_files) > 0
        assert (import_dir / ".py2to3.config.json").exists()

    def test_import_package_dry_run(self, project_dir, temp_dir):
        """Test importing a package in dry-run mode."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        # Create export
        package_path = manager.create_export(
            output_path=str(output_file),
            description="Test dry run"
        )
        
        # Create new import directory
        import_dir = temp_dir / "import_test"
        import_dir.mkdir()
        
        # Import package in dry-run mode
        imported_files = manager.import_package(
            package_path=package_path,
            target_path=str(import_dir),
            dry_run=True
        )
        
        assert len(imported_files) > 0
        # In dry-run mode, files should not be created
        assert not (import_dir / ".py2to3.config.json").exists()

    def test_import_package_selective(self, project_dir, temp_dir):
        """Test importing only selected components."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        # Create export
        package_path = manager.create_export(
            output_path=str(output_file),
            description="Test selective import"
        )
        
        # Create new import directory
        import_dir = temp_dir / "import_test"
        import_dir.mkdir()
        
        # Import only config
        imported_files = manager.import_package(
            package_path=package_path,
            target_path=str(import_dir),
            import_config=True,
            import_recipes=False,
            import_state=False,
            import_journal=False,
            import_stats=False
        )
        
        assert (import_dir / ".py2to3.config.json").exists()
        assert not (import_dir / ".py2to3" / "migration_state.json").exists()

    def test_create_export_no_config(self, temp_dir):
        """Test export when no config exists."""
        project = temp_dir / "empty_project"
        project.mkdir()
        
        manager = ExportManager(project)
        output_file = temp_dir / "test_export.tar.gz"
        
        # Should still create package even without config
        result = manager.create_export(
            output_path=str(output_file),
            description="Empty project"
        )
        
        assert Path(result).exists()

    def test_inspect_package(self, project_dir, temp_dir):
        """Test inspecting a package."""
        manager = ExportManager(project_dir)
        output_file = temp_dir / "test_export.tar.gz"
        
        # Create export
        package_path = manager.create_export(
            output_path=str(output_file),
            description="Test inspection",
            tags=["test"]
        )
        
        # Inspect package
        manifest = manager.inspect_package(package_path)
        
        assert manifest is not None
        assert manifest["description"] == "Test inspection"
        assert "test" in manifest["tags"]
        assert "components" in manifest
        assert manifest["file_count"] > 0
