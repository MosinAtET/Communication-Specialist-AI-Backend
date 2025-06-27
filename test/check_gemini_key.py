import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not set in environment.")
    exit(1)

genai.configure(api_key=api_key)

try:
    models = list(genai.list_models())
    print("Available models:")
    for m in models:
        print("-", m.name)
    
    # Test if gemini-2.0-flash is available
    flash_model = None
    for m in models:
        if 'gemini-2.0-flash' in m.name:
            flash_model = m.name
            break
    
    if flash_model:
        print(f"\n✅ gemini-2.0-flash is available: {flash_model}")
        
        # Test a simple generation
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello, this is a test.")
        print("✅ Model test successful!")
        print(f"Response: {response.text}")
    else:
        print("\n❌ gemini-2.0-flash not found in available models")
        print("Available Gemini models:")
        for m in models:
            if 'gemini' in m.name.lower():
                print(f"  - {m.name}")
        
except Exception as e:
    print("Error listing models:", e) 