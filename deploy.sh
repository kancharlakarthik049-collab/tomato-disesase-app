#!/bin/bash
# Tomato Disease Identification - Deployment Script for Render
# Automates preparation and Git operations for Render deployment
# Usage: ./deploy.sh [--force]

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE_DEPLOY=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
if [ "$1" == "--force" ]; then
    FORCE_DEPLOY=true
fi

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}🚀 Tomato Disease Identification - Render Deployment${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo -e "${BLUE}📌 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

check_file_exists() {
    if [ ! -f "$1" ]; then
        print_error "Missing $1"
        return 1
    fi
    print_success "Found $1"
    return 0
}

check_directory_exists() {
    if [ ! -d "$1" ]; then
        print_error "Missing directory $1"
        return 1
    fi
    print_success "Found directory $1"
    return 0
}

# Main script
print_header

# Step 1: Validate project structure
print_section "Step 1: Validating Project Structure"
echo ""

missing_files=0

# Check critical files
critical_files=(
    "requirements.txt"
    "runtime.txt"
    "Procfile"
    "render.yaml"
    ".gitignore"
    ".gitattributes"
    "app.py"
)

for file in "${critical_files[@]}"; do
    if ! check_file_exists "$file"; then
        missing_files=$((missing_files + 1))
    fi
done

# Check critical directories
critical_dirs=(
    "templates"
    "static"
    "models"
)

for dir in "${critical_dirs[@]}"; do
    if ! check_directory_exists "$dir"; then
        missing_files=$((missing_files + 1))
    fi
done

echo ""

if [ $missing_files -gt 0 ]; then
    print_error "$missing_files critical files/directories are missing"
    echo ""
    echo "Required files:"
    echo "  - requirements.txt"
    echo "  - runtime.txt"
    echo "  - Procfile"
    echo "  - render.yaml"
    echo "  - .gitignore"
    echo "  - app.py"
    echo ""
    echo "Required directories:"
    echo "  - templates/"
    echo "  - static/"
    echo "  - models/"
    echo ""
    exit 1
fi

print_success "All critical files and directories present"
echo ""

# Step 2: Check Git status
print_section "Step 2: Checking Git Status"
echo ""

if ! command -v git &> /dev/null; then
    print_error "Git is not installed"
    exit 1
fi

print_success "Git is installed"

# Check if we're in a git repository
if [ ! -d .git ]; then
    print_warning "Not a Git repository. Initializing..."
    git init
    git add .
fi

# Get git status
git_status=$(git status --porcelain 2>/dev/null || echo "")

if [ -z "$git_status" ]; then
    print_success "No uncommitted changes"
else
    echo -e "${YELLOW}Uncommitted changes detected:${NC}"
    git status --short | head -20
fi

echo ""

# Step 3: Validate deployment configuration
print_section "Step 3: Validating Deployment Configuration"
echo ""

# Check Procfile
if grep -q "gunicorn" Procfile; then
    print_success "Procfile configured with Gunicorn"
else
    print_error "Procfile missing Gunicorn configuration"
fi

# Check render.yaml
if grep -q "type: web" render.yaml; then
    print_success "render.yaml configured correctly"
else
    print_error "render.yaml missing 'type: web'"
fi

# Check runtime.txt
if grep -q "python-" runtime.txt; then
    python_version=$(head -1 runtime.txt)
    print_success "runtime.txt: $python_version"
else
    print_error "runtime.txt missing Python version"
fi

echo ""

# Step 4: Confirm deployment
if [ "$FORCE_DEPLOY" = false ]; then
    print_section "Ready for Deployment"
    echo ""
    echo "Project is ready to deploy to Render."
    echo ""
    read -p "Commit and push to GitHub? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Cancelled"
        exit 0
    fi
fi

# Step 5: Commit and push
print_section "Step 5: Git Commit and Push"
echo ""

# Stage files
echo "Staging deployment files..."
git add requirements.txt runtime.txt Procfile render.yaml .gitignore .gitattributes app.py
git add templates/ static/ .github/ 2>/dev/null || true
git add RENDER_DEPLOYMENT_GUIDE.md PRODUCTION_DEPLOYMENT_SUMMARY.md GIT_LFS_GUIDE.md 2>/dev/null || true

# Create commit
commit_msg="🚀 Configure for Render deployment: Gunicorn (gthread), Flask prod config, Git LFS, guides"

if git diff --cached --quiet; then
    print_success "No new changes to commit"
else
    git commit -m "$commit_msg"
    print_success "Committed changes"
fi

# Push to GitHub
current_branch=$(git rev-parse --abbrev-ref HEAD)
print_success "Pushing to GitHub ($current_branch)..."
git push origin "$current_branch"

print_success "Pushed to GitHub"
echo ""

# Summary
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
print_section "🎉 Deployment Ready!"
echo ""
echo "📌 Next Steps:"
echo "1. Go to: https://render.com/dashboard"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Select your GitHub repository"
echo "4. Render will auto-detect render.yaml"
echo "5. Click 'Create Web Service'"
echo ""
echo "⏱️  Deployment time: ~2-3 minutes"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

