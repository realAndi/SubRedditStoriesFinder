import requests
import os
import re



def sanitize_filename(text):
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|\n]', '', text)
    
    # Replace spaces with underscores and limit length
    return sanitized.replace(' ', '_')[:10]

def get_streamelements_speech(text, voice, output_path):
    BASE_URL = "https://api.streamelements.com/kappa/v2/speech"
    params = {"voice": voice, "text": text}
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    safe_text = "".join(ch for ch in text[:10] if ch.isalnum())
    audio_filename = os.path.join(output_path, f"{voice}_{safe_text}.mp3")  

    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(response.content)

    return audio_filename


