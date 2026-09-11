import sounddevice as sd
import webrtcvad


SAMPLE_RATE = 16000
FRAME_DURATION_MS = 20
CHANNELS = 1

FRAME_SIZE = SAMPLE_RATE * FRAME_DURATION_MS // 1000

vad = webrtcvad.Vad(3)


def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio status: {status}")

    audio_bytes = indata.tobytes()

    is_speech = vad.is_speech(audio_bytes, SAMPLE_RATE)

    if is_speech:
        print("HUMAN")
    else:
        print("NOT HUMAN")


print("Starting microphone VAD...")
print("Speak into the microphone.")
print("Press Ctrl+C to stop.")

with sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16",
    blocksize=FRAME_SIZE,
    callback=audio_callback,
):
    while True:
        sd.sleep(1000)
