""" Aux. Classes and Functions
"""

import os
import sys
import base64
from typing import Literal
from openai import OpenAI
import openai.types.chat as openaitypes
from requests import post

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
        self.__header_to_image = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    @classmethod
    def format_input(
        cls,
        content: str,
        typeof: Literal["img_url", "text"] = "text",
        img_url: str = "",
        role: str = "user",
    ):
        if typeof == "img_url":
            return {
                "role": role,
                "content": [
                    {"type": "text", "text": content},
                    {"type": "image_url", "image_url": {"url": img_url}},
                ],
            }
        return {"role": role, "content": content}

    def send_images(self, absolute_path: str, content: str) -> str:
        """
        Sends an image to the OpenAI API along with a request for a descriptive rhyming response.

        Args:
            absolute_path (str): The absolute file path to the image.
            content (str): The textual content to send along with the image.

        Raises:
            ValueError: If the provided path to the image does not exist.

        Returns:
            str: The descriptive rhyming response from the API.
        """

        if not os.path.exists(absolute_path):
            raise ValueError("The path to the image does not exist.")

        base64_image = ""
        with open(absolute_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": content},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 600,
        }

        response = post(
            "https://api.openai.com/v1/chat/completions",
            headers=self.__header_to_image,
            json=payload,
        )

        return response.json()["choices"][0]["message"]["content"]

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
        api_key=getenv("OPENAI_API_KEY") or "", system_context="Seja conciso."
    )

    img = "/Users/hideki/vox/__testes/ue.png"

    client.messages.append(
        Client.format_input(
            content="Descreva a paleta de cores da imagem. -epp",
            typeof="img_url",
            img_url="https://s2-oglobo.glbimg.com/jzgUNIeBajWtux_gog-p1Be6e74=/0x0:1200x694/984x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_da025474c0c44edd99332dddb09cabe8/internal_photos/bs/2022/Y/4/FRSLBtRomkvLSMbzcjSw/54599493-paola-carosela.jpg",
        )
    )

    client.ask()

    client.messages.append(
        Client.format_input(content="Tá, agora resuma tudo num tweet.")
    )

    client.ask()
