import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
def get_google_api_key():
    return os.getenv("GOOGLE_API_KEY")