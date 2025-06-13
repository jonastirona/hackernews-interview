import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=api_key)

# List available models
for model in genai.list_models():
    print(model.name, model.supported_generation_methods)