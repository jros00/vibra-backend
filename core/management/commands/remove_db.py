from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Find tables that have foreign keys referencing `auth_user`
                cursor.execute("PRAGMA foreign_keys = OFF;")  # Disable constraints
                
                # List all tables related to auth_user by foreign key
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Identify and drop dependent tables
                for table in tables:
                    cursor.execute(f"PRAGMA foreign_key_list({table});")
                    foreign_keys = cursor.fetchall()
                    if any(fk[2] == 'auth_user' for fk in foreign_keys):  # Check if table references auth_user
                        cursor.execute(f"DELETE FROM {table};")
                        self.stdout.write(self.style.SUCCESS(f"Delteted content of related table: {table}"))
                
                # Finally, drop the `auth_user` table
                cursor.execute("DELETE FROM auth_user;")
                cursor.execute("PRAGMA foreign_keys = ON;")  # Re-enable constraints
                self.stdout.write(self.style.SUCCESS("Deleted content of auth_user table and all related tables."))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
