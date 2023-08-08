# makeVideo.py
import moviepy
from moviepy.editor import AudioFileClip, concatenate_audioclips, CompositeVideoClip, VideoFileClip, AudioClip, concatenate_audioclips, ImageClip, concatenate_videoclips
import yt_dlp
import os
import random
from pathlib import Path
import random
import numpy as np
def make_rounded_mask(img_size, radius):
    """
    Make a rounded mask for an image of img_size.
    """
    y, x = np.ogrid[:img_size[1], :img_size[0]]
    mask = (x - img_size[0] / 2) ** 2 + (y - img_size[1] / 2) ** 2 > (img_size[0] / 2 - radius) ** 2
    return mask

def calculate_start_time(video, total_duration):
    min_start = 3 * 60  # 3 minutes in seconds
    max_end = video.duration - (5 * 60)  # video.duration gives the total length of the video in seconds
    
    max_start = max_end - (total_duration + 10)  # Ensuring that the clip doesn't end within the last 5 minutes
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

def concatenate_audio_clips_with_pause(folder_path):
    audio_files = sorted([file for file in folder_path.iterdir() if file.suffix == ".mp3"], 
                         key=lambda x: int(x.stem.split('_')[0]))
    
    audio_clips = [AudioFileClip(str(audio_file)) for audio_file in audio_files]
    
    # Add pauses between the clips
    pauses = [AudioClip(lambda t: 0, duration=0.5) for _ in range(len(audio_clips)-1)]
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
    
    # Calculate start time and end time for the subclip
    start_time = calculate_start_time(video, total_duration)
    end_time = start_time + total_duration + 10  # 10 seconds extra as you mentioned
    
    # Create subclip
    subclip = video.subclip(start_time, end_time)
    
    # Crop and resize
    cropped_and_resized_video = crop_and_resize_video(subclip)
    
    # Concatenate audio clips with pauses
    audio_folder = Path(selected_folder) / "audio"
    concatenated_audio = concatenate_audio_clips_with_pause(audio_folder)

    
    # Find the duration of the first audio clip
    first_audio_path = audio_folder / "1_sentence.mp3"
    first_audio_duration = AudioFileClip(str(first_audio_path)).duration
    
    # Load title card image
    title_card_path = Path(selected_folder) / "title_card.png"
    title_card = (ImageClip(str(title_card_path))
              .resize(0.84)  # Scale the image to 84% of its original size
              .set_duration(first_audio_duration))

    # Overlay the title card image on the video for the duration of the first audio clip
    video_with_title_for_first_audio = CompositeVideoClip([
        cropped_and_resized_video.subclip(0, first_audio_duration),
        title_card.set_position("center")  # Change "center" to desired position
    ])    

    # The part of the video without a title card (Maybe add subtitles here)
    video_without_title_for_remaining = cropped_and_resized_video.subclip(first_audio_duration, cropped_and_resized_video.duration)
    
    final_video = concatenate_videoclips([video_with_title_for_first_audio, video_without_title_for_remaining])
    
    # Set audio of the video to the concatenated audio
    video_with_audio_and_title = final_video.set_audio(concatenated_audio)

    # Save the processed video with audio and title card to selected_folder
    output_path = Path(selected_folder) / "video.mp4"
    video_with_audio_and_title.write_videofile(str(output_path))
