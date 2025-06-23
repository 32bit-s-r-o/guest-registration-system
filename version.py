#!/usr/bin/env python3
"""
Version management for Guest Registration System
Handles version tracking, compatibility, and upgrade paths
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class VersionManager:
    def __init__(self, version_file: str = "version.json"):
        self.version_file = version_file
        self.current_version = "1.0.0"
        self.minimum_database_version = "1.0.0"
        self.upgrade_paths = {
            "1.0.0": ["1.1.0", "1.2.0"],
            "1.1.0": ["1.2.0"],
            "1.2.0": ["1.3.0"],
        }
        
        # Load version information
        self._load_version_info()
    
    def _load_version_info(self):
        """Load version information from file"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    self.current_version = data.get('current_version', self.current_version)
                    self.minimum_database_version = data.get('minimum_database_version', self.minimum_database_version)
                    self.upgrade_paths = data.get('upgrade_paths', self.upgrade_paths)
            except Exception as e:
                print(f"⚠️ Could not load version file: {e}")
    
    def _save_version_info(self):
        """Save version information to file"""
        try:
            data = {
                'current_version': self.current_version,
                'minimum_database_version': self.minimum_database_version,
                'upgrade_paths': self.upgrade_paths,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.version_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save version file: {e}")
    
    def get_current_version(self) -> str:
        """Get current application version"""
        return self.current_version
    
    def get_minimum_database_version(self) -> str:
        """Get minimum required database version"""
        return self.minimum_database_version
    
    def is_compatible(self, database_version: str) -> bool:
        """Check if database version is compatible with current app version"""
        return self._compare_versions(database_version, self.minimum_database_version) >= 0
    
    def get_upgrade_path(self, from_version: str) -> List[str]:
        """Get upgrade path from current version to latest"""
        path = []
        current = from_version
        
        while current in self.upgrade_paths:
            next_versions = self.upgrade_paths[current]
            if not next_versions:
                break
            
            # Choose the highest version in the upgrade path
            next_version = max(next_versions, key=lambda v: self._version_to_tuple(v))
            path.append(next_version)
            current = next_version
        
        return path
    
    def can_upgrade_to(self, target_version: str) -> bool:
        """Check if upgrade to target version is possible"""
        return target_version in self.get_upgrade_path(self.current_version)
    
    def _version_to_tuple(self, version: str) -> tuple:
        """Convert version string to tuple for comparison"""
        parts = version.split('.')
        return tuple(int(part) for part in parts)
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings"""
        v1 = self._version_to_tuple(version1)
        v2 = self._version_to_tuple(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    def update_version(self, new_version: str):
        """Update current version"""
        self.current_version = new_version
        self._save_version_info()
    
    def get_version_info(self) -> Dict:
        """Get complete version information"""
        return {
            'current_version': self.current_version,
            'minimum_database_version': self.minimum_database_version,
            'upgrade_paths': self.upgrade_paths,
            'build_date': datetime.now().isoformat(),
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }

# Version history and changelog
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2025-01-01",
        "features": [
            "Initial guest registration system",
            "User management with roles",
            "Trip management",
            "Guest registration forms",
            "Document upload functionality",
            "GDPR compliance features"
        ],
        "database_schema": "1.0.0",
        "breaking_changes": []
    },
    "1.1.0": {
        "date": "2025-01-15",
        "features": [
            "Performance indexes added",
            "Backup and restore functionality",
            "Email notifications",
            "Invoice generation",
            "Housekeeping management"
        ],
        "database_schema": "1.1.0",
        "breaking_changes": []
    },
    "1.2.0": {
        "date": "2025-02-01",
        "features": [
            "Multi-language support (English/Czech)",
            "Airbnb calendar integration",
            "Advanced analytics and reporting",
            "CSV export functionality",
            "PDF invoice generation"
        ],
        "database_schema": "1.2.0",
        "breaking_changes": []
    }
}

def get_version_changelog(version: str) -> Optional[Dict]:
    """Get changelog for specific version"""
    return VERSION_HISTORY.get(version)

def get_all_changelogs() -> Dict:
    """Get all version changelogs"""
    return VERSION_HISTORY

def check_version_compatibility(app_version: str, db_version: str) -> Dict:
    """Check compatibility between app and database versions"""
    vm = VersionManager()
    
    return {
        'compatible': vm.is_compatible(db_version),
        'app_version': app_version,
        'db_version': db_version,
        'minimum_required_db': vm.get_minimum_database_version(),
        'upgrade_needed': vm._compare_versions(db_version, vm.get_minimum_database_version()) < 0,
        'upgrade_path': vm.get_upgrade_path(db_version) if vm._compare_versions(db_version, vm.get_minimum_database_version()) < 0 else []
    }

# Initialize version manager
version_manager = VersionManager()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python version.py [command]")
        print("Commands:")
        print("  current                    - Show current version")
        print("  info                       - Show version information")
        print("  changelog [version]        - Show changelog for version")
        print("  compatibility <db_version> - Check compatibility")
        print("  upgrade-path <from_version> - Show upgrade path")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "current":
        print(f"Current version: {version_manager.get_current_version()}")
    
    elif command == "info":
        info = version_manager.get_version_info()
        print("Version Information:")
        print(json.dumps(info, indent=2))
    
    elif command == "changelog":
        version = sys.argv[2] if len(sys.argv) > 2 else version_manager.get_current_version()
        changelog = get_version_changelog(version)
        if changelog:
            print(f"Changelog for version {version}:")
            print(json.dumps(changelog, indent=2))
        else:
            print(f"No changelog found for version {version}")
    
    elif command == "compatibility":
        if len(sys.argv) < 3:
            print("❌ Please specify database version")
            sys.exit(1)
        db_version = sys.argv[2]
        compat = check_version_compatibility(version_manager.get_current_version(), db_version)
        print("Compatibility Check:")
        print(json.dumps(compat, indent=2))
    
    elif command == "upgrade-path":
        if len(sys.argv) < 3:
            print("❌ Please specify from version")
            sys.exit(1)
        from_version = sys.argv[2]
        path = version_manager.get_upgrade_path(from_version)
        print(f"Upgrade path from {from_version}:")
        print(" → ".join(path) if path else "No upgrade path available")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1) 