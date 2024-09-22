import requests
from django.core.management.base import BaseCommand
from core.models import Track, AudioFeature
from core.utils import extract_audio_features_from_raw
import librosa
from pydub import AudioSegment
import io

API_KEY = '0989ca22'  # Key that I have created on the Jamendo website for our Vibra project
LIMIT_PER_REQUEST = 10 #200 is the maximum tracks per request allowed by the Jamendo API
TOTAL_TRACKS_NEEDED = 10  # Set the total number of tracks to fetch

class Command(BaseCommand):
    help = 'Fetch songs from the Jamendo API, store them in the database, and process audio features directly from the URL.'
    
    def handle(self, *args, **kwargs):
        url = 'https://api.jamendo.com/v3.0/tracks'
        tracks_fetched = 0  # Track how many tracks we’ve fetched so far
        
        for offset in range(0, TOTAL_TRACKS_NEEDED, LIMIT_PER_REQUEST):
            params = {
                'client_id': API_KEY,
                'format': 'json',
                'limit': LIMIT_PER_REQUEST,
                'offset': offset,
                'include': 'musicinfo+licenses'  # Include more details in the API response
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                tracks = data.get('results', [])
                tracks_fetched += len(tracks)
                
                for track in tracks:
                    # Print full track details for debugging
                    print(f"Track details: {track}")
                    
                    track_id = track['id']
                    track_title = track['name']
                    artist_name = track['artist_name']
                    genre = track.get('musicinfo', {}).get('tags', [])
                    duration = track['duration']
                    
                    # Check for audio URL fields (try 'audio' and 'audiodownload')
                    audio_url = track.get('audio', '') or track.get('audiodownload', '')
                    
                    if not audio_url:
                        self.stdout.write(self.style.ERROR(f"Track {track_title} does not have a valid audio URL."))
                        continue

                    # Save or update the track metadata in the Django Track model
                    track_obj, created = Track.objects.get_or_create(
                        track_id=track_id,
                        defaults={
                            'track_title': track_title,
                            'artist_name': artist_name,
                            'genre': genre,
                            'duration': duration,
                            'audio_url': audio_url  # Save the external URL for audio
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Saved track {track_title} to the database."))

                    # Stream and process the audio file from the URL
                    mfcc_mean, tempo, chroma_mean = self.process_audio_from_url(audio_url)

                    if mfcc_mean is not None and tempo is not None:
                        try:
                            # Save the extracted audio features (MFCC, tempo, chroma_mean)
                            AudioFeature.objects.update_or_create(
                                track=track_obj,
                                defaults={
                                    'mfcc_mean': mfcc_mean,  # Save MFCC
                                    'tempo': tempo,  # Save tempo
                                    'chroma_mean': chroma_mean  # Save chroma features
                                }
                            )
                            self.stdout.write(self.style.SUCCESS(f"Audio features saved for {track_obj.track_id}."))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error saving AudioFeature for {track_obj.track_id}: {e}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Failed to extract features for {track_title}."))
                
                # Stop if we've fetched enough tracks
                if tracks_fetched >= TOTAL_TRACKS_NEEDED:
                    break
            else:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data: {response.status_code}"))
                break  # Exit the loop if the request fails

    def process_audio_from_url(self, audio_url):
        """
        Stream the audio from the URL, convert it to WAV in memory, and extract features like MFCC, tempo, and chroma.
        """
        try:
            # Stream the audio content from the URL using requests
            response = requests.get(audio_url, stream=True)
            if response.status_code == 200:
                print(f"Streaming audio from {audio_url}...")
                audio_data = io.BytesIO(response.content)
                
                # Debug: Check the format or content type of the file
                content_type = response.headers.get('Content-Type', '')
                print(f"Content-Type: {content_type}")
                
                # Dynamically handle the audio format based on the content type
                file_format = "mp3" if "mpeg" in content_type else content_type.split("/")[-1]
                
                # Convert the audio stream to WAV using pydub (in memory)
                try:
                    audio_segment = AudioSegment.from_file(audio_data, format=file_format)
                    wav_io = io.BytesIO()
                    audio_segment.export(wav_io, format="wav")  # Convert to WAV in memory
                    wav_io.seek(0)  # Reset the BytesIO stream to the beginning
                except Exception as conversion_error:
                    print(f"Error converting audio stream to WAV: {conversion_error}")
                    return None, None, None
                
                # Load the converted WAV file into librosa for processing
                y, sr = librosa.load(wav_io, sr=None)
                
                # Extract audio features (MFCC, tempo, chroma)
                mfcc_mean, tempo, chroma_mean = extract_audio_features_from_raw(y, sr)
                return mfcc_mean, tempo, chroma_mean
            else:
                self.stdout.write(self.style.ERROR(f"Failed to stream audio from {audio_url}"))
                return None, None, None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing {audio_url}: {e}"))
            return None, None, None
