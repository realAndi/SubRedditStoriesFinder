# makeVideo.py
import moviepy
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip
import yt_dlp
import os
import random
from pathlib import Path
import sys

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
    resized_video = cropped_video.resize(new_ratio)

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

def make_video(background_video, captions, output_file, total_duration):
# Cut the background video if its duration exceeds total_duration
    if background_video.duration > total_duration:
        background_video = background_video.subclip(0, total_duration)

    # Use the background video
    background = background_video

    # Create a TextClip for each caption
    caption_clips = []
    for caption in captions:
        txt_clip = TextClip(caption, fontsize=24, color='white', font='Arial').set_duration(2)
        caption_clips.append(txt_clip)

    # Overlay the captions on the background
    video = CompositeVideoClip([background] + caption_clips)

    # Write the result to a file
    video.write_videofile(output_file, fps=60)  # fps = frames per second


if __name__ == "__main__":
    total_duration = float(sys.argv[2])
    
    assets_folder = Path("assets")
    assets_folder.mkdir(exist_ok=True)  # Create assets folder if it doesn't exist
    video_filename = assets_folder / "bbswitzer-parkour.mp4"
    video_url = "https://www.youtube.com/watch?v=n_Dv4JMiwK8"
    download_video_if_not_exists(video_url, video_filename)

    # In your main function where you download the video...
    video_clip = VideoFileClip(str(video_filename))

    # Crop and resize video for TikTok
    video_clip = crop_and_resize_video(video_clip)

    # Get the total duration of the video
    video_duration = video_clip.duration

    # Choose a random start time
    start_time = random.uniform(0, video_duration - total_duration)
    captions = ["Caption 1", "Caption 2", "Caption 3"]
    make_video(video_clip, captions, "output.mp4", total_duration)

