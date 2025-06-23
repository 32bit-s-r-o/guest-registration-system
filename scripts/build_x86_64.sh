#!/bin/bash

# x86_64 Docker Build Script for Guest Registration System
# Builds Docker images specifically for x86_64 architecture

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  x86_64 Docker Build Script${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Check arguments
TAG=${1:-"guest-registration:x86_64"}
PLATFORM="linux/amd64"

print_header
print_status "Building x86_64 Docker image"
print_status "Platform: $PLATFORM"
print_status "Tag: $TAG"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if buildx is available
if ! docker buildx version &> /dev/null; then
    print_warning "Docker Buildx not available, trying to enable..."
    docker buildx create --name x86_64-builder --use || {
        print_error "Failed to create buildx builder"
        exit 1
    }
fi

# Build the image
print_status "Starting x86_64 build..."
docker buildx build \
    --platform $PLATFORM \
    --tag $TAG \
    --file Dockerfile \
    --load \
    .

if [ $? -eq 0 ]; then
    print_status "✅ x86_64 Docker image built successfully!"
    
    # Show image info
    print_status "Image information:"
    docker images $TAG
    
    # Show platform info
    print_status "Platform information:"
    docker buildx imagetools inspect $TAG 2>/dev/null || echo "Platform info not available"
    
    print_status "To run the x86_64 image:"
    echo "  docker run -p 8000:8000 $TAG"
    echo ""
    print_status "To push to registry:"
    echo "  docker push $TAG"
    
else
    print_error "❌ x86_64 Docker build failed"
    exit 1
fi

print_status "x86_64 build completed successfully! 🎉" 