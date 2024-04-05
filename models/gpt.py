import os
from typing import List

from openai import OpenAI

from models.model import Model


class GPT(Model):
    client = None
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def __new__(cls, *args, **kwargs):
        if cls.client is None:
            cls.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),

            )
        return super().__new__(cls)

    def _query(self, messages: List[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response["choices"][0]["message"]["content"]
