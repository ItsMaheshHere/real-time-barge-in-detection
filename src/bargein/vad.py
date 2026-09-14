import torch
from silero_vad import load_silero_vad

class SileroVAD:

    def __init__(self, sample_rate=16000, threshold=0.5):
        self.model = load_silero_vad()
        self.sample_rate = sample_rate
        self.threshold = threshold

    def get_speech_probability(self, audio_chunk):
        tensor = torch.from_numpy(audio_chunk).float()
        return self.model(tensor, self.sample_rate).item()

    def is_speech(self, audio_chunk):
        return self.get_speech_probability(audio_chunk) >= self.threshold


class VADFilter:
    """
    Temporal filter to smooth out VAD predictions.
    Prevents short noises from triggering speech (requires min_speech_frames).
    Prevents pausing between words from ending speech (requires min_silence_frames).
    """

    def __init__(self, min_speech_frames=3, min_silence_frames=10):
        self.min_speech_frames = min_speech_frames
        self.min_silence_frames = min_silence_frames
        
        self.speech_frame_count = 0
        self.silence_frame_count = 0
        
        self.is_currently_speaking = False

    def process(self, is_speech_frame):
        if is_speech_frame:
            self.speech_frame_count += 1
            self.silence_frame_count = 0
        else:
            self.silence_frame_count += 1
            self.speech_frame_count = 0

        if not self.is_currently_speaking:
            # We are in silence. Do we have enough speech frames to switch to speaking?
            if self.speech_frame_count >= self.min_speech_frames:
                self.is_currently_speaking = True
        else:
            # We are speaking. Do we have enough silence frames to switch to silence?
            if self.silence_frame_count >= self.min_silence_frames:
                self.is_currently_speaking = False

        return self.is_currently_speaking

    def reset(self):
        self.speech_frame_count = 0
        self.silence_frame_count = 0
        self.is_currently_speaking = False