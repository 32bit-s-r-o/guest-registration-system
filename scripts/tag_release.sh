#!/bin/bash

# Release Tagging Script for Guest Registration System
# Usage: ./scripts/tag_release.sh <version> <commit_hash> <description>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Release Tagging Script${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Check arguments
if [ $# -lt 3 ]; then
    print_error "Usage: $0 <version> <commit_hash> <description>"
    echo "Example: $0 v1.9.0 abc1234 'Release v1.9.0 - New Feature'"
    exit 1
fi

VERSION=$1
COMMIT_HASH=$2
DESCRIPTION=$3

print_header
print_status "Creating release tag: $VERSION"
print_status "Commit: $COMMIT_HASH"
print_status "Description: $DESCRIPTION"

# Validate version format
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format. Use format: vX.Y.Z"
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$VERSION$"; then
    print_warning "Tag $VERSION already exists!"
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deleting existing tag $VERSION"
        git tag -d "$VERSION"
    else
        print_error "Tag creation cancelled"
        exit 1
    fi
fi

# Validate commit hash
if ! git rev-parse --verify "$COMMIT_HASH" >/dev/null 2>&1; then
    print_error "Invalid commit hash: $COMMIT_HASH"
    exit 1
fi

# Create the tag
print_status "Creating annotated tag..."
git tag -a "$VERSION" -m "$DESCRIPTION" "$COMMIT_HASH"

# Verify the tag was created
if git tag -l | grep -q "^$VERSION$"; then
    print_status "✅ Tag $VERSION created successfully!"
else
    print_error "❌ Failed to create tag $VERSION"
    exit 1
fi

# Show tag information
print_status "Tag information:"
git show "$VERSION" --no-patch --format="Tag: %(refname:short)%0aCommit: %(objectname)%0aAuthor: %(taggername) <%(taggeremail)>%0aDate: %(taggerdate)%0aMessage: %(contents:subject)"

# Show recent tags
print_status "Recent tags:"
git tag -n | tail -5

print_status "To push tags to remote:"
echo "  git push origin $VERSION"
echo "  git push origin --tags"

print_status "To create a GitHub release:"
echo "  Visit: https://github.com/your-repo/releases/new"
echo "  Tag: $VERSION"
echo "  Title: $DESCRIPTION"

print_status "Release tagging completed successfully! 🎉" 