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

from moviepy.video.fx.all import lum_contrast

# Parameters
VIDEO_URL = "https://www.youtube.com/watch?v=czIxo62cWC0"
CLIP_MIN_LENGTH = 15
CLIP_MAX_LENGTH = 35
CLIP_INTERVAL = 240  # 4 minutes in seconds
MUSIC_FOLDER = "music"
BACKGROUND_FOLDER = "backgrounds"

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
def cut_random_clip(input_path, output_path, start_range):
    with VideoFileClip(input_path) as video:
        duration = video.duration
        clip_length = random.randint(CLIP_MIN_LENGTH, CLIP_MAX_LENGTH)

        start = random.uniform(start_range, max(0.1, duration - clip_length))
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

    # Pick random background video and random start
    bg_files = [f for f in os.listdir(BACKGROUND_FOLDER) if f.endswith(".mp4")]
    if not bg_files:
        raise FileNotFoundError("No background videos found in the 'backgrounds' folder.")
    bg_path = os.path.join(BACKGROUND_FOLDER, random.choice(bg_files))
    background = VideoFileClip(bg_path)
    if background.duration > video.duration:
        start = random.uniform(0, background.duration - video.duration)
        background = background.subclip(start, start + video.duration)
    else:
        background = background.loop(duration=video.duration)
    background = background.resize(width=video.w)

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
                stroke_color=None,
                stroke_width=0,
                method="caption",
                size=(video.w - 100, None),
                align="center"
            ).set_start(word["start"]).set_duration(word["end"] - word["start"])

            txt_clip = txt_clip.set_position(("center", video.h - 120))
            subs.append(txt_clip)

    final = CompositeVideoClip([stacked, *subs])
    #final = final.fx(lum_contrast, 10, 100, 128)  # Simple eye-friendly contrast boost
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

        print("✂️ Creating multiple clips...")
        with VideoFileClip(video_path) as full:
            total_duration = full.duration

        n_clips = int(total_duration // CLIP_INTERVAL)
        for i in range(n_clips):
            print(f"➡️ Clip {i + 1}/{n_clips}")
            clip_path = os.path.join(tmp, f"clip_{i}.mp4")
            output = f"output_{i}.mp4"

            cut_random_clip(video_path, clip_path, start_range=i * CLIP_INTERVAL)
            transcript = transcribe_audio(clip_path)
            enhance_clip(clip_path, transcript, output)

        print("✅ All clips processed!")

if __name__ == "__main__":
    main()
