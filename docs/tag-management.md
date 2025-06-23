# Git Tag Management Documentation

[← Back to Documentation Index](../docs/README.md)

## Overview

This document describes the Git tag management system for the Guest Registration System, including how to create, manage, and use version tags for releases.

## Current Tags

### Version Tags

| Version | Tag | Description | Commit |
|---------|-----|-------------|--------|
| 1.8.0 | `v1.8.0` | Slovak Language Support & Enhanced Housekeeping | 277a65c |
| 1.7.0 | `v1.7.0` | User Date Format Preferences | 6ab3dd3 |
| 1.6.0 | `v1.6.0` | Housekeeping Photo System | 22c8e12 |
| 1.5.0 | `v1.5.0` | User Soft Delete | e74a2e0 |
| 1.4.0 | `v1.4.0` | Amenity-Housekeeper System | e74a2e0 |
| 1.3.0 | `v1.3.0` | Calendar System | ceb063a |
| 1.2.0 | `v1.2.0` | Amenity System | ceb063a |
| 1.1.0 | `v1.1.0` | Performance Indexes | 2637e6e |
| 1.0.0 | `v1.0.0` | Initial Release | 2637e6e |

## Tag Management Commands

### List Tags

```bash
# List all tags
git tag -l

# List tags with descriptions
git tag -n

# List tags in chronological order
git tag --sort=version:refname
```

### Create Tags

#### Manual Tag Creation

```bash
# Create annotated tag (recommended)
git tag -a v1.9.0 -m "Release v1.9.0 - New Feature" <commit_hash>

# Create lightweight tag
git tag v1.9.0 <commit_hash>

# Tag current commit
git tag -a v1.9.0 -m "Release v1.9.0 - New Feature"
```

#### Using the Tagging Script

```bash
# Use the automated tagging script
./scripts/tag_release.sh v1.9.0 <commit_hash> "Release v1.9.0 - New Feature"

# Example
./scripts/tag_release.sh v1.9.0 abc1234 "Release v1.9.0 - Enhanced Reporting"
```

### Delete Tags

```bash
# Delete local tag
git tag -d v1.9.0

# Delete remote tag
git push origin --delete v1.9.0
```

### Push Tags

```bash
# Push specific tag
git push origin v1.9.0

# Push all tags
git push origin --tags
```

## Release Process

### 1. Prepare Release

1. **Ensure all tests pass**
   ```bash
   python manage.py test
   ```

2. **Update version information**
   - Update version in `version.py`
   - Update documentation
   - Update changelog

3. **Create release commit**
   ```bash
   git add .
   git commit -m "Prepare release v1.9.0"
   ```

### 2. Create Tag

```bash
# Get the commit hash
git log --oneline -1

# Create the tag
./scripts/tag_release.sh v1.9.0 <commit_hash> "Release v1.9.0 - New Features"
```

### 3. Push Tag

```bash
# Push the tag to remote
git push origin v1.9.0
```

### 4. Create GitHub Release

1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Select the tag
4. Add release title and description
5. Upload release assets if needed
6. Publish the release

## Tag Naming Convention

### Version Format

- **Format**: `vX.Y.Z`
- **Example**: `v1.8.0`

### Semantic Versioning

- **Major (X)**: Breaking changes
- **Minor (Y)**: New features, backward compatible
- **Patch (Z)**: Bug fixes, backward compatible

### Tag Messages

- **Format**: `Release vX.Y.Z - Brief Description`
- **Example**: `Release v1.8.0 - Slovak Language Support & Enhanced Housekeeping`

## Migration Integration

### Tag-Migration Mapping

Each version tag corresponds to specific database migrations:

| Version | Migration File | Description |
|---------|----------------|-------------|
| 1.8.0 | `1.8.0_add_default_housekeeper_pay.sql` | Default housekeeper pay |
| 1.7.0 | `1.7.0_add_user_date_format.sql` | User date format preferences |
| 1.6.0 | `1.6.0_add_housekeeping_photo.sql` | Housekeeping photo system |
| 1.5.0 | `1.5.0_add_user_soft_delete.sql` | User soft delete |
| 1.4.0 | `1.4.0_add_amenity_housekeeper_system.sql` | Amenity-housekeeper system |
| 1.3.0 | `1.3.0_add_calendar_system.sql` | Calendar system |
| 1.2.0 | `1.2.0_add_amenity_system.sql` | Amenity system |
| 1.1.0 | `1.1.0_add_performance_indexes.sql` | Performance indexes |
| 1.0.0 | `1.0.0_initial_schema.sql` | Initial schema |

## Best Practices

### Tag Creation

1. **Use annotated tags** for releases
2. **Include descriptive messages**
3. **Tag specific commits** (not just HEAD)
4. **Verify tag creation** before pushing

### Tag Management

1. **Keep tags organized** by version
2. **Document tag purposes** in commit messages
3. **Use consistent naming** conventions
4. **Review tags before release**

### Release Process

1. **Test thoroughly** before tagging
2. **Update documentation** with release notes
3. **Create GitHub releases** for major versions
4. **Notify stakeholders** of releases

## Troubleshooting

### Common Issues

1. **Tag already exists**
   ```bash
   # Delete and recreate
   git tag -d v1.9.0
   git tag -a v1.9.0 -m "Release v1.9.0" <commit_hash>
   ```

2. **Invalid commit hash**
   ```bash
   # Verify commit exists
   git log --oneline | grep <partial_hash>
   ```

3. **Tag not pushed**
   ```bash
   # Push specific tag
   git push origin v1.9.0
   ```

### Tag Verification

```bash
# Verify tag exists
git tag -l | grep v1.9.0

# Show tag details
git show v1.9.0

# Check tag commit
git rev-parse v1.9.0
```

## Automation

### Tagging Script

The `scripts/tag_release.sh` script automates tag creation:

**Features:**
- Version format validation
- Commit hash verification
- Duplicate tag detection
- Colored output
- Helpful instructions

**Usage:**
```bash
./scripts/tag_release.sh <version> <commit_hash> <description>
```

### CI/CD Integration

Tags can be integrated with CI/CD pipelines:

```yaml
# Example GitHub Actions
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create Release
        uses: actions/create-release@v1
```

## Related Documentation

- [Changelog](../CHANGELOG.md) - Version history
- [Release Notes](../RELEASE_NOTES.md) - User-friendly release information
- [Migrations](migrations.md) - Database migration system
- [Testing](testing.md) - Testing procedures

## Support

For tag management issues:

1. Check tag existence: `git tag -l`
2. Verify commit hash: `git log --oneline`
3. Review tag details: `git show <tag>`
4. Check remote tags: `git ls-remote --tags origin`

---

**Last Updated**: January 2025  
**Current Version**: 1.8.0

[← Back to Documentation Index](../docs/README.md) 