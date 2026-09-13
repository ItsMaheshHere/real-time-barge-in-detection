class BargeInDetector:
    """
    Monitors the user's voice while the AI is speaking.
    If the user starts talking, it instantly kills the AI's audio.
    """
    def __init__(self, tts_instance, vad_filter_instance):
        self.tts = tts_instance
        self.vad_filter = vad_filter_instance
        self.is_ai_speaking = False
        
    def start_ai_speech(self):
        self.is_ai_speaking = True
        self.vad_filter.reset()
        
    def stop_ai_speech(self):
        self.is_ai_speaking = False
        
    def check_barge_in(self, is_speech_confirmed: bool) -> bool:
        if not self.is_ai_speaking:
            return False
        if is_speech_confirmed:
            print("\nBarge-In: interrupted!")
            self.tts.stop()
            self.is_ai_speaking = False
            return True
            
        return False