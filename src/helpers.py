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
        """
        Formats the input according to the specified type.

        Args:
            content (str): Content to be formatted.
            typeof (Literal["img_url", "text"], optional): Type of content. Can be "img_url" for image or "text" for text. Default is "text".
            img_url (str, optional): Image URL if the type is "img_url". Default is an empty string.
            role (str, optional): Role of the content author. Default is "user".

        Returns:
            dict: Dictionary formatted with the appropriate structure for the specified content type.
        """
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

        assistant = response.json()["choices"][0]["message"]["content"]

        return assistant

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


class Chat:
    """
    Class that manages the chat with loops and handles inputs.
    """

    ...


if __name__ == "__main__":
    from dotenv import load_dotenv
    from os import getenv

    load_dotenv()

    client = Client(
        api_key=getenv("OPENAI_API_KEY") or "", system_context="Seja conciso."
    )

    img = "/Users/hideki/vox/__testes/ue.png"
