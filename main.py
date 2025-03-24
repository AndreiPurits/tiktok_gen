import os
import whisper
import yt_dlp
import tempfile
import random
import time
import gc

# Set ImageMagick path BEFORE importing moviepy
os.environ["IMAGEMAGICK_BINARY"] = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, clips_array, vfx
from PIL import Image
Image.ANTIALIAS = Image.Resampling.LANCZOS  # Fix for deprecated PIL.Image.ANTIALIAS

# Parameters
VIDEO_URL = "https://www.youtube.com/watch?v=czIxo62cWC0"
CLIP_MIN_LENGTH = 15
CLIP_MAX_LENGTH = 35  # reduced max clip length for faster transcription
MUSIC_FOLDER = "music"  # Folder with background music
BACKGROUND_FOLDER = "backgrounds"  # Folder with looping background videos

# Download video
def download_video(url, out_path):
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(out_path, 'video.%(ext)s'),
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return os.path.join(out_path, "video.mp4")

# Cut random clip
def cut_random_clip(input_path, output_path):
    with VideoFileClip(input_path) as video:
        duration = video.duration
        clip_length = random.randint(CLIP_MIN_LENGTH, CLIP_MAX_LENGTH)

        if clip_length >= duration:
            clip = video
        else:
            start = random.uniform(0, duration - clip_length)
            clip = video.subclip(start, start + clip_length)

        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        clip.close()

# Transcribe audio
def transcribe_audio(video_path, model_size="medium"):
    model = whisper.load_model(model_size)
    result = model.transcribe(video_path, word_timestamps=True)
    return result

# Add background music and subtitles
def enhance_clip(clip_path, transcription, output_path):
    video = VideoFileClip(clip_path)

    # Pick random background video and resize
    bg_files = [f for f in os.listdir(BACKGROUND_FOLDER) if f.endswith(".mp4")]
    if not bg_files:
        raise FileNotFoundError("No background videos found in the 'backgrounds' folder.")
    bg_path = os.path.join(BACKGROUND_FOLDER, random.choice(bg_files))
    background = VideoFileClip(bg_path).resize(width=video.w).loop(duration=video.duration)

    # Stack the original and background videos
    stacked = clips_array([[video], [background]])

    # Pick a random music file
    music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]
    if not music_files:
        raise FileNotFoundError("No .mp3 files found in the 'music' folder.")
    selected_music = os.path.join(MUSIC_FOLDER, random.choice(music_files))

    audio = AudioFileClip(selected_music).volumex(0.15).set_duration(video.duration)
    original_audio = video.audio.volumex(1.0)
    mixed_audio = CompositeAudioClip([original_audio, audio])
    stacked = stacked.set_audio(mixed_audio)

    # Subtitles
    subs = []
    for segment in transcription["segments"]:
        for word in segment["words"]:
            txt = word["word"].strip()
            txt_clip = TextClip(
                txt,
                fontsize=50,
                color="yellow",
                font="Arial-Bold",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(video.w - 100, None),
                align="center"
            ).set_start(word["start"]).set_duration(word["end"] - word["start"])

            # Positioning and styling
            txt_clip = txt_clip.set_position(("center", video.h - 120))
            txt_clip = txt_clip.fadein(0.2).fadeout(0.2)
            subs.append(txt_clip)

    final = CompositeVideoClip([stacked, *subs])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

    video.close()
    background.close()
    audio.close()
    final.close()
    for s in subs:
        s.close()
    gc.collect()
    time.sleep(1)

# Main
def main():
    with tempfile.TemporaryDirectory() as tmp:
        print("🔽 Downloading video...")
        video_path = download_video(VIDEO_URL, tmp)

        print(f"✂️ Cutting clip...")
        clip_path = os.path.join(tmp, f"clip.mp4")
        cut_random_clip(video_path, clip_path)

        print("🧠 Transcribing speech...")
        transcript = transcribe_audio(clip_path)

        print("🎵 Enhancing video...")
        output = f"output.mp4"
        enhance_clip(clip_path, transcript, output)

        print(f"✅ Clip saved as {output}")

if __name__ == "__main__":
    main()