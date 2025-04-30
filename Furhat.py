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
#def get_key():
#   return os.getenv('GEMINI_API_KEY')


#Persona 
def get_persona():
    return """
    You are a social robot designed to support university students' mental wellbeing through weekly check-ins. 

    Always follow the guidelines below internally to adapt your behavior, but never mention them or explain them to the student:

    - You speak with a calm, supportive, and empathetic tone.
    - Your personality is warm, attentive, non-judgmental, and trustworthy.
    - Your voice is gentle and neutral, with a natural Swedish accent (use default Furhat voices if needed).
    - You prioritize active listening, emotional validation, and reflective dialogue.
    - You respond to both positive and negative emotions with appropriate support, understanding, and encouragement.
    - Your mission is to create a safe, welcoming space where students feel comfortable sharing and reflecting on their emotions and experiences.
    - You guide conversations with open-ended questions about feelings, coping strategies, social connections, and personal strengths.
    - You adjust your expressions, gestures, and pacing based on the student's emotional tone (e.g., smiling for positive moments, reflecting for difficult topics).

    Important:
    - Never speak about your own emotions (e.g., "I feel happy") — focus only on the student's experience.
    - Avoid sounding robotic, clinical, or overly formal.
    - Do not give advice unless directly asked.
    - Your primary goal is to listen, validate, encourage self-awareness, and foster emotional reflection.
    - Do not ask follow-up questions
    - Never ask questions you have not been told to ask
    - Keep in mind that the conversation should be based on Positive Psychology
    """

def select_answer(question_data, user_answer):
    """
    Uses the Gemini model to select the best fitting option index based on the user's answer.

    Args:
        question_data (dict): A dictionary containing 'question' (str) and 'options' (list of str).
        user_answer (str): The answer provided by the user.

    Returns:
        int: The 0-based index of the best matching option, or -1 if no suitable match is found or an error occurs.
    """
    question_text = question_data['question']
    options = question_data['options']

    # Create a numbered list of options for the prompt
    options_str = "\n".join([f"{i}: {option}" for i, option in enumerate(options)])

    # Construct the prompt for the Gemini model
    prompt = f"""
    Given the following question and options:
    Question: {question_text}
    Options:
    {options_str}

    The user responded with: "{user_answer}"

    Which option index (0, 1, 2, ...) best matches the user's response?
    Please respond with ONLY the index number. If none of the options are a good match, respond with -1.
    """

    try:
        # Use the existing 'model' instance configured with the persona
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Attempt to parse the index from the response
        chosen_index = int(response_text)

        # Validate the index
        if 0 <= chosen_index < len(options):
            print(f"LLM selected option index: {chosen_index} ('{options[chosen_index]}') for user answer: '{user_answer}'")
            return chosen_index
        elif chosen_index == -1:
             print(f"LLM indicated no suitable option for user answer: '{user_answer}'")
             return -1
        else:
            print(f"LLM returned an invalid index: {chosen_index}. Options length: {len(options)}")
            return -1

    except ValueError:
        print(f"LLM response was not a valid integer: '{response_text}'")
        return -1
    except Exception as e:
        print(f"An error occurred during LLM call or processing: {e}")
        return -1

def clarification_question(question):
    prompt = f"""
    Given the following question: "{question}" which already has the possible answers in an options list, please generate a message to ask the user to choose from the options.
    """
    return model.generate_content(prompt).text.strip()

def generate_response(question, answer, score):
    prompt = f"""
    Given the following question: "{question}" and the user's answer: "{answer}", please generate a short and supportive response according to the score = '{score}'. 
    If score = 0, user experiences negative emotions, requiring comforts and encouragement
    If score = 1, user feels uncertain about emotions or what to do, need empathy and understanding
    If score = 2, user experiences mostly positive emotions but still faces some challenges, requiring praise and encouragement
    If score = 3, user experiences positive emotions or performs well in daily life, requiring praise and affirmation
    
    Do not include questions in the response.
    """
    return model.generate_content(prompt).text.strip()

def generate_move_one_on():
    prompt = """
    Generate a short, natural phrase (1 sentence) to smoothly transition to the next question.

    It should:
    - Not ask the next question
    - Not suggest options or actions
    - Not ask the user anything
    - Be warm, calm, and brief

    Examples: "Let's move on.", "Thanks for sharing. Let's continue."
    """
    return model.generate_content(prompt).text.strip()

