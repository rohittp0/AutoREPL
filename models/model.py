from typing import List


class Model:
    SYSTEM_PROMPT = (
        "You are a AI codding assistant. Your task is fix the code based on the error message."
        " You will recive input in the format:\n"
        "```python\n"
        "{The code that caused the error}\n"
        "```\n"
        "```text\n"
        "{The error message}\n"
        "```\n"
        "You should output the fixed code. The output should contain the entire code, not just the fixed part."
        " Your response should be in the format:\n"
        "```python\n"
        "THE FIXED CODE\n"
        "```\n"
        "Where the THE FIXED CODE is the code with the error fixed."
        " This should contain the entire code and nothing else."
        "The format of the input and output is important. Make sure to follow the format exactly."
        " If you are unable to fix the code, your response should be an empty code block (```python\n\n```."
    )

    def __init__(self, preserve_history: bool):
        self.preserve_history = preserve_history
        self.system_prompt = {"role": "system", "content": self.SYSTEM_PROMPT}
        self.history = []

    def _query(self, messages: List[dict]) -> str:
        raise NotImplementedError()

    def query(self, code: str, error: str) -> str:
        prompt = {"role": "user", "content": self._to_prompt(code, error)}

        response = self._query([
            self.system_prompt,
            *self.history,
            prompt,
        ])

        if self.preserve_history:
            self.history.append(prompt)
            self.history.append({"role": "assistant", "content": response})

        return self._from_response(response).strip()

    def feedback(self, feedback: str):
        if self.preserve_history:
            self.history.append({"role": "user", "content": feedback})

    @staticmethod
    def _to_prompt(code: str, error: str):
        return f"```python\n{code}\n```\n```text\n{error}\n```"

    @staticmethod
    def _from_response(response: str):
        return response.split("```python\n")[1].split("\n```")[0]
