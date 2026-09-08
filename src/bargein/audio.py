import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 320

#for error/warning reporting
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio status: {status}")

    print(f"Frames {frames}")
    print(f"Shape {indata.shape}")
    print(f"Samples {indata[:5]}")

def start_audio_stream():
    print("Starting microphone...")
    
    with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=CHUNK_SIZE,
            callback=audio_callback,
    ):
        while True:
            sd.sleep(1000)

if __name__ == "__main__":
    start_audio_stream()
