import io
import asyncio
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

    async def _generate_and_play(self, text: str):
        print("[TTS] Generating voice")
        communicate = edge_tts.Communicate(text, self.voice)
        
        # Stream the MP3 data into RAM
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                
        # Load the MP3 bytes into pygame
        audio_io = io.BytesIO(audio_data)
        pygame.mixer.music.load(audio_io, "mp3")
        
        print("[TTS] Playing audio")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            # NOTE:add our VAD interruption logic here
            await asyncio.sleep(0.1)

    def stop(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("[TTS] Playback interrupted!")