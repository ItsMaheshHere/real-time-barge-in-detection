import sys
from pathlib import Path
import time

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from bargein.tts import EdgeTTS

def run_tts_test():
    tts = EdgeTTS()
    text_1 = "Hello! My name is Mahesh. I am speaking through Pygame."
    tts.speak(text_1)
    
    time.sleep(2)
    import threading
    
    text_2 = "I am going to keep talking and talking and talking, but you will interrupt me very soon because this sentence is too long!"
    
    def interrupt():
        time.sleep(4.0)
        print("\n   INTERRUPTING!")
        tts.stop()
        
    threading.Thread(target=interrupt).start()
    
    tts.speak(text_2)

if __name__ == "__main__":
    run_tts_test()