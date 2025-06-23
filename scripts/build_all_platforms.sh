#!/bin/bash

# Multi-Platform Docker Build Script for Guest Registration System
# Builds Docker images for all supported processor architectures

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Multi-Platform Docker Build${NC}"
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

print_platform() {
    echo -e "${CYAN}[PLATFORM]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Check arguments
TAG=${1:-"guest-registration:latest"}
PUSH_TO_REGISTRY=${2:-"false"}

# Define all supported platforms
PLATFORMS=(
    "linux/amd64"    # x86_64 architecture (Intel/AMD 64-bit)
    "linux/arm64"    # ARM 64-bit (Apple Silicon, ARM servers)
    "linux/arm/v7"   # ARM 32-bit (Raspberry Pi, ARM devices)
    "linux/arm/v6"   # ARM 32-bit (older Raspberry Pi)
    "linux/386"      # x86 32-bit (Intel/AMD 32-bit)
    "linux/ppc64le"  # PowerPC 64-bit little-endian
    "linux/s390x"    # IBM S390x (mainframe)
    "linux/riscv64"  # RISC-V 64-bit
)

# Platform descriptions for better output
PLATFORM_DESCRIPTIONS=(
    "x86_64 (Intel/AMD 64-bit)"
    "ARM64 (Apple Silicon, ARM servers)"
    "ARMv7 (Raspberry Pi, ARM devices)"
    "ARMv6 (older Raspberry Pi)"
    "x86_32 (Intel/AMD 32-bit)"
    "PowerPC 64-bit little-endian"
    "IBM S390x (mainframe)"
    "RISC-V 64-bit"
)

print_header
print_status "Building Docker images for all supported platforms"
print_status "Tag: $TAG"
print_status "Push to registry: $PUSH_TO_REGISTRY"
echo

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if buildx is available
if ! docker buildx version &> /dev/null; then
    print_warning "Docker Buildx not available, trying to enable..."
    docker buildx create --name multi-platform-builder --use || {
        print_error "Failed to create buildx builder"
        exit 1
    }
fi

# Create or use multi-platform builder
print_status "Setting up multi-platform builder..."
docker buildx create --name multi-platform-builder --use --driver docker-container 2>/dev/null || {
    print_status "Using existing multi-platform builder"
}

# Bootstrap the builder
print_status "Bootstrapping builder..."
docker buildx inspect --bootstrap

echo
print_status "Starting multi-platform build..."

# Build for all platforms
PLATFORM_ARG=""
for i in "${!PLATFORMS[@]}"; do
    platform="${PLATFORMS[$i]}"
    description="${PLATFORM_DESCRIPTIONS[$i]}"
    PLATFORM_ARG="$PLATFORM_ARG,$platform"
    print_platform "Adding $platform ($description)"
done

# Remove leading comma
PLATFORM_ARG="${PLATFORM_ARG#,}"

echo
print_status "Building for platforms: $PLATFORM_ARG"

# Build command
BUILD_CMD="docker buildx build --platform $PLATFORM_ARG --tag $TAG --file Dockerfile"

# Add push flag if requested
if [ "$PUSH_TO_REGISTRY" = "true" ]; then
    BUILD_CMD="$BUILD_CMD --push"
    print_status "Images will be pushed to registry"
else
    BUILD_CMD="$BUILD_CMD --load"
    print_status "Images will be loaded locally (first platform only)"
fi

BUILD_CMD="$BUILD_CMD ."

print_status "Executing: $BUILD_CMD"
echo

# Execute the build
if eval $BUILD_CMD; then
    print_status "✅ Multi-platform Docker build completed successfully!"
    
    if [ "$PUSH_TO_REGISTRY" = "true" ]; then
        print_status "All platform images pushed to registry: $TAG"
    else
        print_status "Local image loaded: $TAG"
        print_warning "Only the first platform (x86_64) is loaded locally"
        print_warning "Use --push flag to push all platforms to registry"
    fi
    
    echo
    print_status "Supported platforms:"
    for i in "${!PLATFORMS[@]}"; do
        platform="${PLATFORMS[$i]}"
        description="${PLATFORM_DESCRIPTIONS[$i]}"
        echo "  ✅ $platform - $description"
    done
    
    echo
    print_status "Usage examples:"
    echo "  # Run locally (x86_64)"
    echo "  docker run -p 8000:8000 $TAG"
    echo ""
    echo "  # Pull specific platform"
    echo "  docker pull --platform linux/arm64 $TAG"
    echo ""
    echo "  # Run on specific platform"
    echo "  docker run --platform linux/arm64 -p 8000:8000 $TAG"
    
else
    print_error "❌ Multi-platform Docker build failed"
    exit 1
fi

echo
print_status "Multi-platform build completed successfully! 🎉" 