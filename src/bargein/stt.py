import os
import io
import scipy.io.wavfile
import numpy as np
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqSTT:
    
    def __init__(self):
        self.client = Groq()
        
        self.model = "whisper-large-v3-turbo"

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        if len(audio_data) == 0:
            return ""

        # The microphone gives us raw numbers. Groq expects a WAV file.
        # We create a fake WAV file in memory so we don't have to save it to your hard drive.
        wav_io = io.BytesIO()
        
        # Scipy wants the audio as 16-bit integers to make a proper WAV file
        audio_int16 = (audio_data * 32767).astype(np.int16)
        scipy.io.wavfile.write(wav_io, sample_rate, audio_int16)
        
        wav_io.seek(0)
        
        try:
            print("[STT] Sending audio to Groq")
            transcription = self.client.audio.transcriptions.create(
                file=("audio.wav", wav_io.read()),
                model=self.model,
                response_format="text",
                language="en" # Forcing English makes it even faster
            )
            return transcription.strip()
            
        except Exception as e:
            print(f"  [STT Error]: {e}")
            return ""