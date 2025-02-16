import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print(f"Starting app with OpenAI API Key: {api_key}")
else:
    print("ERROR: OPENAI_API_KEY is not set!")
