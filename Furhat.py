import os
import google.generativeai as genai

def get_key():
    """Fetches Gemini API key from .bashrc file."""
    bashrc_path = os.path.expanduser('~/.bashrc')
    with open(bashrc_path) as f:
        for line in f:
            if 'export GEMINI_API_KEY' in line:
                _, value = line.split('=')
                os.environ['GEMINI_API_KEY'] = value.strip()
    return os.getenv('GEMINI_API_KEY')

def get_persona():
    return """
    You are a helpful assistant trained in mindfulness and emotional support.
    Respond in a calm, friendly, and encouraging tone.
    """

# Init
apiKey = get_key()
genai.configure(api_key=apiKey)
persona = get_persona()

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=persona
)

response = model.generate_content("Hello, how are you?")
print(response.text)
