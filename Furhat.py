import os
from furhat_remote_api import FurhatRemoteAPI
import google.generativeai as genai
from interview_modul import InterviewSession
from gestures import *
import random 

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

def generate_response(question, answer):
    prompt = f"""
    Given the following question: "{question}" and the user's answer: "{answer}", please generate a supportive response. Do not include questions in the response.
    """
    return model.generate_content(prompt).text.strip()

def generate_move_one_on():
    prompt = f"""
    Generate some short text for the robot to say when it is moving to the next question.
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
    "gemini-2.0-flash",
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
furhat.say(text=generate_language("Give me a good introduction where you introduce yourself"))
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
    
    print(f"\nQuestion: {current_q['question']}")
    for i, option in enumerate(current_q['options']):
        print(f"{i + 1}. {option}")
    
    furhat.say(text=current_q['question'], blocking=True)
    random.choice([listen_nod_response, listen_smile_response])() 
    result = furhat.listen()
    if result.message == "":
        result.message = "nothing"
    print("User said: ", result.message)
    try:        
        choice_index = select_answer(current_q, result.message)
        print("CHOICE INDEX: ", choice_index)
        if 0 <= choice_index < len(current_q['options']):
            chosen_answer_text = current_q['options'][choice_index]
            interview_session.record_answer(chosen_answer_text)
            furhat.say(text=generate_response(current_q['question'], chosen_answer_text), blocking=True)
            furhat.say(text=generate_move_one_on(), blocking=True)
        elif choice_index == -1:
            reflect()
            # No suitable option found, handle accordingly
            print("No suitable option found for the user's answer.")
            furhat.say(text=clarification_question(current_q), blocking=True)
            # furhat.say(text="I didn't quite understand your answer. Could you please", blocking=True)
        else:
            print("Invalid choice number.")
            
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")
        break  # Exit loop on unexpected error
    
    # save the answer

