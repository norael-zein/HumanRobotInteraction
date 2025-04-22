import json

class InterviewSession:
    def __init__(self, question_file):
        with open(question_file, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)
        self.answers = {}
        self.branch = None
        self.current_section = 'introduction'
        self.current_question_index = 0
        self._branch_determining_question = "Which kind of emotion do you experience as of lately: positive or negative emotions?"  # TODO: Make this configurable?

    def get_current_question(self):
        """Returns the data for the current question or None if the interview is finished."""
        if self.current_section is None:
            return None

        section_questions = self.questions.get(self.current_section)
        if not section_questions or self.current_question_index >= len(section_questions):
            # Section finished, potentially move to next or end
            if self.current_section == 'introduction':
                # Intro finished, determine branch if not already set (e.g., if branch question wasn't last)
                if self.branch is None:
                    # Fallback if branch wasn't determined correctly by the specific question
                    print("Warning: Branch could not be determined based on intro answers. Defaulting to branch_1.")
                    self.branch = "branch_1"  # Default or raise error

                print(f"\n--- Transitioning to Branch: {'Positive' if self.branch == 'branch_1' else 'Negative'} Emotions ---")
                self.current_section = self.branch
                self.current_question_index = 0
                # Re-check if the new section has questions
                section_questions = self.questions.get(self.current_section)
                if not section_questions:  # Branch might be empty or invalid
                    self.current_section = None
                    return None
            else:
                # Branch finished
                self.current_section = None
                return None

        # Return current question from the (potentially updated) section
        if self.current_section and self.current_question_index < len(self.questions[self.current_section]):
            return self.questions[self.current_section][self.current_question_index]
        else:
            # Should ideally not be reached if logic above is correct, but acts as safeguard
            self.current_section = None
            return None

    def record_answer(self, answer_text):
        """Records the answer for the current question and advances the state."""
        current_question_data = self.get_current_question()
        if current_question_data is None:
            print("Error: Tried to record an answer, but no current question is available.")
            return

        question_text = current_question_data['question']
        # Ensure the provided answer is one of the valid options
        if answer_text not in current_question_data['options']:
            print(f"Warning: Received answer '{answer_text}' which is not in the predefined options for question '{question_text}'. Recording it anyway.")
            # Or raise ValueError("Invalid answer option provided.")

        self.answers[question_text] = answer_text
        print(f"Recorded Answer: {question_text} -> {answer_text}")  # Debug print

        # Check if this was the question that determines the branch
        if self.current_section == 'introduction' and question_text == self._branch_determining_question:
            if answer_text == "Mostly positive":
                self.branch = "branch_1"
            elif answer_text == "Mostly negative":
                self.branch = "branch_2"
            else:
                print(f"Warning: Unexpected answer '{answer_text}' for branch determining question. Defaulting to branch_1.")
                self.branch = "branch_1"  # Default branch

        # Advance to the next question index for the current section
        self.current_question_index += 1

    def evaluate(self):
        print("\n--- Evaluation Summary ---")
        for q, a in self.answers.items():
            print(f"Q: {q}\nA: {a}\n")

    def save_session(self, output_file="session_results.json"):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.answers, f, indent=2, ensure_ascii=False)
        print(f"\nSession saved to {output_file}")

# if __name__ == "__main__":
#     session = InterviewSession("questions.json")

#     while True:
#         current_q = session.get_current_question()
#         if current_q is None:
#             print("\n--- Interview Finished ---")
#             break

#         print(f"\nQuestion: {current_q['question']}")
#         for i, option in enumerate(current_q['options']):
#             print(f"{i + 1}. {option}")

#         # --- Simulation of external processing ---
#         # In a real scenario, you would send the question/options externally,
#         # receive the user's natural language response, process it with an LLM
#         # to choose the best option index, and get the corresponding option text.
#         # Here, we simulate by asking the user for the number directly.
#         try:
#             choice_index = int(input("Simulate external choice (select number): ")) - 1
#             if 0 <= choice_index < len(current_q['options']):
#                 chosen_answer_text = current_q['options'][choice_index]
#                 # --- End Simulation ---

#                 session.record_answer(chosen_answer_text)
#             else:
#                 print("Invalid choice number.")
#                 # In a real scenario, you might re-prompt or handle the error
#         except ValueError:
#             print("Invalid input. Please enter a number.")
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             break  # Exit loop on unexpected error

    # session.evaluate()
    # session.save_session()
