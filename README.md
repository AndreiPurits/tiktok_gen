# 🎬 YouTube to TikTok Clip Generator

This Python script automates the creation of TikTok-style clips from YouTube videos. It downloads a YouTube video, cuts multiple short segments, adds animated word-by-word subtitles, overlays background music and a satisfying background video.

## ✨ Features

- Automatically downloads and trims a YouTube video into short clips
- Adds background TikTok-style “satisfying” videos
- Adds background music from local folder
- Word-by-word animated subtitles using OpenAI Whisper
- Outputs multiple processed TikTok-ready clips

## 📂 Folder Structure

```
project-root/
│
├── backgrounds/        # Add short looping background videos here (e.g., slime, ASMR, paint mixing)
├── music/              # Add royalty-free background .mp3 music here
├── main.py             # Main script
└── output_0.mp4        # Example result file
```

## 🔧 Requirements

- Python 3.9+
- [ImageMagick](https://imagemagick.org/index.php) (with path set correctly on Windows)
- ffmpeg installed and accessible in your PATH

### Python packages
- moviepy
- yt-dlp
- openai-whisper


## The script will:

- Download the video from VIDEO_URL
- Cut several short clips (15–35s each)
- Transcribe audio using Whisper
- Add subtitles + background visuals/music
- Save the result as output_0.mp4, output_1.mp4, etc.

## Notes
- Subtitles require ImageMagick installed and configured
- Place your background .mp4 and music .mp3 in the respective folders
- Whisper transcription can be slow depending on model size and hardware 
