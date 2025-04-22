import json

class InterviewSession:
    def __init__(self, question_file):
        with open(question_file, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)
        self.answers = {}
        self.branch = None

    def ask_question(self, section, question_data):
        print(f"\n{question_data['question']}")
        for i, option in enumerate(question_data['options']):
            print(f"{i + 1}. {option}")
        choice = int(input("Your answer (choose number): "))
        self.answers[question_data['question']] = question_data['options'][choice - 1]

    def run_intro(self): #TODO the way we decide on the branch is only based on one question (q2) we can imporve that by scoring.
        print("\n--- Introduction ---")
        for q in self.questions['introduction']:
            self.ask_question("introduction", q)

        emotion_response = self.answers.get("Which kind of emotion do you experience as of lately: positive or negative emotions?")
        if emotion_response == "Mostly positive":
            self.branch = "branch_1"
        elif emotion_response == "Mostly negative":
            self.branch = "branch_2"
        else:
            self.branch = "branch_1"  # default

    def run_branch(self):
        print(f"\n--- Branch: {'Positive' if self.branch == 'branch_1' else 'Negative'} Emotions ---")
        for q in self.questions[self.branch]:
            self.ask_question(self.branch, q)

    def evaluate(self):
        print("\n--- Evaluation Summary ---")
        for q, a in self.answers.items():
            print(f"Q: {q}\nA: {a}\n")

    def save_session(self, output_file="session_results.json"):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.answers, f, indent=2, ensure_ascii=False)
        print(f"\nSession saved to {output_file}")

if __name__ == "__main__":
    session = InterviewSession("questions.json")
    session.run_intro()
    session.run_branch()
    session.evaluate()
    session.save_session()
