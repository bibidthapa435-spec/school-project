import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_project.settings")
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    print("Database schema reset successfully.")
