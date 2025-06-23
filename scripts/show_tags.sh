#!/bin/bash

# Show Tags Script for Guest Registration System
# Displays current tag information and status

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Current Git Tags${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}[ERROR]${NC} This script must be run from the project root directory"
    exit 1
fi

print_header

# Show all tags with descriptions
echo -e "${GREEN}All Tags:${NC}"
git tag -n

echo

# Show tags in chronological order
echo -e "${GREEN}Tags by Version:${NC}"
git tag --sort=version:refname -n

echo

# Show latest tag
LATEST_TAG=$(git tag --sort=version:refname | tail -1)
if [ -n "$LATEST_TAG" ]; then
    echo -e "${GREEN}Latest Tag:${NC} $LATEST_TAG"
    echo -e "${GREEN}Latest Tag Details:${NC}"
    git show "$LATEST_TAG" --no-patch --format="  Commit: %(objectname)%0a  Author: %(taggername) <%(taggeremail)>%0a  Date: %(taggerdate)%0a  Message: %(contents:subject)"
else
    print_warning "No tags found"
fi

echo

# Check if tags are pushed to remote
print_status "Checking remote tags..."
REMOTE_TAGS=$(git ls-remote --tags origin 2>/dev/null | cut -f2 | sed 's/refs\/tags\///' || echo "")
if [ -n "$REMOTE_TAGS" ]; then
    echo -e "${GREEN}Remote Tags:${NC}"
    echo "$REMOTE_TAGS" | sort -V
else
    print_warning "No remote tags found or unable to fetch"
fi

echo

print_status "Tag management commands:"
echo "  List tags: git tag -l"
echo "  Show tag details: git show <tag>"
echo "  Push tags: git push origin --tags"
echo "  Create new tag: ./scripts/tag_release.sh <version> <commit> <description>"

print_status "Tag display completed! 🏷️" 