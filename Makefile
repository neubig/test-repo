# Makefile for Python 2 to 3 Migration Toolkit
# Common tasks for developers and users

.PHONY: help install install-dev setup test test-cov clean lint format check-format demo docs

# Default target
help:
	@echo "Python 2 to 3 Migration Toolkit - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install         Install production dependencies"
	@echo "  make install-dev     Install development dependencies"
	@echo "  make setup           Run interactive setup script"
	@echo "  make test            Run test suite"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make lint            Run code linters (flake8, pylint)"
	@echo "  make format          Format code with black"
	@echo "  make check-format    Check code formatting without changes"
	@echo "  make clean           Remove generated files and caches"
	@echo "  make demo            Run a quick demo migration"
	@echo "  make docs            Generate documentation"
	@echo ""
	@echo "Quick start:"
	@echo "  1. make setup        # Interactive setup"
	@echo "  2. make test         # Run tests"
	@echo "  3. ./py2to3 wizard   # Start guided migration"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt
	@echo "✓ Development dependencies installed"

# Run setup script
setup:
	@./setup.sh

# Run tests
test:
	@echo "Running test suite..."
	pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo ""
	@echo "✓ Coverage report generated in htmlcov/index.html"

# Run linters
lint:
	@echo "Running flake8..."
	-flake8 src/ tests/ --max-line-length=120 --exclude=__pycache__
	@echo ""
	@echo "Running pylint..."
	-pylint src/ --max-line-length=120

# Format code with black
format:
	@echo "Formatting code with black..."
	black src/ tests/ --line-length=120
	@echo "✓ Code formatted"

# Check formatting without making changes
check-format:
	@echo "Checking code formatting..."
	black src/ tests/ --check --line-length=120

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/
	@echo "✓ Cleaned generated files"

# Run a quick demo
demo:
	@echo "Running quick demo..."
	@echo ""
	@echo "1. Checking Python 3 compatibility..."
	./py2to3 check src/core/ --report demo_check.txt || true
	@echo ""
	@echo "2. Running preflight checks..."
	./py2to3 preflight src/ || true
	@echo ""
	@echo "3. Checking migration status..."
	./py2to3 status || true
	@echo ""
	@echo "✓ Demo complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  - Run './py2to3 wizard' for guided migration"
	@echo "  - Run './py2to3 --help' to see all commands"

# Generate documentation
docs:
	@echo "Generating documentation..."
	@if [ -d "docs" ]; then \
		cd docs && make html; \
		echo "✓ Documentation generated in docs/_build/html/"; \
	else \
		echo "Documentation directory not found"; \
	fi

# Quick check - runs basic validation
check: check-format lint test
	@echo ""
	@echo "✓ All checks passed!"

# Full setup for development
dev-setup: install-dev
	@echo "Setting up development environment..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
		echo "✓ Pre-commit hooks installed"; \
	fi
	@echo "✓ Development environment ready"

# Show project info
info:
	@echo "Python 2 to 3 Migration Toolkit"
	@echo "================================"
	@echo ""
	@echo "Python version: $$(python3 --version)"
	@echo "Pip version: $$(pip --version)"
	@echo ""
	@echo "Project structure:"
	@echo "  - src/          Python migration tools"
	@echo "  - tests/        Test suite"
	@echo "  - my-vite-app/  Web application (React + TypeScript)"
	@echo ""
	@echo "Entry point: ./py2to3"
	@echo ""
	@echo "Documentation:"
	@echo "  - README.md"
	@echo "  - CLI_GUIDE.md"
	@echo "  - WIZARD_GUIDE.md"
	@echo "  - And many more guide files..."
