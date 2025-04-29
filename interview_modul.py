import json

class InterviewSession:
    def __init__(self, question_file):
        """Initializes the session by loading a list of questions from a JSON file."""
        with open(question_file, 'r', encoding='utf-8') as f:
            # Expecting a JSON file containing a list of strings (questions)
            self.questions = json.load(f)
            if not isinstance(self.questions, list) or not all(isinstance(q, str) for q in self.questions):
                raise ValueError("Question file must contain a JSON list of strings.")
        self.answers = {}
        self.current_question_index = 0

    def get_current_question(self):
        """Returns the current question string or None if the interview is finished."""
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        else:
            # Reached the end of the questions list
            return None

    def record_answer(self, answer_text):
        """Records the answer for the current question and advances to the next."""
        current_question_text = self.get_current_question()
        if current_question_text is None:
            print("Error: Tried to record an answer, but no current question is available (interview finished?).")
            return

        # Record the answer associated with the question text
        self.answers[current_question_text] = answer_text
        print(f"Recorded Answer: {current_question_text} -> {answer_text}") # Debug print

        # Advance to the next question index
        self.current_question_index += 1

    def evaluate(self):
        """Prints a summary of the questions and their recorded answers."""
        print("\n--- Evaluation Summary ---")
        if not self.answers:
            print("No answers were recorded.")
            return
        for q, a in self.answers.items():
            print(f"Q: {q}\nA: {a}\n")

    def save_session(self, output_file="session_results.json"):
        """Saves the recorded answers to a JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.answers, f, indent=2, ensure_ascii=False)
        print(f"\nSession saved to {output_file}")

# Removed the __main__ block as it depended on the previous structure with options.
# You would need a new way to interact with the session, likely involving
# getting the question string, sending it to an external system (like an LLM or user input),
# receiving the answer text, and then calling record_answer.
