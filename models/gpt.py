import os
from typing import List

from openai import OpenAI

from config import Config
from models.model import Model


class GPT(Model):
    client = None
    model = Config().openai_model

    def __new__(cls, *args, **kwargs):
        if cls.client is None:
            cls.client = OpenAI(
                api_key=Config().openai_api_key,

            )
        return super().__new__(cls)

    def _query(self, messages: List[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response["choices"][0]["message"]["content"]
