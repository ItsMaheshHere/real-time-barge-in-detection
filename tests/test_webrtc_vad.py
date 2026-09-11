import webrtcvad

SAMPLE_RATE = 16000
FRAME_DURATION_MS=20

vad = webrtcvad.Vad(2)

frame_size = SAMPLE_RATE * FRAME_DURATION_MS // 1000

silence = b"\x00\x00" * frame_size

is_speech = vad.is_speech(silence, SAMPLE_RATE)

print(f"Speech detected: {is_speech}")