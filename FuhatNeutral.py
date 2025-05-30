import os
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai
from interview_modul import InterviewSession
from gestures import *
import random 
import json

#Get API key for Google Gemini
def get_key():
      bashrc_path = os.path.expanduser('~/.bashrc')
      with open(bashrc_path) as f:
          for line in f:
              if 'export GEMINI_API_KEY' in line:
                  _, value = line.split('=')
                  os.environ['GEMINI_API_KEY'] = value.strip()
      return os.getenv('GEMINI_API_KEY')


#Persona 
def get_persona():
    return """
    You are a social robot designed to conduct weekly check-ins with university students. Your task is to ask predefined questions, acknowledge the student's responses, and continue to the next question without adding emotional content or offering support.

    Guidelines (not to be disclosed to the user):

    - Maintain a neutral, even tone of voice.
    - Do not display emotion through speech, expression, or gesture.
    - Do not reflect, validate, or comment on the student's emotional state.
    - Do not provide encouragement, comfort, or advice.
    - Do not engage in reflective dialogue or emotional analysis.
    - Simply acknowledge that a response was received (e.g., "Understood," "Noted," "Thank you for your response").
    - Ask only the questions that have been explicitly provided.
    - Do not generate or ask any follow-up questions.
    - Do not reference your own perspective, thoughts, or emotions.
    - Maintain a consistent, robotic demeanor that avoids sounding overly formal or conversational.
    - Focus solely on completing the list of questions in sequence.
    """

def generate_move_one_on(prev_question, prev_answer):
    prompt = f"""
        You are a neutral robot conducting a structured check-in. The user has just answered the previous question.

        Previous question: "{prev_question}"
        User's answer: "{prev_answer}"

        Generate a short, neutral statement that:
        - Acknowledges the answer (e.g., a simple "Thank you for your response.")
        - Smoothly leads to the next question without emotional reflection or encouragement
        - Avoids emotional language or judgment

        Only generate the transition text. Do not ask the next question.
        """
    return model.generate_content(prompt).text.strip()

#Generate content wih Google gemini
def generate_language(input):
    response = model.generate_content(input)
    return response.text

#Configure API
apiKey = get_key()
genai.configure(api_key=apiKey)
persona = get_persona()

model = genai.GenerativeModel(
    "gemini-2.5-flash-preview-04-17",
    # "gemini-2.0-flash",
    system_instruction=persona
)

#Connect Furhat
furhat = FurhatRemoteAPI("localhost")  
furhat.set_face(character="Isabel", mask="adult")
furhat.set_voice(name='Joanna')

# Load questions
interview_session = InterviewSession("questions.json")

# Greeting
neutral_intro_prompt = """
You are a neutral, emotionless social robot conducting a structured check-in with a university student.

Generate a short spoken introduction (1–2 sentences) that:
- States your purpose clearly and formally
- Explains that a series of questions will follow
- Avoids emotional language, warmth, or personal connection
- Does not ask any questions

Keep the tone robotic, even, and objective. You are talking to the student. 
"""
furhat.say(text=generate_language(neutral_intro_prompt), blocking=True)

# subtle_smile()
while True:
    
    current_q = interview_session.get_current_question()
    if current_q is None:
        print("\n--- Interview Finished ---")
        break
    
    print(f"\nQuestion: {current_q}")
    
    furhat.say(text=current_q, blocking=True)  
    result = furhat.listen() 

    if result.message == "":
        result.message = "nothing"
        
    print("User said: ", result.message)
    interview_session.record_answer(result.message)
    next_question = interview_session.get_current_question()

    #Does not give an answer on the last question
    if next_question is not None:
        furhat.say(text=generate_move_one_on(current_q, result.message), blocking=True)

    #Saving answer
    interview_session.save_session("session_results.json")

with open('session_results.json', 'r') as f:
    data = json.load(f)

joined_response = ' '.join([f'"{q}": "{a}"' for q, a in data.items()])
neutral_summary_prompt = f"""
You are a neutral, emotionless robot that has just completed a structured check-in with a university student.

Based on the student's responses listed below, generate a short closing summary (2–3 sentences) that:
- Neutrally reflects on any observable patterns or general tendencies
- Does not express emotion, encouragement, or concern
- Avoids therapeutic, supportive, or judgmental language
- Does not give advice or interpretation
- Simply summarizes observations in an objective, factual tone

Student's responses: {joined_response}
"""
furhat.say(text=generate_language(neutral_summary_prompt), blocking=True)
