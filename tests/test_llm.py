import sys
from pathlib import Path

src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from bargein.llm import GroqLLM

def run_llm_test():
    try:
        llm = GroqLLM()
    except Exception as e:
        print(f"Failed")
        return
    
    # Test 1
    test_message_1 = "Hi! Can you tell me a very short joke? not on the scarecrow"
    response_1 = llm.generate_response(test_message_1)
    print(f"AI: {response_1}")
    
    # Test 2 To prove it has memory
    test_message_2 = "Can you explain it?"
    response_2 = llm.generate_response(test_message_2)
    print(f"AI: {response_2}")
    print("\n")

if __name__ == "__main__":
    run_llm_test()