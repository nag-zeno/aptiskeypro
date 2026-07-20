"""Script to fix admin role in SQLite DB."""
import sqlite3
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('aptispro_dev.db')
cursor = conn.cursor()

# Show current users
print("=== Current users ===")
cursor.execute("SELECT id, email, role, is_active FROM users")
rows = cursor.fetchall()
for r in rows:
    print(f"  id={r[0]}, email={r[1]}, role={r[2]}, is_active={r[3]}")

# Update admin role
cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@aptiskey.com'")
conn.commit()
print(f"\n=== Updated {cursor.rowcount} user(s) ===")

# Show users after update
print("\n=== Users after update ===")
cursor.execute("SELECT id, email, role, is_active FROM users")
rows = cursor.fetchall()
for r in rows:
    print(f"  id={r[0]}, email={r[1]}, role={r[2]}, is_active={r[3]}")

conn.close()
print("\nDone!")
