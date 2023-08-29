import requests
import os
import re
import time
import boto3
import json

def sanitize_filename(text):
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|\n]', '', text)
    
    # Replace spaces with underscores and limit length
    return sanitized.replace(' ', '_')[:10]

def get_amazon_polly_speech(text, voice, output_path, engine='neural'):
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    polly_client = boto3.client(
        'polly',
        region_name='us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # First request for the audio data
    audio_response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice,
        Engine=engine
    )

    # Second request for the speech mark data
    speech_mark_response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='json',
        VoiceId=voice,
        Engine=engine,
        SpeechMarkTypes=["word", "sentence"]
    )
    
    safe_text = sanitize_filename(text)
    audio_filename = os.path.join(output_path, f"{voice}_{safe_text}.mp3")
    json_filename = os.path.join(output_path, f"{voice}_{safe_text}.json")  # JSON file name

    # Save the audio file
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(audio_response['AudioStream'].read())
        
    # Convert raw speech mark data to list of JSON objects
    raw_data = speech_mark_response['AudioStream'].read().decode()
    marks = [json.loads(line) for line in raw_data.strip().split("\n")]
    
    # Save the list of JSON objects as a single JSON array
    with open(json_filename, 'w') as json_file:
        json.dump(marks, json_file)
    
    return audio_filename, json_filename
