# Scripts Directory

This directory contains utility scripts for managing the Guest Registration System.

## Available Scripts

### Tag Management

#### `tag_release.sh`
**Purpose**: Create Git tags for releases with validation and automation.

**Usage**:
```bash
./scripts/tag_release.sh <version> <commit_hash> <description>
```

**Example**:
```bash
./scripts/tag_release.sh v1.9.0 abc1234 "Release v1.9.0 - Enhanced Reporting"
```

**Features**:
- Version format validation (vX.Y.Z)
- Commit hash verification
- Duplicate tag detection
- Colored output
- Helpful instructions for next steps

#### `show_tags.sh`
**Purpose**: Display current Git tag information and status.

**Usage**:
```bash
./scripts/show_tags.sh
```

**Features**:
- Lists all tags with descriptions
- Shows tags in chronological order
- Displays latest tag details
- Checks remote tag status
- Provides helpful commands

## Script Requirements

All scripts require:
- Bash shell
- Git repository
- Project root directory (must contain `app.py`)

## Usage Examples

### View Current Tags
```bash
# Show all tag information
./scripts/show_tags.sh

# List tags manually
git tag -l
git tag -n
```

### Create a New Release Tag
```bash
# Get the commit hash for the release
git log --oneline -1

# Create the tag (replace with actual values)
./scripts/tag_release.sh v1.9.0 abc1234 "Release v1.9.0 - New Feature"

# Push the tag to remote
git push origin v1.9.0
```

### Tag Management Commands
```bash
# List all tags
git tag -l

# Show tag details
git show v1.8.0

# Delete a tag
git tag -d v1.9.0

# Push all tags
git push origin --tags
```

## Integration with Release Process

These scripts integrate with the release process:

1. **Prepare Release**: Update version, documentation, and changelog
2. **Create Tag**: Use `tag_release.sh` to create the version tag
3. **Push Tag**: Push the tag to the remote repository
4. **Create GitHub Release**: Use the tag to create a GitHub release

## Related Documentation

- [Tag Management](../docs/tag-management.md) - Comprehensive tag management guide
- [Release Process](../docs/RELEASE_NOTES.md) - Release procedures and notes
- [Changelog](../CHANGELOG.md) - Version history and changes

## Script Development

When adding new scripts:

1. **Use consistent naming**: `action_purpose.sh`
2. **Include shebang**: `#!/bin/bash`
3. **Add error handling**: `set -e`
4. **Use colored output**: For better user experience
5. **Validate inputs**: Check parameters and environment
6. **Add documentation**: Include usage examples

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x scripts/tag_release.sh
   ```

2. **Wrong Directory**
   ```bash
   # Ensure you're in the project root
   ls app.py
   ```

3. **Invalid Commit Hash**
   ```bash
   # Verify commit exists
   git log --oneline | grep <partial_hash>
   ```

### Getting Help

- Check script usage: `./scripts/tag_release.sh`
- View tag documentation: `docs/tag-management.md`
- Check Git status: `git status`

---

**Last Updated**: January 2025  
**Scripts Version**: 1.0.0 