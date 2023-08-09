import whisper



def transcribe_with_whisper(audio_file_path):
    """
    Transcribe an audio file using OpenAI's Whisper ASR API.

    Args:
        audio_file_path (str): Path to the audio file to be transcribed.

    Returns:
        str: Transcribed text.
    """
    model = whisper.load_model("base.en")
    result = model.transcribe(audio_file_path)
    return result['segments']
