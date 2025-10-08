#!/usr/bin/env python3
"""
Virtual Environment Manager for Python 2 to 3 Migration

Helps create, manage, and test Python 3 virtual environments during migration.
Provides isolated environments for testing migrated code and validating dependencies.
"""

import json
import os
import platform
import subprocess
import sys
import venv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class VirtualEnvironmentManager:
    """Manages Python 3 virtual environments for migration testing."""
    
    def __init__(self, base_dir: str = ".py2to3_venvs"):
        """
        Initialize the virtual environment manager.
        
        Args:
            base_dir: Base directory for storing virtual environments
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.state_file = self.base_dir / "venvs.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load virtual environment state from JSON file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"environments": {}}
        return {"environments": {}}
    
    def _save_state(self):
        """Save virtual environment state to JSON file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save state: {e}", file=sys.stderr)
    
    def create(self, name: str, python_version: Optional[str] = None, 
               with_pip: bool = True, system_site_packages: bool = False) -> bool:
        """
        Create a new virtual environment.
        
        Args:
            name: Name of the virtual environment
            python_version: Specific Python version (e.g., "3.8", "3.9")
            with_pip: Whether to install pip in the environment
            system_site_packages: Whether to give access to system site-packages
        
        Returns:
            True if successful, False otherwise
        """
        venv_path = self.base_dir / name
        
        if venv_path.exists():
            print(f"Error: Virtual environment '{name}' already exists")
            return False
        
        print(f"Creating virtual environment '{name}'...")
        
        try:
            # Determine Python executable
            if python_version:
                python_cmd = f"python{python_version}"
                # Check if the specified Python version is available
                try:
                    result = subprocess.run([python_cmd, "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"Error: Python {python_version} not found")
                        return False
                    print(f"Using {result.stdout.strip()}")
                except FileNotFoundError:
                    print(f"Error: Python {python_version} not found")
                    return False
            else:
                python_cmd = sys.executable
            
            # Create the virtual environment
            builder = venv.EnvBuilder(
                system_site_packages=system_site_packages,
                clear=False,
                symlinks=(os.name != 'nt'),
                upgrade=False,
                with_pip=with_pip
            )
            builder.create(str(venv_path))
            
            # Get Python version in the venv
            pip_cmd = self._get_pip_executable(venv_path)
            python_exec = self._get_python_executable(venv_path)
            result = subprocess.run([python_exec, "--version"], 
                                  capture_output=True, text=True)
            py_version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            # Save environment info
            self.state["environments"][name] = {
                "path": str(venv_path),
                "created": datetime.now().isoformat(),
                "python_version": py_version,
                "system_site_packages": system_site_packages,
                "with_pip": with_pip,
                "packages_installed": []
            }
            self._save_state()
            
            print(f"✓ Virtual environment '{name}' created successfully")
            print(f"  Location: {venv_path}")
            print(f"  Python: {py_version}")
            return True
            
        except Exception as e:
            print(f"Error creating virtual environment: {e}", file=sys.stderr)
            return False
    
    def _get_python_executable(self, venv_path: Path) -> str:
        """Get the Python executable path for a virtual environment."""
        if platform.system() == "Windows":
            return str(venv_path / "Scripts" / "python.exe")
        else:
            return str(venv_path / "bin" / "python")
    
    def _get_pip_executable(self, venv_path: Path) -> str:
        """Get the pip executable path for a virtual environment."""
        if platform.system() == "Windows":
            return str(venv_path / "Scripts" / "pip.exe")
        else:
            return str(venv_path / "bin" / "pip")
    
    def _get_activate_script(self, venv_path: Path) -> str:
        """Get the activation script path for a virtual environment."""
        if platform.system() == "Windows":
            return str(venv_path / "Scripts" / "activate.bat")
        else:
            return str(venv_path / "bin" / "activate")
    
    def install_requirements(self, name: str, requirements_file: str) -> bool:
        """
        Install packages from requirements file into a virtual environment.
        
        Args:
            name: Name of the virtual environment
            requirements_file: Path to requirements.txt file
        
        Returns:
            True if successful, False otherwise
        """
        if name not in self.state["environments"]:
            print(f"Error: Virtual environment '{name}' not found")
            return False
        
        venv_path = Path(self.state["environments"][name]["path"])
        if not venv_path.exists():
            print(f"Error: Virtual environment path does not exist: {venv_path}")
            return False
        
        if not os.path.exists(requirements_file):
            print(f"Error: Requirements file not found: {requirements_file}")
            return False
        
        pip_cmd = self._get_pip_executable(venv_path)
        
        print(f"Installing packages from {requirements_file} into '{name}'...")
        
        try:
            result = subprocess.run(
                [pip_cmd, "install", "-r", requirements_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Packages installed successfully")
                # Update state with installed packages
                self._update_installed_packages(name, venv_path)
                return True
            else:
                print(f"Error installing packages:\n{result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
    
    def install_package(self, name: str, package: str) -> bool:
        """
        Install a single package into a virtual environment.
        
        Args:
            name: Name of the virtual environment
            package: Package name (can include version, e.g., "numpy==1.19.0")
        
        Returns:
            True if successful, False otherwise
        """
        if name not in self.state["environments"]:
            print(f"Error: Virtual environment '{name}' not found")
            return False
        
        venv_path = Path(self.state["environments"][name]["path"])
        if not venv_path.exists():
            print(f"Error: Virtual environment path does not exist: {venv_path}")
            return False
        
        pip_cmd = self._get_pip_executable(venv_path)
        
        print(f"Installing {package} into '{name}'...")
        
        try:
            result = subprocess.run(
                [pip_cmd, "install", package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ {package} installed successfully")
                self._update_installed_packages(name, venv_path)
                return True
            else:
                print(f"Error installing package:\n{result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
    
    def _update_installed_packages(self, name: str, venv_path: Path):
        """Update the list of installed packages in state."""
        pip_cmd = self._get_pip_executable(venv_path)
        
        try:
            result = subprocess.run(
                [pip_cmd, "freeze"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                packages = [line.strip() for line in result.stdout.split('\n') 
                           if line.strip() and not line.startswith('#')]
                self.state["environments"][name]["packages_installed"] = packages
                self.state["environments"][name]["last_updated"] = datetime.now().isoformat()
                self._save_state()
        except Exception:
            pass
    
    def list_environments(self) -> List[Dict]:
        """
        List all managed virtual environments.
        
        Returns:
            List of environment information dictionaries
        """
        environments = []
        for name, info in self.state["environments"].items():
            venv_path = Path(info["path"])
            exists = venv_path.exists()
            
            env_info = {
                "name": name,
                "path": info["path"],
                "exists": exists,
                "created": info.get("created", "Unknown"),
                "python_version": info.get("python_version", "Unknown"),
                "package_count": len(info.get("packages_installed", []))
            }
            environments.append(env_info)
        
        return environments
    
    def remove(self, name: str, force: bool = False) -> bool:
        """
        Remove a virtual environment.
        
        Args:
            name: Name of the virtual environment
            force: Force removal without confirmation
        
        Returns:
            True if successful, False otherwise
        """
        if name not in self.state["environments"]:
            print(f"Error: Virtual environment '{name}' not found")
            return False
        
        venv_path = Path(self.state["environments"][name]["path"])
        
        if not force:
            response = input(f"Remove virtual environment '{name}'? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled")
                return False
        
        print(f"Removing virtual environment '{name}'...")
        
        try:
            # Remove the directory
            if venv_path.exists():
                import shutil
                shutil.rmtree(venv_path)
            
            # Remove from state
            del self.state["environments"][name]
            self._save_state()
            
            print(f"✓ Virtual environment '{name}' removed successfully")
            return True
            
        except Exception as e:
            print(f"Error removing virtual environment: {e}", file=sys.stderr)
            return False
    
    def run_command(self, name: str, command: List[str]) -> bool:
        """
        Run a command in a virtual environment.
        
        Args:
            name: Name of the virtual environment
            command: Command to run as a list of strings
        
        Returns:
            True if command succeeded, False otherwise
        """
        if name not in self.state["environments"]:
            print(f"Error: Virtual environment '{name}' not found")
            return False
        
        venv_path = Path(self.state["environments"][name]["path"])
        if not venv_path.exists():
            print(f"Error: Virtual environment path does not exist: {venv_path}")
            return False
        
        python_cmd = self._get_python_executable(venv_path)
        
        try:
            result = subprocess.run(
                [python_cmd] + command,
                cwd=os.getcwd()
            )
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error running command: {e}", file=sys.stderr)
            return False
    
    def run_tests(self, name: str, test_path: Optional[str] = None) -> bool:
        """
        Run pytest tests in a virtual environment.
        
        Args:
            name: Name of the virtual environment
            test_path: Optional path to tests (defaults to 'tests')
        
        Returns:
            True if tests passed, False otherwise
        """
        if name not in self.state["environments"]:
            print(f"Error: Virtual environment '{name}' not found")
            return False
        
        venv_path = Path(self.state["environments"][name]["path"])
        if not venv_path.exists():
            print(f"Error: Virtual environment path does not exist: {venv_path}")
            return False
        
        python_cmd = self._get_python_executable(venv_path)
        test_path = test_path or "tests"
        
        print(f"Running tests in '{name}'...")
        
        try:
            # First, check if pytest is installed
            result = subprocess.run(
                [python_cmd, "-m", "pytest", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("pytest not found in environment. Installing pytest...")
                pip_cmd = self._get_pip_executable(venv_path)
                subprocess.run([pip_cmd, "install", "pytest"], check=True)
            
            # Run tests
            result = subprocess.run(
                [python_cmd, "-m", "pytest", test_path, "-v"],
                cwd=os.getcwd()
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error running tests: {e}", file=sys.stderr)
            return False
    
    def get_info(self, name: str) -> Optional[Dict]:
        """
        Get detailed information about a virtual environment.
        
        Args:
            name: Name of the virtual environment
        
        Returns:
            Environment information dictionary or None if not found
        """
        if name not in self.state["environments"]:
            return None
        
        info = self.state["environments"][name].copy()
        venv_path = Path(info["path"])
        info["exists"] = venv_path.exists()
        
        return info
    
    def print_activation_command(self, name: str):
        """
        Print the command to activate a virtual environment.
        
        Args:
            name: Name of the virtual environment
        """
        if name not in self.state["environments"]:
            print(f"Error: Virtual environment '{name}' not found")
            return
        
        venv_path = Path(self.state["environments"][name]["path"])
        
        if not venv_path.exists():
            print(f"Error: Virtual environment path does not exist: {venv_path}")
            return
        
        if platform.system() == "Windows":
            activate_cmd = str(venv_path / "Scripts" / "activate.bat")
            print(f"\nTo activate this environment, run:")
            print(f"  {activate_cmd}")
        else:
            activate_cmd = str(venv_path / "bin" / "activate")
            print(f"\nTo activate this environment, run:")
            print(f"  source {activate_cmd}")


def main():
    """Main entry point for standalone testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Virtual Environment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a virtual environment")
    create_parser.add_argument("name", help="Name of the environment")
    create_parser.add_argument("--python", help="Python version (e.g., 3.8)")
    create_parser.add_argument("--system-site-packages", action="store_true",
                             help="Give access to system site-packages")
    
    # List command
    subparsers.add_parser("list", help="List all virtual environments")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a virtual environment")
    remove_parser.add_argument("name", help="Name of the environment")
    remove_parser.add_argument("--force", action="store_true", help="Force removal")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install packages")
    install_parser.add_argument("name", help="Name of the environment")
    install_parser.add_argument("-r", "--requirements", help="Requirements file")
    install_parser.add_argument("-p", "--package", help="Single package to install")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get environment info")
    info_parser.add_argument("name", help="Name of the environment")
    
    args = parser.parse_args()
    
    manager = VirtualEnvironmentManager()
    
    if args.command == "create":
        manager.create(args.name, args.python, system_site_packages=args.system_site_packages)
    elif args.command == "list":
        envs = manager.list_environments()
        if not envs:
            print("No virtual environments found")
        else:
            print("\nVirtual Environments:")
            for env in envs:
                status = "✓" if env["exists"] else "✗"
                print(f"  {status} {env['name']}")
                print(f"      Path: {env['path']}")
                print(f"      Python: {env['python_version']}")
                print(f"      Packages: {env['package_count']}")
                print()
    elif args.command == "remove":
        manager.remove(args.name, args.force)
    elif args.command == "install":
        if args.requirements:
            manager.install_requirements(args.name, args.requirements)
        elif args.package:
            manager.install_package(args.name, args.package)
        else:
            print("Error: Specify --requirements or --package")
    elif args.command == "info":
        info = manager.get_info(args.name)
        if info:
            print(f"\nVirtual Environment: {args.name}")
            print(f"  Path: {info['path']}")
            print(f"  Exists: {info['exists']}")
            print(f"  Created: {info.get('created', 'Unknown')}")
            print(f"  Python: {info.get('python_version', 'Unknown')}")
            print(f"  Packages: {len(info.get('packages_installed', []))}")
            if info.get('packages_installed'):
                print(f"\n  Installed packages:")
                for pkg in info['packages_installed'][:10]:
                    print(f"    - {pkg}")
                if len(info['packages_installed']) > 10:
                    print(f"    ... and {len(info['packages_installed']) - 10} more")
        else:
            print(f"Environment '{args.name}' not found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
