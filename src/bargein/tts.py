import io
import time
import queue
import asyncio
import threading
import edge_tts
import pygame

class EdgeTTS:
    def __init__(self, voice: str = "en-US-AriaNeural"):
        self.voice = voice
        pygame.mixer.init()

    def speak(self, text: str):
        if not text.strip():
            return
        asyncio.run(self._generate_and_play(text))

    async def _generate_audio(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, self.voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    async def _generate_and_play(self, text: str):
        print("TTS: Generating voice")
        audio_data = await self._generate_audio(text)
        audio_io = io.BytesIO(audio_data)
        pygame.mixer.music.load(audio_io, "mp3")
        print("TTS: Playing audio")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

    def speak_streaming(self, text_token_generator, stop_event: threading.Event = None):
        audio_queue = queue.Queue(maxsize=3)
        SENTENCE_ENDINGS = {'.', '!', '?'}
        MIN_CHUNK_CHARS = 30

        def producer():
            sentence_buffer = ""
            for token in text_token_generator:
                if stop_event and stop_event.is_set():
                    break

                sentence_buffer += token
                last_char = sentence_buffer.strip()[-1] if sentence_buffer.strip() else ""

                if last_char in SENTENCE_ENDINGS and len(sentence_buffer.strip()) >= MIN_CHUNK_CHARS:
                    chunk_text = sentence_buffer.strip()
                    sentence_buffer = ""
                    print(f"TTS: Generating chunk: '{chunk_text[:40]}...'")
                    audio_data = asyncio.run(self._generate_audio(chunk_text))
                    if audio_data:
                        audio_queue.put(audio_data)

            if sentence_buffer.strip() and not (stop_event and stop_event.is_set()):
                audio_data = asyncio.run(self._generate_audio(sentence_buffer.strip()))
                if audio_data:
                    audio_queue.put(audio_data)

            audio_queue.put(None)

        def consumer():
            while True:
                if stop_event and stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
                try:
                    audio_data = audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if audio_data is None:
                    break

                audio_io = io.BytesIO(audio_data)
                pygame.mixer.music.load(audio_io, "mp3")
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    if stop_event and stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    time.sleep(0.05)

        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)

        producer_thread.start()
        consumer_thread.start()

        producer_thread.join()
        consumer_thread.join()

    def stop(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("TTS: Playback interrupted!")