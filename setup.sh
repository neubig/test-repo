#!/usr/bin/env bash
#
# Quick Setup Script for Python 2 to 3 Migration Toolkit
#
# This script automates the setup process:
# - Checks Python version
# - Creates a virtual environment (optional)
# - Installs dependencies
# - Validates the installation
# - Runs a quick demo
#
# Usage:
#   ./setup.sh              # Install with automatic venv
#   ./setup.sh --no-venv    # Install without venv
#   ./setup.sh --dev        # Install with development dependencies
#   ./setup.sh --help       # Show help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
USE_VENV=true
INSTALL_DEV=false
VENV_DIR="venv"
PYTHON_CMD="python3"

# Functions
print_header() {
    echo -e "\n${BOLD}${MAGENTA}================================${NC}"
    echo -e "${BOLD}${MAGENTA}$1${NC}"
    echo -e "${BOLD}${MAGENTA}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_step() {
    echo -e "\n${BOLD}${BLUE}▶${NC} $1${NC}"
}

show_help() {
    cat << EOF
${BOLD}Python 2 to 3 Migration Toolkit - Setup Script${NC}

${BOLD}USAGE:${NC}
    ./setup.sh [OPTIONS]

${BOLD}OPTIONS:${NC}
    --no-venv           Skip virtual environment creation
    --dev               Install development dependencies
    --venv-dir DIR      Specify virtual environment directory (default: venv)
    --python PYTHON     Specify Python command (default: python3)
    -h, --help          Show this help message

${BOLD}EXAMPLES:${NC}
    ./setup.sh                      # Standard installation with venv
    ./setup.sh --dev                # Install with dev dependencies
    ./setup.sh --no-venv            # Install without venv (global)
    ./setup.sh --venv-dir .venv     # Use .venv directory

${BOLD}DESCRIPTION:${NC}
    This script automates the setup of the Python 2 to 3 Migration Toolkit.
    It will:
    - Check your Python version (requires Python 3.6+)
    - Create a virtual environment (unless --no-venv is specified)
    - Install all required dependencies
    - Validate the installation
    - Run a quick demo to verify everything works

EOF
    exit 0
}

check_python_version() {
    print_step "Checking Python version..."
    
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.6 or later."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 6 ]); then
        print_error "Python 3.6+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected"
}

create_venv() {
    if [ "$USE_VENV" = false ]; then
        print_info "Skipping virtual environment creation"
        return
    fi
    
    print_step "Creating virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Remove and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
    
    # Activate the virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

install_dependencies() {
    print_step "Installing dependencies..."
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install dependencies
    if [ "$INSTALL_DEV" = true ]; then
        print_info "Installing production and development dependencies..."
        pip install -r requirements-dev.txt
    else
        print_info "Installing production dependencies..."
        pip install -r requirements.txt
    fi
    
    print_success "Dependencies installed successfully"
}

validate_installation() {
    print_step "Validating installation..."
    
    # Check if py2to3 script exists
    if [ ! -f "py2to3" ]; then
        print_error "py2to3 script not found"
        return 1
    fi
    
    # Make sure it's executable
    chmod +x py2to3
    print_success "py2to3 script is executable"
    
    # Test basic imports
    print_info "Testing imports..."
    $PYTHON_CMD -c "import chardet; import json; import os; import sys" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Core dependencies are working"
    else
        print_warning "Some dependencies may not be properly installed"
    fi
}

run_quick_demo() {
    print_step "Running quick demo..."
    
    # Check if there are Python files to analyze
    if [ -d "src" ]; then
        print_info "Running preflight check on src/ directory..."
        ./py2to3 preflight src/ 2>/dev/null || true
        print_success "Demo completed"
    else
        print_info "No src/ directory found, skipping demo"
    fi
}

show_next_steps() {
    print_header "Setup Complete!"
    
    echo -e "${BOLD}Next Steps:${NC}\n"
    
    if [ "$USE_VENV" = true ]; then
        echo -e "  ${BOLD}1.${NC} Activate the virtual environment:"
        echo -e "     ${CYAN}source $VENV_DIR/bin/activate${NC}"
        echo ""
    fi
    
    echo -e "  ${BOLD}2.${NC} Run the wizard for guided migration:"
    echo -e "     ${CYAN}./py2to3 wizard${NC}"
    echo ""
    
    echo -e "  ${BOLD}3.${NC} Or check your code for Python 3 compatibility:"
    echo -e "     ${CYAN}./py2to3 check <path>${NC}"
    echo ""
    
    echo -e "  ${BOLD}4.${NC} View all available commands:"
    echo -e "     ${CYAN}./py2to3 --help${NC}"
    echo ""
    
    echo -e "${BOLD}Documentation:${NC}"
    echo -e "  • README.md - Project overview"
    echo -e "  • CLI_GUIDE.md - Complete CLI reference"
    echo -e "  • WIZARD_GUIDE.md - Guided migration workflow"
    echo ""
    
    echo -e "${BOLD}Quick Examples:${NC}"
    echo -e "  ${CYAN}./py2to3 wizard${NC}              # Interactive guided migration"
    echo -e "  ${CYAN}./py2to3 check src/${NC}          # Check Python 3 compatibility"
    echo -e "  ${CYAN}./py2to3 fix src/ --backup${NC}   # Apply fixes with backup"
    echo -e "  ${CYAN}./py2to3 status${NC}               # Show migration progress"
    echo ""
    
    print_success "Ready to start migrating! 🚀"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-venv)
            USE_VENV=false
            shift
            ;;
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --venv-dir)
            VENV_DIR="$2"
            shift 2
            ;;
        --python)
            PYTHON_CMD="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header "Python 2 to 3 Migration Toolkit Setup"
    
    print_info "Configuration:"
    echo "  • Python: $PYTHON_CMD"
    echo "  • Use venv: $USE_VENV"
    if [ "$USE_VENV" = true ]; then
        echo "  • Venv directory: $VENV_DIR"
    fi
    echo "  • Install dev dependencies: $INSTALL_DEV"
    
    check_python_version
    create_venv
    install_dependencies
    validate_installation
    run_quick_demo
    show_next_steps
    
    echo -e "\n${GREEN}${BOLD}✓ Setup completed successfully!${NC}\n"
}

# Run main function
main
