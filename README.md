# Real-Time Barge-In Detection for Voice AI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
This was a personal project to understand how real-time voice AI systems work under the hood. I built everything from scratch: voice activity detection, speech-to-text, LLM integration, and text-to-speech — and then wired them together into a working voice loop with barge-in support.

---

## What is Barge-In?

I noticed a problem when using ChatGPT Voice and Gemini Voice. When the AI is giving a response and I try to speak, the AI doesn't stop immediately — it keeps talking for about 1 to 2 seconds before it finally recognizes that I started speaking. That delay felt unnatural. In a real conversation, a person stops talking the moment they hear you interrupt. These assistants don't do that.

So I decided to build my own prototype to solve this. The goal was to detect that the user started speaking as fast as possible — and stop the AI audio almost instantly.

The way I implemented it: while the AI's voice is playing through the speaker, I keep a Voice Activity Detector (VAD) running in the background, checking the microphone every 32ms. The moment it confirms your voice (which takes about 100ms), it immediately calls `tts.stop()` and the audio cuts off. No 1-2 second delay.

---

## How It Works

```
You speak
   ↓
Silero VAD detects your voice (every 32ms)
   ↓
Audio is sent to Groq Whisper (speech-to-text)
   ↓
Text is sent to Groq LLaMA / Qwen (AI response, streamed token by token)
   ↓
TTS starts playing the first sentence before the full response is even generated
   ↓
While AI is speaking, VAD is still running in the background
   ↓
If you speak → BargeInDetector fires → audio stops instantly
   ↓
Your new speech gets processed immediately
```

The streaming pipeline (LLM tokens → sentence detection → TTS audio) is what gives it low latency. Instead of waiting for the full response, it starts speaking the first sentence in about 400ms.

---

## Project Structure

```
real-time-barge-in-detection/
├── src/
│   ├── main.py                 ← Entry point, main voice assistant loop
│   └── bargein/
│       ├── audio.py            ← Basic mic capture utilities
│       ├── vad.py              ← Silero VAD wrapper + temporal filter
│       ├── stt.py              ← Groq Whisper STT
│       ├── llm.py              ← Groq LLM with conversation memory + streaming
│       ├── tts.py              ← Edge TTS with producer-consumer streaming
│       └── bargein.py          ← Barge-in detection logic
├── tests/
│   ├── test_microphone_vad.py  ← Live VAD test
│   ├── test_stt.py             ← STT test (records 5 seconds, transcribes)
│   ├── test_llm.py             ← LLM test
│   └── test_tts.py             ← TTS and interruption test
├── requirements.txt
└── .env                        ← API keys (not committed)
```

---

## Tech Stack

| Component | Tool |
|---|---|
| VAD | [Silero VAD](https://github.com/snakers4/silero-vad) |
| STT | [Groq Whisper Large v3 Turbo](https://console.groq.com) |
| LLM | [Groq Qwen 3.8 27B](https://console.groq.com) |
| TTS | [Microsoft Edge TTS](https://github.com/rany2/edge-tts) |
| Audio Playback | [Pygame](https://www.pygame.org) |
| Microphone Input | [SoundDevice](https://python-sounddevice.readthedocs.io) |

Groq is used for both STT and LLM because it's ridiculously fast. Free tier is enough for development.

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/ItsMaheshHere/real-time-barge-in-detection.git
cd real-time-barge-in-detection
```

**2. Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file** in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key at [console.groq.com](https://console.groq.com)

**5. Run**
```bash
python src/main.py
```


## Current Limitations

**Echo / False Barge-In (the big one)**
If you're not wearing headphones, the AI's voice comes out of your speakers, the microphone picks it up, and the VAD thinks you interrupted. On Android, this is solved by the hardware `AcousticEchoCanceler`. In a browser, WebRTC handles it automatically. In a desktop Python app, you have to do it in software — which is genuinely hard to get right. For now, **headphones are required** for a clean experience.

---

## What's Next (Future Plans)

The plan was always to port this to Android.

- Hardware AEC eliminates the echo problem completely
- Android's `AudioRecord` API gives lower latency than Python's sounddevice

The Python prototype successfully demonstrates the core barge-in concept. The next major milestone on the roadmap is building the native Android application.

---

## License

MIT