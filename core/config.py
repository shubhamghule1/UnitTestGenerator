import os
from dotenv import load_dotenv

def setup_environment():
    # Explicitly specify the path to the .env file
    env_file_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f".env file not found at {env_file_path}")

    # Load the environment variables from the .env file
    load_dotenv(dotenv_path=env_file_path)

    # Check if the OPENAI_API_KEY is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    else:
        print("OPENAI_API_KEY loaded successfully")