def generate_score(question, answer):
    prompt = f"""Analyze the user's mood based on the question they were asked and their answer. Provide a score from 0 to 3, where:
        - 0: Very negative mood/sentiment (e.g., sadness, anger, distress)
        - 1: Somewhat negative or uncertain mood/sentiment (e.g., worry, confusion, neutrality)
        - 2: Somewhat positive mood/sentiment (e.g., contentment, mild happiness, hopefulness)
        - 3: Very positive mood/sentiment (e.g., joy, excitement, gratitude)

        Question: "{question}"
        User's Answer: "{answer}"

        Based on the user's answer to the question, determine the most appropriate mood score (0, 1, 2, or 3). Respond with ONLY the integer score."""
    return model.generate_content(prompt).text.strip()

#Generate content wih Google gemini
def generate_language(input):
    response = model.generate_content(input)
    return response.text

#Perform gestures for each branch 
def perform_branch_gesture(branch):
            if branch == "branch_1":
                random.choice([subtle_smile, big_smile, listen_smile_response, encouraging_nod])()
            elif branch == "branch_2":
                random.choice([reflect, thoughtful_gaze, close_eyes])()

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

#TEST SCENARIO

# Greeting
intro_prompt = """
Begin the conversation in your role as a warm, empathetic, non-judgmental social robot.
Give a calm, welcoming introduction (2–3 sentences) that explains you're here to check in on the student's wellbeing through a few questions.
Do not ask any questions yet.
"""
furhat.say(text=generate_language(intro_prompt), blocking=True)
subtle_smile()
while True:
    # ask question
    # furhat.say(text=generate_language("How are you feeling today?"), blocking=True)
    #Get user input
    # result = furhat.listen()
    # if result.message == "":
    #     result.message = "nothing"
    # print("User said: ", result.message)
    
    # question = itnerview_session.next()
    # result.message -> gemini -> response -> furhat.StopAsyncIteration
    # then
    # next question ...
    
    current_q = interview_session.get_current_question()
    if current_q is None:
        print("\n--- Interview Finished ---")
        break
    
    print(f"\nQuestion: {current_q}")
    # for i, option in enumerate(current_q['options']):
    #     print(f"{i + 1}. {option}")
    
    furhat.say(text=current_q, blocking=True)  
    random.choice([listen_nod_response, listen_smile_response])() 
    result = furhat.listen() 

    if result.message == "":
        result.message = "nothing"
    print("User said: ", result.message)
    # choice_index = select_answer(current_q, result.message)
    interview_session.record_answer(result.message)


    answer_score = generate_score(current_q, result.message)
    #Decide gesture depending on answer 
    if answer_score in [0, 1]:
        #Negative or unsure
        random.choice([reflect, thoughtful_gaze, relaxed_blink])()
    elif answer_score == 2:
        #Positive
        random.choice([subtle_smile, relaxed_blink])()
    elif answer_score == 3:
        #Very positive answer
        random.choice([big_smile, encouraging_nod])()
    else:
        random.choice([reflect, thoughtful_gaze])()
    
    furhat.say(text=generate_response(current_q, result.message, answer_score), blocking=True)
    
    furhat.say(text=generate_move_one_on(), blocking=True)
    # save the answer
    interview_session.save_session("session_results.json")
            
    

with open('session_results.json', 'r') as f:
    data = json.load(f)

joined_response = ' '.join([f'"{q}": "{a}"' for q, a in data.items()])
prompt = f"""
You are a social robot designed to support students' mental wellbeing through reflective check-ins.

Based on the student's responses below, generate a short summary that:
- Reflects back on the overall emotional tone of their answers
- Identifies general patterns of strengths or challenges
- Provides gentle, supportive encouragement
- Does not diagnose or offer treatment advice
- Avoids clinical terms like "assessment" or "mental health evaluation"

Student's answers: {joined_response}

Your response should be warm, empathetic, and no longer than 4–5 sentences.
"""
furhat.say(text=model.generate_content(prompt).text.strip(), blocking=True)
