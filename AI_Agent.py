from openai import OpenAI
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import math
from pydub import AudioSegment
from datetime import timedelta
import googleapiclient.discovery
import yt_dlp
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import ffmpeg
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVEN_LABS_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

openai_client = OpenAI(api_key = openai_api_key)
elevenlabs_client = ElevenLabs(api_key = elevenlabs_api_key)
youtube_client = googleapiclient.discovery.build("youtube", "v3", developerKey = youtube_api_key)

def generate_story(input):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": input
            }
        ]
    )

    response = completion.choices[0].message.content
    return response

def generate_script(input):
    completion = openai_client.chat.completions.create(
        model= "gpt-4o-mini",
        messages = [
            {
                "role" : "system",
                "content": "You are now a Professional YouTube Script Writer. I’m working on this YouTube Video Story that I will provide and I need you to write a 100 word long YouTube script. \n Here is the formula you’re going to follow: \n You need to follow a formula that goes like this: Hook (3–5 seconds) > Intro (5 seconds) > Body/Explanation > Introduce a Problem/Challenge > Exploration/Development > Climax/Key Moment > Conclusion/Summary > Call to Action (5 seconds max). \n IMPORTANT: THE TOTAL VIDEO SHOULD BE OF 30 seconds \n Here are some Instructions I need you to Keep in mind while writing this script: \n Hook (That is Catchy and makes people invested into the video, maxi 2 lines long) \n Intro (This should provide content about the video and should give viewers a clear reason of what’s inside the video and sets up an open loop) \n Body (This part of the script is the bulk of the script and this is where all the information is delivered, use storytelling techniques to write this part and make sure this is as informative as possible, don’t de-track from the topic. I need this section to have everything a reader needs to know from this topic) \n Call to Action (1–2 lines max to get people to watch the next video popping on the screen) \n Here are some more points to keep in mind while writing this script: \n Hook needs to be strong and to the point to grab someone’s attention right away and open information gaps to make them want to keep watching. Don’t start a video with ‘welcome’ because that’s not intriguing. Open loops and information gaps to keep the viewer craving more. Make the script very descriptive. \n In terms of the Hook: \n Never Start the Script Like This: “Hi guys, welcome to the channel, my name’s…” So, here are three types of hooks you can use instead, with examples. \n IMPORTANT: GENERATE A SCRIPT WITHOUT ANY HEADINGS AND IT SHOULD BE A SINGLE PARAGRAPH"
            },
            {
                "role" : "user",
                "content" : f"Generate me a script for the following story: \n {input}" 
            }
        ]
    )

    response = completion.choices[0].message.content
    return response

def generate_text_to_speech(input, file_name):
    output_file = f"{file_name}.mp3"
    audio_stream = elevenlabs_client.text_to_speech.convert_as_stream(
        text = input,
        voice_id = "29vD33N1CtxCmqQRPOHJ",
        model_id =  "eleven_flash_v2_5"
    )
 
    with open(output_file, "wb") as audio_file:
        for audio_chunk in audio_stream:
            audio_file.write(audio_chunk)
    
    return output_file

def get_audio_duration(file_name):
    file = f"{file_name}.mp3"
    audio = AudioSegment.from_file(file)
    return audio.duration_seconds

def generate_speech_to_text(file_name, audio_duration):
    audio_file_path = f"{file_name}.mp3"
    
    with open(audio_file_path, "rb") as audio_file:
        response = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    transcript_text = response.text
    text_file_path = f"{file_name}.txt"
    
    with open(text_file_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)
        print(f"Captions for voiceover saved in {text_file_path}")
    
    srt_file_path = f"{file_name}.srt"
    words = transcript_text.split()
    total_words = len(words)
    avg_word_time = audio_duration / total_words
    
    srt_content = ""
    start_time = timedelta(seconds=0)
    caption_length = 8
    
    for i in range(math.ceil(total_words / caption_length)):
        chunk = words[i * caption_length: (i + 1) * caption_length]
        chunk_text = " ".join(chunk)
        end_time = start_time + timedelta(seconds=len(chunk) * avg_word_time)
        
        start_time_str = f"{str(start_time)[:-3]},000"
        end_time_str = f"{str(end_time)[:-3]},000"
        
        srt_content += f"{i + 1}\n"
        srt_content += f"{start_time_str} --> {end_time_str}\n"
        srt_content += f"{chunk_text}\n\n"
        
        start_time = end_time
    
    with open(srt_file_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    print(f"SRT captions saved as {srt_file_path}")



def search_youtube_videos(query, max_results=5):
    request = youtube_client.search().list(
        q = query,
        part = "snippet",
        maxResults = max_results,
        type = "video"
    )

    response = request.execute()

    video_urls = [
            f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            for item in response.get("items", [])
        ]
    return video_urls

def download_video(url, output_path = "videos/"):
    os.makedirs(output_path, exist_ok = True)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': f'{output_path}%(title)s.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info_dict)
    
def edit_videos(video_files, total_duration):
    clips = [VideoFileClip(f) for f in video_files]
    each_clip_duration = total_duration / len(clips)

    trimmed_clips = [clip.subclip(0 , min(each_clip_duration, clip.duration)) for clip in clips]
    final_video = concatenate_videoclips(trimmed_clips, method = "compose")
    final_video.write_videofile("compiled_video.mp4", codec = "libx264", fps = 24)
    return "compiled_video.mp4"

def add_voiceover_in_video(video_file, audio_file):
    video = VideoFileClip(video_file).without_audio()
    audio = AudioFileClip(audio_file)
    final_video = video.set_audio(audio)
    final_video.write_videofile("final_video.mp4", codec = "libx264", fps = 24) 
    return "final_video.mp4"

def add_captions_in_video(video_file, subtitle_file):
    print(f"Subtitle file path: {subtitle_file}")
    output_file = "compiled_video_with_subtitles.mp4"
    ffmpeg.input(video_file).output(output_file, vf=f"subtitles='{subtitle_file}'").global_args('-map', '0:v', '-map', '0:a').run()

if __name__ == "__main__":
    file_name = "test"
    print("STEP 1: Generating Story using gpt-3.5-turbo")
    user_input = input("Tell me a story topic: ")
    story = generate_story(user_input)
    print(story)

    print("\n \n STEP 2: Generating Video Script using gpt-4o-mini")
    script = generate_script(story)
    print(script)

    print("STEP 3: Generating Voice-Over for script using ElevenLabs")
    voiceover_file = generate_text_to_speech(script, file_name)

    audio_duration  = get_audio_duration(file_name)

    print("STEP 4: Generating captions for the voice-over:")
    captions = generate_speech_to_text(file_name, audio_duration)
    print(captions)

    print("STEP 5: Fetch relevant videos url from youtube:")
    videos = search_youtube_videos(user_input)
    print(videos)

    print("STEP 6: Downloaded videos from their respective urls")
    download_videos = [download_video(url) for url in videos]

    print("STEP 7: Compiling downloaded videos:")
    compiled_video = edit_videos(download_videos, audio_duration)

    subtitle_file = f"{file_name}.srt"
    print(subtitle_file)

    print("STEP 9: Adding captions in final video:")
    compiled_video_with_captions = add_captions_in_video(compiled_video, subtitle_file)

    print("STEP 8: Adding voice in final video:")
    final_video = add_voiceover_in_video(compiled_video_with_captions, voiceover_file)


    print("Final video saved as:", final_video)