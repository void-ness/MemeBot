import os
import io
import time
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, AudioClip
import yt_dlp
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemeGeneratorManager:
    def __init__(self, urls: list[str], output_path: str):
        self.final_video_path = output_path
        self.input_video_path = "media/video/video.mp4"
        
        self.audio_urls = urls
        self.max_retries = 3
        self.start_time = time.perf_counter()
        self.time_logs = []

        self.temp_audio_dir = "media/audio/temp_audio"
        self.init_audio_dir()

    def log_time(self, stage):
        current_time = time.perf_counter()
        elapsed = current_time - self.start_time
        relative = current_time - getattr(self, 'last_time', self.start_time)
        self.time_logs.append((stage, elapsed, relative))
        self.last_time = current_time

    def print_time_logs(self):
        print("\nTime logs:")
        for stage, elapsed, relative in self.time_logs:
            print(f"{stage:<30} - Absolute: {elapsed:.2f}s, Relative: {relative:.2f}s")

    def generate_meme(self):
        """Generate a meme video by combining the video and audio clips."""
        self.log_time("Starting meme generation")

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all download tasks and store futures with their indices
            future_to_index = {executor.submit(self.download_youtube_audio, url): i 
                               for i, url in enumerate(self.audio_urls)}
            
            # Initialize a list to store audio clips in order
            audio_clips = [None] * len(self.audio_urls)
            
            # Process futures as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    audio_clip = future.result()
                    if audio_clip:
                        audio_clips[index] = audio_clip
                except Exception as e:
                    logging.error(f"Error processing URL at index {index}: {str(e)}")

        # Remove any None values (failed downloads)
        audio_clips = [clip for clip in audio_clips if clip is not None]

        self.log_time("Finished downloading audio clips")

        if len(audio_clips) == len(self.audio_urls):
            self.combine_audio_with_video(audio_clips)
        else:
            logging.warning("Some audio files failed to download. Check logs for details.")
        
        self.log_time("Finished meme generation")

        # self.delete_downloaded_audios()
        self.clean_directory(self.temp_audio_dir)
        self.log_time("Finished deleting audio clips downloaded")

        self.print_time_logs()

    def init_audio_dir(self):
        """Create the directory to save audio and video files."""
        if not os.path.exists(self.temp_audio_dir):
            os.makedirs(self.temp_audio_dir)
        
        if not os.path.exists(self.final_video_path):
            os.makedirs(self.final_video_path)

    def clean_directory(self, directory_path):
        """
        Remove all files and subdirectories from the specified directory.
        
        :param directory_path: Path to the directory to be cleaned
        """
        try:
            # Ensure the directory exists
            if not os.path.exists(directory_path):
                print(f"The directory {directory_path} does not exist.")
                return

            # Iterate over all files and subdirectories
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        # Remove the file
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        # Remove the directory and its contents
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

            print(f"All files and subdirectories in {directory_path} have been removed.")

        except Exception as e:
            print(f"An error occurred while cleaning the directory: {e}")
            
    def delete_downloaded_audios(self):
        """Delete the downloaded audio files."""
        for audio_path in self.downloaded_audio_paths:
            try:
                os.remove(audio_path)
                logging.info(f"Deleted: {audio_path}")
            except OSError as e:
                logging.error(f"Error deleting {audio_path}: {e}")

    def download_youtube_audio(self, url):
        """Download the audio from a YouTube URL and return the audio file clip."""
        for attempt in range(self.max_retries):
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'external_downloader': 'ffmpeg',
                    'external_downloader_args': [
                        '-ss', '60',  # Start time
                        '-to', '62.5'  # End time
                    ],
                    'outtmpl': os.path.join(self.temp_audio_dir, '%(id)s.%(ext)s'),  # Save to media/audio
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    audio_file = ydl.prepare_filename(info)  # Get audio file path

                # Ensure correct extension and return the audio file path
                audio_file = audio_file.replace(".webm", ".mp3")
                # return audio_file
                audio = AudioFileClip(audio_file)
                return audio

            except Exception as e:
                logging.error(f"Error: {e} - Attempt {attempt + 1} of {self.max_retries}")

                # Check if max retries reached
                if attempt + 1 == self.max_retries:
                    logging.error(f"Max retries reached. Skipping URL: {url}")
                    return None

                # Wait before retrying
                time.sleep(2)
    
    def combine_audio_with_video(self, audio_clips):
        """Combine video with the downloaded audio clips in sequence."""
        # Load the video file
        video = VideoFileClip(self.input_video_path)
        
        # Loop through each audio file and set start time to avoid overlap
        current_start_time = 0
        for i, audio in enumerate(audio_clips):
            audio_clips[i] = audio.set_start(current_start_time)
            current_start_time += audio.duration
        
        final_audio = CompositeAudioClip(audio_clips)

        # Set the final audio to the video
        final_video = video.set_audio(final_audio)
        
        self.log_time("Starting video export")
        
        final_video.write_videofile(self.final_video_path, codec="libx264", audio_codec="aac", 
                                    threads=4, preset='ultrafast')
        
        self.log_time("Finished video export")

        video.close()
        for clip in audio_clips:
            clip.close()

# audio_urls = [
#     "https://www.youtube.com/watch?v=PejQbGZraqg",
#     "https://www.youtube.com/watch?v=MhXCj8E9CZU",
#     "https://www.youtube.com/watch?v=d2ofxg8pHfQ",
#     "https://www.youtube.com/watch?v=kw4tT7SCmaY"
# ]

# MemeGeneratorManager(urls=audio_urls).generate_meme()