import sys
import collections
import queue
import threading
from pathlib import Path
import numpy as np
import sounddevice as sd

src_path = str(Path(__file__).parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from bargein.vad import SileroVAD, VADFilter
from bargein.stt import GroqSTT
from bargein.llm import GroqLLM
from bargein.tts import EdgeTTS
from bargein.bargein import BargeInDetector

SAMPLE_RATE = 16000
FRAME_SIZE = 512


class VoiceAssistant:

    def __init__(self):
        self.vad = SileroVAD(sample_rate=SAMPLE_RATE, threshold=0.5)
        self.vad_filter = VADFilter(min_speech_frames=3, min_silence_frames=15)

        self.stt = GroqSTT()
        self.llm = GroqLLM()
        self.tts = EdgeTTS()
        self.barge_in_detector = BargeInDetector(self.tts, self.vad_filter)

        # Keeps the last 15 frames in memory
        self.lookback_buffer = collections.deque(maxlen=15)
        self.audio_buffer = []
        self.was_speaking = False

        self.speech_queue = queue.Queue()
        self.running = True

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")

        audio_chunk = indata[:, 0].copy()
        self.lookback_buffer.append(audio_chunk)

        prob = self.vad.get_speech_probability(audio_chunk)
        is_confirmed = self.vad_filter.process(prob >= 0.5)

        # BARGE-IN CHECK: We check this on every single audio frame
        if self.barge_in_detector.check_barge_in(is_confirmed):
            # The user just interrupted! Clear old audio and start recording them instantly.
            self.audio_buffer = []
            # Grab the past ~480ms
            self.audio_buffer.extend(list(self.lookback_buffer)[:-1])

            self.was_speaking = True


        if is_confirmed:
            if not self.was_speaking:
                # User started speaking Grab the history
                self.audio_buffer.extend(list(self.lookback_buffer)[:-1])
            self.audio_buffer.append(audio_chunk)
            self.was_speaking = True
        elif self.was_speaking:
            # The transition: user just stopped speaking
            if len(self.audio_buffer) >= 8:
                audio_data = np.concatenate(self.audio_buffer)
                self.speech_queue.put(audio_data)
            self.audio_buffer = []
            self.was_speaking = False

    def _process_speech(self, audio_data: np.ndarray):
        text = self.stt.transcribe(audio_data, SAMPLE_RATE)
        if not text:
            return

        print(f"\nYou: {text}")

        # stop_event lets barge-in instantly kill both pygame AND the TTS producer thread
        stop_event = threading.Event()

        self.barge_in_detector.start_ai_speech(stop_event=stop_event)
        try:
            self.tts.speak_streaming(self.llm.stream_response(text), stop_event=stop_event)
        finally:
            self.barge_in_detector.stop_ai_speech()
            self.vad_filter.reset()

    def _worker(self):
        while self.running:
            try:
                audio_data = self.speech_queue.get(timeout=0.5)
                self._process_speech(audio_data)
            except queue.Empty:
                continue

    def run(self):
        print("\nStart!\n")

        worker_thread = threading.Thread(target=self._worker, daemon=True)
        worker_thread.start()

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=FRAME_SIZE,
            callback=self._audio_callback,
        ):
            try:
                while self.running:
                    sd.sleep(100)
            except KeyboardInterrupt:
                self.running = False

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()