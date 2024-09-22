# Load the metadata from the Jamendo API and extract the audio features

The script downloads the audio files, extracts the audio features and then erases the audio file directly afterwards. It saves a link to the Jamendo API for each specific track.

Change the variables LIMIT_PER_REQUEST and TOTAL_TRACKS_NEEDED to match the number of tracks that you want the metadata from. Currently it is set to download the metadata for 10 tracks.

### Step 1.
Install ffmpeg. I tried for a long time to find a similar pip installment instead of brew so it could be added to the requirements file but I could not find anything that worked. 

    brew install ffmpeg

### Step 2. 
Run the following command:

    python manage.py fetch_songs_from_jamendo

### Step 3. 
Start the server

### Step 4. 
Navigate to a specific track
In the url field: type http://localhost:8000/api/for_you/trackid/
Where track id is the id of a specific track you have downloaded

For example:

    http://localhost:8000/api/for_you/241/

This will provide you with the link to the specific track and the link to the five most similar tracks among the ones that you have extracted the data from. If you click on one of the links, it will play the requested song directly in the browser. In this way we don't need to store the actual audio files locally. We can use only the audio features for machine learning pruposes which will require a lot less memory. Still a lot of memory is needed.

This code still gives this warning message "currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'" but it seems like the only way around it is to make another brew installment which I want to avoid. The code still works without this installment. Maybe we can discuss how to do with other installments than pip in the future.
