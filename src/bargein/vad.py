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