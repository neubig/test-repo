#!/usr/bin/env python3
"""
Setup script for py2to3 CLI tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="py2to3-toolkit",
    version="1.0.0",
    author="Python Migration Team",
    author_email="team@example.com",
    description="Comprehensive toolkit for Python 2 to Python 3 migration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/test-repo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "py2to3=cli:main",
        ],
    },
    install_requires=[
        "chardet>=4.0.0",  # Required for encoding detection
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    keywords="python2 python3 migration refactoring modernization",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/test-repo/issues",
        "Source": "https://github.com/yourusername/test-repo",
    },
)
