import requests
import os
import re
import time
import boto3

def sanitize_filename(text):
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|\n]', '', text)
    
    # Replace spaces with underscores and limit length
    return sanitized.replace(' ', '_')[:10]

def get_streamelements_speech(text, voice, output_path):
    BASE_URL = "https://api.streamelements.com/kappa/v2/speech"
    params = {"voice": voice, "text": text}

    MAX_RETRIES = 5  # You can adjust this number based on your needs
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()

            safe_text = "".join(ch for ch in text[:10] if ch.isalnum())
            audio_filename = os.path.join(output_path, f"{voice}_{safe_text}.mp3")

            with open(audio_filename, 'wb') as audio_file:
                audio_file.write(response.content)

            return audio_filename

        except requests.exceptions.HTTPError as e:
            # Check if the error status code corresponds to "Too Many Requests"
            if response.status_code == 429:
                time.sleep(30)  # wait for 30 seconds before retrying
            else:
                raise e  # If it's a different HTTP error, raise it immediately
    raise Exception("Max retries reached. Exiting.")

def get_amazon_polly_speech(text, voice, output_path, engine='neural'):
    polly_client = boto3.client('polly', region_name='us-east-1')
    
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice,
        Engine=engine
    )
    
    safe_text = sanitize_filename(text)
    audio_filename = os.path.join(output_path, f"{voice}_{safe_text}.mp3")

    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(response['AudioStream'].read())
    
    return audio_filename
