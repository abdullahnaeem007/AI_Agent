# YouTube Video Automation

This project automates the process of generating a short video with voiceover, captions, and relevant YouTube clips based on a given story topic. It integrates OpenAI, ElevenLabs, and YouTube APIs to achieve this. Below is a step-by-step guide on how the script works.

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- Required dependencies: Install using `pip install -r requirements.txt`
- API keys for OpenAI, ElevenLabs, and YouTube (stored in a `.env` file)
- FFmpeg installed and added to the system PATH

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repo.git
   cd your-repo
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up API keys:** Create a `.env` file and add the following:
   ```sh
   OPENAI_API_KEY=your_openai_api_key
   ELEVEN_LABS_API_KEY=your_elevenlabs_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

## Step-by-Step Execution

### 1. Generate Story
The script takes a user input (story topic) and generates a story using OpenAI’s GPT-3.5 Turbo.
   ```sh
   user_input = input("Tell me a story topic: ")
   story = generate_story(user_input)
   ```

### 2. Generate Video Script
The generated story is then converted into a structured YouTube script using GPT-4o Mini.
   ```sh
   script = generate_script(story)
   ```

### 3. Generate Voice-Over
The script is converted into speech using ElevenLabs’ text-to-speech API, saving the output as an MP3 file.
   ```sh
   voiceover_file = generate_text_to_speech(script, file_name)
   ```

### 4. Generate Captions
Captions are created using OpenAI's Whisper model, saving them as both `.txt` and `.srt` subtitle files.
   ```sh
   captions = generate_speech_to_text(file_name, audio_duration)
   ```

### 5. Fetch Relevant YouTube Videos
Relevant YouTube videos are searched and retrieved using the YouTube Data API.
   ```sh
   videos = search_youtube_videos(user_input)
   ```

### 6. Download YouTube Videos
The fetched YouTube videos are downloaded using `yt_dlp`.
   ```sh
   download_videos = [download_video(url) for url in videos]
   ```

### 7. Edit and Compile Videos
The downloaded videos are trimmed and merged to match the voiceover duration.
   ```sh
   compiled_video = edit_videos(download_videos, audio_duration)
   ```

### 8. Add Captions to Video
The generated `.srt` file is added as subtitles to the video using FFmpeg.
   ```sh
   compiled_video_with_captions = add_captions_in_video(compiled_video, subtitle_file)
   ```

### 9. Add Voice-Over to Final Video
The generated voice-over is added as the final audio track to the compiled video.
   ```sh
   final_video = add_voiceover_in_video(compiled_video_with_captions, voiceover_file)
   ```

### 10. Output Final Video
The final processed video is saved as `final_video.mp4`.
   ```sh
   print("Final video saved as:", final_video)
   ```

## Usage
Run the script by executing:
```sh
python AI_Agent.py
```
Follow the prompts to generate a video based on your chosen story topic.

## Dependencies
- `openai`
- `elevenlabs`
- `pydub`
- `googleapiclient`
- `yt_dlp`
- `moviepy`
- `ffmpeg`
- `dotenv`

## Notes
- Ensure all API keys are valid and correctly set up in the `.env` file.
- FFmpeg must be installed for proper video and subtitle processing.
- Video downloads are subject to YouTube’s terms and conditions.

## License
This project is open-source and free to use under the MIT License.

