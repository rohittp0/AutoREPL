import os

import ollama

from models.model import Model


class Lama(Model):
    model = os.getenv("OLLAMA_MODEL", "codellama")

    def __init__(self, preserve_history: bool):
        super().__init__(preserve_history)

        try:
            models = ollama.list()
            if self.model not in models:
                self._pull_model()
        except Exception as e:
            print(f"Error: unable to connect to Ollama: \n{e}")
            exit(1)

    def _pull_model(self):
        for progress in ollama.pull(self.model, stream=True):
            percent = progress.get("completed", 0) / progress.get("total", 1) * 100
            print(f"\rOllama Pull: {progress['status']} - {percent} %", end="")
        print("\r", '' * 100)

    def _query(self, messages: list) -> str:
        response = ollama.chat(model=self.model, messages=messages)
        return response["message"]["content"]
