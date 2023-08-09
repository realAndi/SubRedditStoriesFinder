# makeVideo.py
import moviepy
from moviepy.editor import *
import yt_dlp
import os
import random
from pathlib import Path
import random
import numpy as np
from whisper_transcription import transcribe_with_whisper

def generate_captions_from_transcription(transcription_dict):    
    captions = []
    for segment in transcription_dict:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text']

        text_clip = TextClip(text, fontsize=56, color='white', size=(int(1080*9/16) - 200, 1080),
                    font="Futura-PT-Bold", method='caption', stroke_color='black', 
                    stroke_width=2, align="center", kerning=-1, transparent=True)
        text_clip = text_clip.set_pos(('center')).set_start(start_time).set_end(end_time)

        captions.append(text_clip)

    return captions


def overlay_captions_on_video(video, captions):
    # Start from the beginning of the video
    last_end_time = 0
    segments = []

    for caption in captions:
        # Append a portion of the video without captions
        if last_end_time < caption.start:
            segments.append(video.subclip(last_end_time, caption.start))

        # Append a portion of the video with the caption overlay
        segments.append(CompositeVideoClip([
            video.subclip(caption.start, caption.end),
            caption.set_position(('center', 'bottom')).set_start(0)
        ]))

        last_end_time = caption.end

    if last_end_time > 99.65:
        last_end_time = 99.64
    if last_end_time < (video.duration):
        segments.append(video.subclip(last_end_time))


    # Concatenate all segments
    result = concatenate_videoclips(segments)

    return result



def calculate_start_time(video, total_duration):
    min_start = 3 * 60  # 3 minutes in seconds
    max_end = video.duration - (5 * 60)  # video.duration gives the total length of the video in seconds
    
    max_start = max_end - (total_duration + 3)  # Ensuring that the clip doesn't end within the last 5 minutes
    return random.uniform(min_start, max_start)


def crop_and_resize_video(video_clip, new_ratio=(9, 16)):
    """
    Crops and resizes a video clip to a new ratio.
    """
    # Calculate new width and height
    width, height = video_clip.size
    new_height = new_ratio[1] * (width / new_ratio[0])
    new_width = new_ratio[0] * (height / new_ratio[1])
    # Determine dimensions to use (whichever dimension doesn't result in cropping out of bounds)
    if new_height <= height:
        crop_height = new_height
        crop_width = width
    else:
        crop_height = height
        crop_width = new_width
    # Calculate crop coordinates (center crop)
    x_center = width / 2
    y_center = height / 2
    x1 = x_center - (crop_width / 2)
    y1 = y_center - (crop_height / 2)
    # Crop and resize the video
    cropped_video = video_clip.crop(x1, y1, x1 + crop_width, y1 + crop_height)
    # resized_video = cropped_video.resize(new_ratio)
    resized_video = cropped_video.resize(height=1080, width=int(1080*9/16))

    return resized_video

def download_video_if_not_exists(url, output_filename):
    if not os.path.exists(output_filename):
        ydl_opts = {
            "format": "bestvideo[height<=1080][ext=mp4]",
            "outtmpl": output_filename,
            "retries": 10,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    else:
        print('You already have the video downloaded! Skipping this step!')


def concatenate_audio_clips_with_pause(folder_path, start_index=1):
    audio_files = sorted([file for file in folder_path.iterdir() if file.suffix == ".mp3"], 
                         key=lambda x: int(x.stem.split('_')[0]))
    
    # Start from the specified index
    audio_files = audio_files[start_index-1:]
    
    audio_clips = [AudioFileClip(str(audio_file)) for audio_file in audio_files]
    
    # Add pauses between the clips
    pauses = [AudioClip(lambda t: 0, duration=0.4) for _ in range(len(audio_clips)-1)]
    audio_sequence = [audio_clips[0]]

    for i, pause in enumerate(pauses):
        audio_sequence.append(pause)
        audio_sequence.append(audio_clips[i+1])
    
    concatenated_audio = concatenate_audioclips(audio_sequence)
    
    return concatenated_audio


def make_video(selected_folder, total_duration):
    # Convert total_duration from string to float
    total_duration = float(total_duration)
    
    # Download the video
    assets_folder = Path("assets")
    assets_folder.mkdir(exist_ok=True)  # Create assets folder if it doesn't exist
    video_filename = assets_folder / "bbswitzer-parkour.mp4"
    video_url = "https://www.youtube.com/watch?v=n_Dv4JMiwK8"
    download_video_if_not_exists(video_url, video_filename)
    
    # Load the video using moviepy
    video = VideoFileClip(str(assets_folder / "bbswitzer-parkour.mp4"))
    
    print("Video Loaded")
    # Calculate start time and end time for the subclip
    start_time = calculate_start_time(video, total_duration)
    end_time = start_time + total_duration + 10  # 10 seconds extra as you mentioned
    
    print("Calculated Title Card duration")

    # Create subclip
    subclip = video.subclip(start_time, end_time)
    
    # Crop and resize
    cropped_and_resized_video = crop_and_resize_video(subclip)
    print("Resized to 9:16 Aspect Ratio")


    # Concatenate audio clips with pauses
    audio_folder = Path(selected_folder) / "audio"
    concatenated_audio = concatenate_audio_clips_with_pause(audio_folder, start_index=2)

    
    # Find the duration of the first audio clip
    first_audio_path = audio_folder / "1_sentence.mp3"
    first_audio_duration = AudioFileClip(str(first_audio_path)).duration
    first_audio_clip = AudioFileClip(str(first_audio_path))    

    # Load title card image
    title_card_path = Path(selected_folder) / "title_card.png"
    title_card = (ImageClip(str(title_card_path))
              .resize(0.78)  # Scale the image to 84% of its original size
              .set_duration(first_audio_duration))



    # Overlay the title card image on the video for the duration of the first audio clip
    video_with_title_for_first_audio = CompositeVideoClip([
        cropped_and_resized_video.subclip(0, first_audio_duration),
        title_card.set_position("center")  # Change "center" to desired position
    ]).set_audio(first_audio_clip)    

    print("Added Title Card")

    # The part of the video without a title card (Maybe add subtitles here)
    video_without_title_for_remaining = (cropped_and_resized_video  
        .subclip(first_audio_duration, cropped_and_resized_video.duration)
        .set_audio(concatenated_audio))
    

    # Save the video with that needs captions so we can transcribe
    audio_segment = video_without_title_for_remaining.audio
    audio_segment_filename = str(Path(selected_folder) / "staging_audio.mp3")  # Change to .mp3 since it's audio only
    audio_segment.write_audiofile(audio_segment_filename)

    # OpenAi Whisper
    print("Using OpenAI Whisper to get transcript.")
    transcription = transcribe_with_whisper(audio_segment_filename)
    print("Done. Generating subtitles...")
    # Generate captions from the transcription
    captions = generate_captions_from_transcription(transcription)

    video_with_captions = overlay_captions_on_video(video_without_title_for_remaining, captions)

    print("Merging videos")
    final_video = concatenate_videoclips([video_with_title_for_first_audio, video_with_captions])

    print("Rendering! We're almost done!")
    # Save the video with captions
    output_path = Path(selected_folder) / "final.mp4"
    # The tiktok speed
    final_video = final_video.fx(vfx.speedx, 1.03)
    final_video.write_videofile(str(output_path))


