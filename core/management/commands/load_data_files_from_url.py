import os
import requests
import zipfile
import tempfile
from django.core.management.base import BaseCommand
from core.models import Song  # Ensure correct model import
import shutil
import urllib3
import csv

urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

class Command(BaseCommand):
    help = 'Load MP3 files and metadata into the database'

    def handle(self, *args, **kwargs):
        # Define MP3 part files and their corresponding names
        mp3_parts = [
            'https://mirg.city.ac.uk/datasets/magnatagatune/mp3.zip.001',
            'https://mirg.city.ac.uk/datasets/magnatagatune/mp3.zip.002',
            'https://mirg.city.ac.uk/datasets/magnatagatune/mp3.zip.003'
        ]
        
        # Define the final zip file name to which the parts will be merged
        final_zip_name = 'merged_mp3.zip'

        # Temporary directories
        temp_dir = tempfile.mkdtemp()  # Automatically creates a temporary directory

        # Call the download and unzip function with the required arguments
        self.download_and_unzip(mp3_parts, temp_dir, final_zip_name)

        self.stdout.write(self.style.SUCCESS('Successfully downloaded and extracted MP3 files'))

        # Metadata files (CSV)
        metadata_files = [
            'https://mirg.city.ac.uk/datasets/magnatagatune/clip_info_final.csv',
            'https://mirg.city.ac.uk/datasets/magnatagatune/annotations_final.csv',
            'https://mirg.city.ac.uk/datasets/magnatagatune/comparisons_final.csv'
        ]

        # Process CSV files for metadata
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as dest_dir:
            self.stdout.write(f"Using temporary directories:\nTemp unzip: {temp_dir}\nDestination: {dest_dir}")

            # Move MP3 files from unzipped folders to the final destination
            self.move_mp3_files(temp_dir, dest_dir)

            # Download and process metadata CSV files
            for url in metadata_files:
                self.download_csv_file(url, temp_dir)

            # Insert metadata into the database
            self.load_metadata_into_db(os.path.join(temp_dir, 'clip_info_final.csv'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded MP3 files and metadata'))

    def download_csv_file(self, url, destination):
        try:
            csv_file = self.download_file_with_retry(url, destination)
            if csv_file:
                self.stdout.write(f"Successfully downloaded CSV file: {csv_file}")
            else:
                self.stdout.write(f"Failed to download CSV file: {url}")
        except Exception as e:
            self.stdout.write(f"Failed to download CSV file {url}: {e}")
            
    # Function to download files with retry
    def download_file_with_retry(self, url, destination, retries=3, expected_size=None):
        attempt = 0
        while attempt < retries:
            try:
                file_name = os.path.join(destination, os.path.basename(url))
                self.stdout.write(f"Downloading {url} (attempt {attempt + 1})...")
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raises HTTPError for bad responses

                # Write content to file
                with open(file_name, 'wb') as f:
                    for chunk in response.iter_content(1024 * 1024):  # 1 MB chunk size
                        if chunk:
                            f.write(chunk)

                # Check file size if expected size is provided
                if expected_size is not None:
                    file_size = os.path.getsize(file_name)
                    if file_size < expected_size * 0.9:  # Warn if file size is much smaller
                        self.stdout.write(f"Warning: Downloaded file size {file_size} bytes seems smaller than expected.")
                    elif file_size > expected_size:
                        self.stdout.write(f"Warning: Downloaded file is larger than expected {file_size} bytes.")

                # If no expected size or file size is good, return the file path
                self.stdout.write(f"Downloaded {url} successfully (size: {os.path.getsize(file_name)} bytes).")
                return file_name

            except requests.exceptions.RequestException as e:
                self.stdout.write(f"Failed to download {url}. Error: {str(e)}")
                attempt += 1
                if attempt == retries:
                    raise Exception(f"Failed to download {url} after {retries} attempts.")

        return None  # If all attempts fail

    # For handling zip files with parts
    def download_and_unzip(self, part_files, destination, final_zip_name):
        # Download all parts of the zip file
        for part_url in part_files:
            self.download_file_with_retry(part_url, destination)

        # Merge all parts into a single zip file
        merged_zip_path = os.path.join(destination, final_zip_name)
        try:
            with open(merged_zip_path, 'wb') as merged_zip:
                for part_file in part_files:
                    part_path = os.path.join(destination, os.path.basename(part_file))
                    if os.path.exists(part_path):
                        with open(part_path, 'rb') as part:
                            shutil.copyfileobj(part, merged_zip)
                    else:
                        self.stdout.write(f"Part file {part_path} does not exist. Skipping.")
                        return  # Stop the process if a part is missing
        except Exception as e:
            self.stdout.write(f"Error merging zip parts: {e}")
            return

        # Now try unzipping the merged zip file
        try:
            with zipfile.ZipFile(merged_zip_path, 'r') as zip_ref:
                zip_ref.extractall(destination)
            self.stdout.write(f"Successfully unzipped {merged_zip_path}")
        except zipfile.BadZipFile:
            self.stdout.write(f"{merged_zip_path} is not a valid zip file. Skipping.")
        except Exception as e:
            self.stdout.write(f"Error unzipping {merged_zip_path}: {e}")

    def move_mp3_files(self, source_dir, dest_dir):
        # Move all mp3 files from source to destination, including nested directories
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".mp3"):
                    # Move each mp3 file to the destination directory
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    
                    # Check if file already exists in the destination to avoid overwriting
                    if not os.path.exists(dest_file):
                        shutil.move(src_file, dest_file)
                    else:
                        self.stdout.write(f"File {file} already exists in the destination. Skipping.")

    def load_metadata_into_db(self, metadata_file_path):
        # Debugging to show where the file is being looked for
        self.stdout.write(f'Looking for metadata file at: {metadata_file_path}')
        
        # Load metadata from CSV and insert into the database
        try:
            with open(metadata_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Create or update Song instance here
                    song = Song(
                        clip_id=row['clip_id'],
                        track_number=row['track_number'],
                        title=row['title'],
                        artist=row['artist'],
                        album=row['album'],
                        url=row['url'],
                        segment_start=row['segmentStart'],
                        segment_end=row['segmentEnd'],
                        original_url=row['original_url'],
                        mp3_path=row['mp3_path'],
                    )
                    song.save()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {metadata_file_path}"))
