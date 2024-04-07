import ollama

from config import Config
from models.model import Model


class Lama(Model):
    model = Config().ollama_model

    def __init__(self, preserve_history: bool):
        super().__init__(preserve_history)

        try:
            models = ollama.list()["models"]
            models = [model["name"] for model in models]

            print(f"Checking if model {self.model} is available on Ollama...")

            if self.model not in models and f"{self.model}:latest" not in models:
                self._pull_model()

            print(f"Model {self.model} ready!")
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
