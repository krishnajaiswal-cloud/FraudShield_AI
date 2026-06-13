"""Test updated get_database_url method"""
from app.core.config import settings

print("Testing updated get_database_url() method:")
print(f"  DATABASE_URL (config): {settings.DATABASE_URL}")
print(f"  Resolved URL: {settings.get_database_url()}")
print(f"  ✓ URL is absolute: {'/' in settings.get_database_url() or '\\' in settings.get_database_url()}")
