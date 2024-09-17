SETUP

Step 1. Initialized a new Django project named vibra_backend: `django-admin startproject vibra_backend .``

Step 2. Create Separate Domain Specific Django Apps for Each Major Functionality:
    python manage.py startapp home
    python manage.py startapp for_you (NOT YET)
    python manage.py startapp profile (NOT YET)

Step 3. Apply Migrations:
    python manage.py migrate

    When Should You Run It?

    Initial Project Setup: To set up the initial database schema when starting a new Django project.

    After Model Changes: Whenever you make changes to your models (e.g., adding a new model, modifying fields), you need to:

        Create Migration Files: Run python manage.py make migrations to generate migration files reflecting your model changes.

        Apply Migrations: Run python manage.py migrate to apply those changes to your database.

    After Pulling New Code: If you've pulled new code from version control that includes migrations, you need to apply them to keep your local database up to date.


