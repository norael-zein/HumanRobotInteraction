import os
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai
from interview_modul_old import InterviewSession
from gestures import *
import random 
import json

#Get API key for Google Gemini
# def get_key():
#      bashrc_path = os.path.expanduser('~/.bashrc')
#      with open(bashrc_path) as f:
#          for line in f:
#              if 'export GEMINI_API_KEY' in line:
#                  _, value = line.split('=')
#                  os.environ['GEMINI_API_KEY'] = value.strip()
#      return os.getenv('GEMINI_API_KEY')
def get_key():
   return os.getenv('GEMINI_API_KEY')


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
    prompt = f"""
    Generate a short text for the robot to say when it is moving to the next question.
    """
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
furhat.say(text=generate_language("Introduce yourself shortly without asking questions. Talk like a mental health therapist."))
# subtle_smile()
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
    
    print(f"\nQuestion: {current_q['question']}")
    for i, option in enumerate(current_q['options']):
        print(f"{i + 1}. {option}")
    
    furhat.say(text=current_q['question'], blocking=True)  
    # random.choice([listen_nod_response, listen_smile_response])() 
    result = furhat.listen() 

    if result.message == "":
        result.message = "nothing"
    print("User said: ", result.message)
    interview_session.record_answer(result.message)
    
    # choice_index = select_answer(current_q, result.message)

    # if choice_index != -1:
    #     chosen_answer_score = current_q['scores'][choice_index]

    #     #Decide gesture depending on answer 
    #     if chosen_answer_score in [0, 1]:
    #         #Negative or unsure
    #         random.choice([reflect, thoughtful_gaze, relaxed_blink])()
    #     elif chosen_answer_score == 2:
    #         #Positive
    #         random.choice([subtle_smile, relaxed_blink])()
    #     elif chosen_answer_score == 3:
    #         #Very positive answer
    #         random.choice([big_smile, encouraging_nod])()
    #     else:
    #         random.choice([reflect, thoughtful_gaze])()
    # try:        
    #     choice_index = select_answer(current_q, result.message)
    #     print("CHOICE INDEX: ", choice_index)
    #     if 0 <= choice_index < len(current_q['options']):
    #         chosen_answer_text = current_q['options'][choice_index]
    #         chosen_answer_score = current_q['scores'][choice_index]
    #         interview_session.record_answer(chosen_answer_text)
    #         furhat.say(text=generate_response(current_q['question'], chosen_answer_text, chosen_answer_score), blocking=True)
            
    #         #Generate gestures
    #         perform_branch_gesture(interview_session.branch)

    #         furhat.say(text=generate_move_one_on(), blocking=True)
    #     elif choice_index == -1:
    #         random.choice([reflect,thoughtful_gaze])()
    #         # No suitable option found, handle accordingly
    #         print("No suitable option found for the user's answer.")
    #         furhat.say(text=clarification_question(current_q), blocking=True)
    #         # furhat.say(text="I didn't quite understand your answer. Could you please", blocking=True)
    #     else:
    #         print("Invalid choice number.")
    interview_session.save_session("session_results.json")
                
    # except ValueError:
    #     print("Invalid input. Please enter a number.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     break  # Exit loop on unexpected error
    
    # save the answer

with open('session_results.json', 'r') as f:
    data = json.load(f)

joined_response = ' '.join([f'"{q}": "{a}"' for q, a in data.items()])
prompt = f"""
    Give a short assessment of user's mental health based on the answers user given: {joined_response}"""
furhat.say(text=model.generate_content(prompt).text.strip(), blocking=True)