import os
from django.core.management.base import BaseCommand
from django.conf import settings
from home.models import Song  # Import your model
from django.utils import timezone
from django.core.files import File

class Command(BaseCommand):
    help = 'Load MP3 files from multiple folders into the database'

    def add_arguments(self, parser):
        # Argument to specify the base directory where MP3 files are stored
        parser.add_argument('directory', type=str, help='The base directory containing MP3 files and subdirectories')

    def handle(self, *args, **kwargs):
        base_directory = kwargs['directory']

        # Ensure the provided directory exists
        if not os.path.isdir(base_directory):
            self.stdout.write(self.style.ERROR(f"Directory {base_directory} does not exist"))
            return

        # Use os.walk to iterate over all directories and subdirectories
        for root, dirs, files in os.walk(base_directory):
            for file in files:
                if file.endswith(".mp3"):
                    file_path = os.path.join(root, file)

                    # Extract file name without extension to use as the title
                    file_title = os.path.splitext(file)[0]

                    # Save the MP3 file reference to the database
                    with open(file_path, 'rb') as mp3_file:
                        # Create a File object to be passed to the model
                        django_file = File(mp3_file)

                        # Create the Song instance and save it
                        song = Song(
                            title=file_title,
                            uploaded_at=timezone.now()  # Automatically set the uploaded timestamp
                        )
                        song.mp3_file.save(file, django_file)  # Save the file using the model's FileField

        self.stdout.write(self.style.SUCCESS(f'Successfully processed MP3 files from {base_directory}'))
