"""Test OpenAI API directly without LangChain"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing OpenAI API directly...")
print(f"API Key (first 20 chars): {os.getenv('OPENAI_API_KEY')[:20]}...")

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Prathamesh wants to buy a laptop worth 27,450 rupees. He has 22,975 rupees. What is the amount he still needs to be able to buy the laptop?"}
        ],
        max_tokens=200
    )

    print("\n✅ SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
