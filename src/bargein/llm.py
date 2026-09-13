import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqLLM:
    def __init__(self, system_prompt: str = "You are a helpful voice assistant. Speak naturally and keep your answers very brief and conversational, as they will be spoken out loud."):
        self.client = Groq()
        self.model = "qwen/qwen3.8-27b"
        self.system_prompt = system_prompt
        
        # We store the conversation history so the AI remembers what we talked about
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def generate_response(self, user_text: str) -> str:
        if not user_text.strip():
            return ""

        self.chat_history.append({"role": "user", "content": user_text})
        
        try:
            print("[LLM] Generating response...")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                temperature=0.7,
                max_tokens=100, # We keep it short so it doesn't talk forever
            )
            
            ai_response = completion.choices[0].message.content.strip()
            
            # Add AI's response to memory so it has context for the next question
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            print(f"[LLM Error]: {e}")
            return "I'm sorry, I am having trouble thinking right now."

    def stream_response(self, user_text: str):
        if not user_text.strip():
            return

        self.chat_history.append({"role": "user", "content": user_text})

        try:
            print("LLM: response...")
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                temperature=0.7,
                max_tokens=150,
                stream=True,
            )

            full_response = ""
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                full_response += token
                yield token

            self.chat_history.append({"role": "assistant", "content": full_response})

        except Exception as e:
            print(f"[LLM Error]: {e}")