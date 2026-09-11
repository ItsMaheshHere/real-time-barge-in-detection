import sys
from pathlib import Path
import sounddevice as sd
import numpy as np

# Add src directory to path so we can import our new package
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from bargein.vad import SileroVAD

SAMPLE_RATE = 16000
# Silero VAD typically works best with 512 samples (32ms) at 16kHz
FRAME_SIZE = 512
CHANNELS = 1

vad = SileroVAD(sample_rate=SAMPLE_RATE, threshold=0.5)

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio status: {status}")

    # indata is shape (frames, channels), e.g. (512, 1). We need a 1D array.
    audio_chunk = indata[:, 0]
    
    # Get the exact probability from our new class
    prob = vad.get_speech_probability(audio_chunk)
    
    bar = "█" * int(prob * 20)
    if prob >= 0.5:
        print(f"HUMAN     [{bar:<20}] {prob:.3f}")
    else:
        print(f"NOT HUMAN [{bar:<20}] {prob:.3f}")


with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",  # Silero uses float32 instead of int16
    blocksize=FRAME_SIZE,
    callback=audio_callback,
):
    while True:
        sd.sleep(1000)