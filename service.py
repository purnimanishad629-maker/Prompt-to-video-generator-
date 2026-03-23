import os
from gtts import gTTS

def generate_audio_gtts(text, audio_folder, video_id):
    """Generate audio using gTTS (free, no API key needed)"""
    try:
        audio_path = os.path.join(audio_folder, f'{video_id}_gtts.mp3')
        
        # gTTS supports Hindi
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save(audio_path)
        
        return audio_path
    except Exception as e:
        print(f"gTTS error: {e}")
        return None

def generate_audio_elevenlabs(text, api_key, audio_folder, video_id):
    """Generate audio using ElevenLabs (better quality)"""
    try:
        from elevenlabs import generate, set_api_key
        
        set_api_key(api_key)
        
        audio_path = os.path.join(audio_folder, f'{video_id}_eleven.mp3')
        
        # Generate audio
        audio = generate(
            text=text,
            voice="Hindi Female",  # You can change this
            model="eleven_monolingual_v1"
        )
        
        # Save audio
        with open(audio_path, 'wb') as f:
            f.write(audio)
        
        return audio_path
        
    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return None
