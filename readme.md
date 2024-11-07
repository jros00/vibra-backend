# The core of VIBRA's backend.

## Installation Process (IMPORTANT):
    
### 1. Install dependencies: 
        
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        brew install redis
        brew install ffmpeg

### 2. Run this ONCE (sets up the initial db schema in sqllite): 

        First set up a file called super_secret.py under the main folder.
        Add a string variable: my_ip = ""
        The string can be empty for installation, but you should save your
        IP address in this variable when running the server. 
        
        python manage.py makemigrations
        python manage.py migrate

### 3. Run this to load the database tables with initial content:
    
        python manage.py fetch_songs_from_jamendo
        python manage.py load_chats

        NEW UPDATE in load_chats, to be able to run the script without deleting the entire database, 
        run `python manage.py remove_db`. This will only remove user related content. After that, run 
        `python manage.py load_chats` as usual to apply the latest updates. 

### 4. To START the server

#### a. Open one terminal and run:

        redis-server


#### b. To START the server, run: 

        uvicorn vibra_backend.asgi:application --host 0.0.0.0 --port 8000

(Running on 0.0.0.0 makes the server accessible over your local network, which is necessary for testing on your iPhone.)

### 5. NOTE: Ideally, create a new branch by your name i.e. 'Johannes' and work and commit on this branch.
    


## LOG:

    Step 1. Initialized a new Django project named vibra_backend: `django-admin startproject vibra_backend .`` (DONE)

    Step 2. Create Separate Domain Specific Django Apps for Each Major Functionality: 
        python manage.py startapp home (DONE)
        python manage.py startapp for_you (DONE)
        python manage.py startapp profile (NOT YET)

    Step 3. Apply Migrations:
        python manage.py migrate

        When Should You Run It?

        Initial Project Setup: To set up the initial database schema when starting a new Django project.

        After Model Changes: Whenever you make changes to your models (e.g., adding a new model, modifying fields), you need to:

            Create Migration Files: Run python manage.py make migrations to generate migration files reflecting your model changes.

            Apply Migrations: Run python manage.py migrate to apply those changes to your database.

        After Pulling New Code: If you've pulled new code from version control that includes migrations, you need to apply them to keep your local database up to date.


