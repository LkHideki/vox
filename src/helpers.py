""" Aux. Classes and Functions
"""

import sys
from typing import Literal
from openai import OpenAI
import openai.types.chat as openaitypes

from custom_types import TMESSAGE


class Client:
    def __init__(
        self,
        api_key: str,
        system_context: str,
        model: str = "gpt-4o",
        max_tokens: int = 700,
    ) -> None:
        self.__client = OpenAI(api_key=api_key)
        self.messages: list[TMESSAGE] = []
        self.model = model
        self.system: str = system_context
        self.max_tokens: int = max_tokens

    @classmethod
    def format_input(
        cls,
        content: str,
        typeof: Literal["img_url", "text"],
        img_url: str = "",
        role: str = "user",
    ):
        if typeof == "img_url":
            return {
                "role": role,
                "content": [
                    {"type": content},
                    {"type": "image_url", "image_url": {"url": img_url}},
                ],
            }
        return {"role": role, "content": content}

    def ask(self):
        res = self.__client.chat.completions.create(
            model=self.model,
            messages=[
                openaitypes.ChatCompletionSystemMessageParam(
                    {"role": "system", "content": self.system}
                ),
                *self.messages,
            ],
            max_tokens=self.max_tokens,
            n=1,
            stream=True,
        )

        print("> ", end="")

        final = ""
        for chunk in res:
            _aux = chunk.choices[0].delta.content or ""
            final += _aux
            sys.stdout.write(_aux)
            sys.stdout.flush()
        print()

        self.messages.append(Client.format_input(final.strip(), role="assistant"))


if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv()

    client = Client(
        api_key=getenv("OPENAI_API_KEY") or "", system_context="Você fala tudo rimando"
    )
