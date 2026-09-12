import sys
from pathlib import Path
import sounddevice as sd

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from bargein.stt import GroqSTT

def run_stt_test():
    try:
        stt = GroqSTT()
    except Exception as e:
        print("Failed")
        return

    sample_rate = 16000
    duration = 5
    
    print("Recording")
    
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait() 
    
    print("Recording finished")
    
    # The recording is shape (frames, channels), we need 1D array
    audio_data = recording[:, 0]
    
    # Send to STT
    text = stt.transcribe(audio_data, sample_rate)
    if text:
        print(f'"{text}"')
    else:
        print("No text detected")

if __name__ == "__main__":
    run_stt_test()