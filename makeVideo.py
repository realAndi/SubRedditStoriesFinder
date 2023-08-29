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
import json

def generate_captions(json_filename, words_per_group=3):
    with open(json_filename, 'r') as json_file:
        marks = json.load(json_file)

    sentences = [mark for mark in marks if mark['type'] == 'sentence']
    words = [mark for mark in marks if mark['type'] == 'word']

    text_clips = []
    for sentence in sentences:
        original_text = sentence['value']
        sentence_words = [word for word in words if word['start'] >= sentence['start'] and word['end'] <= sentence['end']]
        word_groups = [sentence_words[i:i+words_per_group] for i in range(0, len(sentence_words), words_per_group)]

        for idx, group in enumerate(word_groups):
            start_idx = group[0]['start'] - sentence['start']
            end_idx = group[-1]['end'] - sentence['start'] + 1

            # I know this is ghetto, I don't care.
            if start_idx > 0 and original_text[start_idx-1] == '"':
                start_idx -= 1
            if end_idx < len(original_text) and original_text[end_idx] == '"':
                end_idx += 1

            phrase = original_text[start_idx:end_idx]


            group_start_time = group[0]['time'] / 1000
            if idx < len(word_groups) - 1:  # if not the last group
                group_end_time = word_groups[idx + 1][0]['time'] / 1000 - 0.01  # start of the next group minus 10ms
            else:  # for the last group
                group_end_time = group[-1]['time'] / 1000 + 0.5  # last word's time plus half a second

            text_clip = TextClip(phrase, fontsize=56, color='white', 
                            size=(int(1080*9/16) - 200, 1080),
                            font="Futura-PT-Bold", method='caption', 
                            stroke_color='black', stroke_width=2, 
                            align="center", kerning=-1, transparent=True)

            text_clip = text_clip.set_pos(('center')).set_start(group_start_time).set_end(group_end_time)
            text_clips.append(text_clip)

    return text_clips







def overlay_captions_on_video(video, captions, seconds_to_add=0):
    last_end_time = 0
    segments = []

    for caption in captions:
        if last_end_time < caption.start and last_end_time < video.duration:
            segments.append(video.subclip(last_end_time, min(caption.start, video.duration)))

        clip_start = min(caption.start, video.duration)
        clip_end = min(caption.end, video.duration)
        
        if clip_start >= video.duration:
            break

        segments.append(CompositeVideoClip([
            video.subclip(clip_start, clip_end),
            caption.set_position(('center', 'bottom')).set_start(0)
        ]))

        last_end_time = caption.end

    last_end_time = min(last_end_time, video.duration, 99.65)
    extended_end_time = last_end_time + seconds_to_add

    if last_end_time < video.duration:
        segment_end_time = min(extended_end_time, video.duration)
        last_end_time = video.duration
        if last_end_time < segment_end_time:
            segments.append(video.subclip(last_end_time, segment_end_time))

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


def make_video(selected_folder, total_duration, useCaptions):
    # Convert total_duration from string to float
    total_duration = float(total_duration)
    
    # Download the video
    assets_folder = Path("assets")
    assets_folder.mkdir(exist_ok=True)  # Create assets folder if it doesn't exist
    video_filename = assets_folder / "bbswitzer-parkour.mp4"
    video_url = "https://www.youtube.com/watch?v=n_Dv4JMiwK8"
    download_video_if_not_exists(video_url, video_filename)
    
    # Load the video using moviepy
    video = VideoFileClip(str(assets_folder / "parkour2.mp4"))
    
    print("Video Loaded")
    # Calculate start time and end time for the subclip
    start_time = calculate_start_time(video, total_duration)
    end_time = start_time + total_duration + 2 # Safety measures
    
    print("Calculated Title Card duration")

    # Create subclip
    subclip = video.subclip(start_time, end_time)
    
    # Crop and resize
    cropped_and_resized_video = crop_and_resize_video(subclip)
    print("Resized to 9:16 Aspect Ratio")


    # Concatenate audio clips with pauses
    audio_folder = Path(selected_folder) / "audio"
    
    # Find the duration of the first audio clip
    first_audio_path = audio_folder / "1_sentence.mp3"
    first_audio_duration = AudioFileClip(str(first_audio_path)).duration
    first_audio_clip = AudioFileClip(str(first_audio_path))    

    remaining_audio_path = audio_folder / "2_sentence.mp3"
    remaining_audio_duration = AudioFileClip(str(remaining_audio_path)).duration
    remaining_audio_clip = AudioFileClip(str(remaining_audio_path))    

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

    post_title_duration = total_duration - first_audio_duration

    # The part of the video without a title card
    video_without_title_for_remaining_end_time = first_audio_duration + post_title_duration

    # Ensure the video has a minimum duration of 1 minute and 1 second
    seconds_to_add = 0
    min_duration = 61
    if post_title_duration < min_duration:
        seconds_to_add = min_duration - remaining_audio_duration
    
    video_without_title_for_remaining = (cropped_and_resized_video  
        .subclip(first_audio_duration, video_without_title_for_remaining_end_time + seconds_to_add)
        .set_audio(remaining_audio_clip))
    

    print("Total duration of video so far " + str(video_without_title_for_remaining.duration))

    # Save the video with that needs captions so we can transcribe
    audio_segment = video_without_title_for_remaining.audio
    audio_segment_filename = str(Path(selected_folder) / "staging_audio.mp3")  # Change to .mp3 since it's audio only
    audio_segment.write_audiofile(audio_segment_filename)
    final_video = None
    if useCaptions:
        # # OpenAi Whisper (Legacy code, ignore if you dont need it. )
        # print("Using OpenAI Whisper to get transcript.")
        # transcription = transcribe_with_whisper(audio_segment_filename)
        # print("Done. Generating subtitles...")
        # # Generate captions from the transcription
        # captions = generate_captions_from_transcription(transcription)

        captions = generate_captions(audio_folder / '2_mark.json')
        video_with_captions = overlay_captions_on_video(video_without_title_for_remaining, captions, seconds_to_add)





        print("Merging videos")
        final_video = concatenate_videoclips([video_with_title_for_first_audio, video_with_captions])
    else:
        print("Skipping captions. Merging videos.")
        final_video = concatenate_videoclips([video_with_title_for_first_audio, video_without_title_for_remaining])

    print("Rendering! We're almost done!")
    # Save the video with captions
    output_path = Path(selected_folder) / "final.mp4"
    # The tiktok speed
    final_video.write_videofile(str(output_path))


