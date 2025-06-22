#!/usr/bin/env python3
"""
Translation extraction and compilation script for Flask-Babel.
This script extracts translatable strings from the application and compiles translation files.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to extract and compile translations."""
    print("🌍 Flask-Babel Translation Management")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Create babel.cfg if it doesn't exist
    if not os.path.exists('babel.cfg'):
        print("📝 Creating babel.cfg configuration file...")
        with open('babel.cfg', 'w') as f:
            f.write("""[python: app.py]
[python: *.py]
[jinja2: templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
""")
        print("✅ babel.cfg created")
    
    # Extract messages
    if not run_command("pybabel extract -F babel.cfg -k _l -o messages.pot .", "Extracting translatable messages"):
        sys.exit(1)
    
    # Create translations directory if it doesn't exist
    translations_dir = Path("translations")
    translations_dir.mkdir(exist_ok=True)
    
    # Initialize translations for each supported language
    languages = ['en', 'cs']  # English and Czech
    
    for lang in languages:
        lang_dir = translations_dir / lang / "LC_MESSAGES"
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if .po file exists
        po_file = lang_dir / "messages.po"
        
        if po_file.exists():
            print(f"🔄 Updating existing translation for {lang}...")
            if not run_command(f"pybabel update -i messages.pot -d translations -l {lang}", f"Updating {lang} translation"):
                print(f"⚠️  Warning: Failed to update {lang} translation")
        else:
            print(f"🔄 Initializing new translation for {lang}...")
            if not run_command(f"pybabel init -i messages.pot -d translations -l {lang}", f"Initializing {lang} translation"):
                print(f"⚠️  Warning: Failed to initialize {lang} translation")
    
    # Compile translations
    if not run_command("pybabel compile -d translations", "Compiling translations"):
        sys.exit(1)
    
    print("\n🎉 Translation extraction and compilation completed!")
    print("\n📋 Next steps:")
    print("1. Edit the .po files in translations/[lang]/LC_MESSAGES/messages.po")
    print("2. Add translations for each msgstr line")
    print("3. Run this script again to compile the translations")
    print("4. Restart your Flask application to see the changes")
    
    print(f"\n📁 Translation files created in: {translations_dir.absolute()}")
    for lang in languages:
        po_file = translations_dir / lang / "LC_MESSAGES" / "messages.po"
        if po_file.exists():
            print(f"   - {lang}: {po_file}")

if __name__ == "__main__":
    main() 