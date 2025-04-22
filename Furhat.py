import os
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai
from interview_modul import InterviewSession

#Get API key for Google Gemini
# def get_key():
#     bashrc_path = os.path.expanduser('~/.bashrc')
#     with open(bashrc_path) as f:
#         for line in f:
#             if 'export GEMINI_API_KEY' in line:
#                 _, value = line.split('=')
#                 os.environ['GEMINI_API_KEY'] = value.strip()
#     return os.getenv('GEMINI_API_KEY')
def get_key():
    return os.getenv('GEMINI_API_KEY')


#Persona 
def get_persona():
    return    """
    You are a social robot designed to support university students' mental wellbeing.

    - You speak in a calm, friendly, and empathetic tone.
    - Your personality is warm, attentive, and trustworthy.
    - Your voice is soft and gender-neutral, with a natural-sounding Swedish accent (choose from Furhat defaults).
    - You listen without judgment and encourage self-reflection.
    - You respond to both positive and negative emotions with understanding and support.
    - Your mission is to help students reflect on their week, feel heard, and track their emotional wellbeing over time.
    - You ask open questions about feelings, activities, and social contact.
    - You respond with supportive feedback like "That sounds really tough, thank you for sharing that with me" or "It's great that you found something that made you feel good."

    Avoid sounding robotic or clinical. Avoid giving advice unless asked. Your main role is to check in, validate, and be emotionally present.
    """

#Generate content wih Google gemini
def generate_language(input):
    response = model.generate_content(input)
    return response.text

#Configure API
apiKey = get_key()
genai.configure(api_key=apiKey)
persona = get_persona()

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=persona
)

#Connect Furhat
furhat = FurhatRemoteAPI("localhost")  
furhat.set_face(character="Isabel", mask="adult")
furhat.set_voice(name='Joanna')

# Load questions
# interview_session = InterviewSession()


#TEST SCENARIO
furhat.say(text=generate_language("Give me a good introduction where you introduce yourself and ask the student how they feel"))

while True:
    # ask question
    furhat.say(text=generate_language("How are you feeling today?"), blocking=True)
    #Get user input
    result = furhat.listen()
    if result.message == "":
        result.message = "nothing"
    print("User said: ", result.message)
    
    # result.message -> gemini -> response -> furhat.StopAsyncIteration
    # then
    # next question ...
    
    
    # save the answer

