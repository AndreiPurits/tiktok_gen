import os
from yt_dlp import YoutubeDL

def download_youtube_video(url, output_folder="downloads"):
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # filename based on title
        'quiet': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Пример использования:
download_youtube_video("https://www.youtube.com/watch?v=zZ7AimPACzc", output_folder="backgrounds")
