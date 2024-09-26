import requests
from django.core.management.base import BaseCommand
from core.models import Track, AudioFeature
from core.utils import extract_audio_features_from_raw
import librosa
from pydub import AudioSegment
import io

API_KEY = '0989ca22'  # Key that I have created on the Jamendo website for our Vibra project
LIMIT_PER_REQUEST = 200  # 200 are the maximum tracks per request allowed by the Jamendo API
TOTAL_TRACKS_NEEDED = 200  # Set the total number of tracks to fetch

class Command(BaseCommand):
    help = 'Fetch songs from the Jamendo API, store them in the database, and process audio features directly from the URL.'

    def handle(self, *args, **kwargs):
        url = 'https://api.jamendo.com/v3.0/tracks'
        tracks_fetched = 0

        for offset in range(0, TOTAL_TRACKS_NEEDED, LIMIT_PER_REQUEST):
            params = {
                'client_id': API_KEY,
                'format': 'json',
                'limit': LIMIT_PER_REQUEST,
                'offset': offset,
                'include': 'musicinfo+licenses'  # Include additional fields
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                tracks = data.get('results', [])
                tracks_fetched += len(tracks)

                for track in tracks:
                    track_id = track['id']
                    track_title = track['name']
                    artist_name = track['artist_name']
                    album_name = track.get('album_name', None)
                    album_id = track.get('album_id', None)
                    album_image = track.get('image', None)
                    artist_id = track.get('artist_id', None)
                    genre = track.get('musicinfo', {}).get('tags', [])
                    duration = track['duration']
                    release_date = track.get('releasedate', None)
                    audio_url = track.get('audio', '') or track.get('audiodownload', '')
                    share_url = track.get('shareurl', None)

                    # Safely handle the licenses field
                    licenses = track.get('licenses', [])
                    license_url = None
                    if isinstance(licenses, list) and len(licenses) > 0:
                        license_url = licenses[0].get('buyurl', None)

                    if not audio_url:
                        self.stdout.write(self.style.ERROR(f"Track {track_title} does not have a valid audio URL."))
                        continue

                    # Save or update the track metadata in the Django Track model
                    track_obj, created = Track.objects.update_or_create(
                        track_id=track_id,
                        defaults={
                            'track_title': track_title,
                            'artist_name': artist_name,
                            'album_name': album_name,
                            'album_id': album_id,
                            'album_image': album_image,
                            'artist_id': artist_id,
                            'audio_url': audio_url,
                            'duration': duration,
                            'release_date': release_date,
                            'genre': genre,
                            'share_url': share_url,
                            'license_url': license_url,
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
                                track = track_obj,
                                defaults={
                                    'mfcc_mean': mfcc_mean,
                                    'tempo': tempo,
                                    'chroma_mean': chroma_mean
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
                break

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
                
                # Convert the audio stream to WAV using pydub (in memory)
                try:
                    audio_segment = AudioSegment.from_file(audio_data, format="mp3")
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
