#!/usr/bin/env python3
"""
Script to fix the user table's primary key sequence in PostgreSQL.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, db

load_dotenv()

def fix_user_sequence():
    with app.app_context():
        table_prefix = app.config['TABLE_PREFIX']
        user_table = f"{table_prefix}user"
        print(f"🔄 Fixing sequence for table: {user_table}")
        try:
            sql = text(f"SELECT setval(pg_get_serial_sequence('{user_table}', 'id'), COALESCE(MAX(id), 1)) FROM {user_table};")
            db.session.execute(sql)
            db.session.commit()
            print("✅ Sequence fixed successfully!")
        except Exception as e:
            print(f"❌ Error fixing sequence: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_user_sequence() 