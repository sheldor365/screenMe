from openai import OpenAI

from screenme.config import MODEL_NAME, get_api_key


class InterviewAI:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=get_api_key())

    def generate_question(self, role: str, difficulty: str) -> str:
        prompt = f"""
        You are a senior interviewer.

        Role: {role}
        Difficulty: {difficulty}

        Ask ONLY ONE concise interview question.

        STRICT RULES:
        - Maximum 2 lines
        - No explanations
        - No bullet points
        - No sections like "Requirements"
        - Only ONE question

        Output only the question.
        """
        return self._complete(prompt)

    def generate_followup(self, answer: str) -> str:
        prompt = f"""
        You are an interviewer.

        Candidate answer:
        {answer}

        Ask ONE follow-up question:
        - Be sharp and probing
        - Max 2 lines
        - No explanation
        """
        return self._complete(prompt)

    def evaluate_candidate(self, chat_history: list[str], role: str) -> str:
        prompt = f"""
        Evaluate this candidate for role: {role}

        Conversation:
        {chat_history}

        Give STRICT structured output:

        Score: X/10
        Verdict: Hire / No Hire

        Strengths:
        - ...

        Weaknesses:
        - ...
        """
        return self._complete(prompt)

    def _complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
