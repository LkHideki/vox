import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
import openai.types.chat as openaitypes
import pyperclip

load_dotenv()

# -----

TMESSAGE = (
    openaitypes.ChatCompletionSystemMessageParam
    | openaitypes.ChatCompletionUserMessageParam
    | openaitypes.ChatCompletionAssistantMessageParam
    | openaitypes.ChatCompletionToolMessageParam
    | openaitypes.ChatCompletionFunctionMessageParam
)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat(messages: list[TMESSAGE], model: str, context: str, max_tokens: int) -> None:
    """
    Chat with the OpenAI GPT model using a list of messages.
    The assistant's answer is appended to messages list.

    Args:
        messages (list[TMESSAGE]): List of messages exchanged in the chat.
        model (str): The name of the GPT-3 model to use.
        context (str): The system context of the chat.
        max_tokens (int): The maximum number of tokens to generate.

    Returns:
        None
    """

    res = client.chat.completions.create(
        model=model,
        messages=[
            openaitypes.ChatCompletionSystemMessageParam(
                {"role": "system", "content": context}
            ),
            *messages,
        ],
        max_tokens=max_tokens,
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

    messages.append(
        openaitypes.ChatCompletionAssistantMessageParam(
            {"role": "assistant", "content": final.strip()}
        )
    )


def user_says(text: str) -> openaitypes.ChatCompletionUserMessageParam:
    """
    Creates a user message for the chat completion.

    Args:
        text (str): The content of the user message.

    Returns:
        openaitypes.ChatCompletionUserMessageParam: The user message parameter object.
    """
    return openaitypes.ChatCompletionUserMessageParam({"role": "user", "content": text})


def cli_quick_answer(text: str, model: str, context: str, max_tokens: int):
    """
    Generates a quick answer using the OpenAI Chat API.

    Args:
        text (str): The user's input text.
        model (str): The model to use for generating the answer.
        context (str): The system context.
        max_tokens (int): The maximum number of tokens to generate.

    Returns:
        None
    """

    res = client.chat.completions.create(
        model=model,
        messages=[
            openaitypes.ChatCompletionSystemMessageParam(
                {"role": "system", "content": context}
            ),
            openaitypes.ChatCompletionUserMessageParam(
                {"role": "user", "content": text}
            ),
        ],
        max_tokens=max_tokens,
        n=1,
        stream=True,
    )

    final = ""
    for chunk in res:
        _aux = chunk.choices[0].delta.content or ""
        final += _aux
        sys.stdout.write(_aux)
        sys.stdout.flush()
    print()


if __name__ == "__main__":
    CONFIGS_PATH = os.path.sep.join(
        os.path.dirname(__file__).split(os.path.sep) + ["configs.json"]
    )

    with open(CONFIGS_PATH, "r", encoding="utf-8") as fp:
        settings = json.load(fp)

    CONTEXT = settings["system"].strip()
    MAX_TOKENS = settings["max_tokens"]
    MODEL: str = settings["models"]["gpt3"]
    cli_args: list[str] = [x.strip() for x in sys.argv[1:]]
    if "4" in cli_args:
        MODEL = settings["models"]["gpt4"]
    if "v" in cli_args:
        MODEL = settings["models"]["gpt4vision"]

    if "-p" in cli_args:
        _i = cli_args.index("-p")

        aliases = set(settings["aliases"].keys())
        _user_input: str = " ".join(cli_args[_i + 1 :])
        _user_input_raw_set = set(_user_input.split())
        while not aliases.isdisjoint(_user_input_raw_set):
            alias = aliases.intersection(_user_input_raw_set).pop()
            _user_input = _user_input.replace(alias, settings["aliases"][alias])
            _user_input_raw_set = set(_user_input.split())
        if "-:p" in _user_input:
            _user_input = _user_input.replace("-:p", pyperclip.paste())

        cli_quick_answer(_user_input, MODEL, CONTEXT, MAX_TOKENS)
    else:
        msgs: list[TMESSAGE] = []
        user_input_raw: str = input("> ").strip()
        while user_input_raw not in ("", ":q"):
            match user_input_raw:
                case ":3":
                    MODEL = settings["models"]["gpt3"]
                    print(f"<using {MODEL=}>")
                case ":4":
                    MODEL = settings["models"]["gpt4"]
                    print(f"<using {MODEL=}>")
                case ":c":
                    last_assistant_message = [
                        x["content"] for x in msgs if x["role"] == "assistant"
                    ].pop()
                    if last_assistant_message is None:
                        print("Nenhuma resposta na lista.")
                    else:
                        pyperclip.copy(last_assistant_message)
                case ":ca":
                    ALL_MSGS = "\n\n".join(
                        [f"{x['role']}: {x['content']}" for x in msgs]
                    )
                    if ALL_MSGS is None:
                        print("Nenhuma resposta na lista.")
                    else:
                        pyperclip.copy(ALL_MSGS)
                case _:
                    aliases = set(settings["aliases"].keys())
                    user_input: str = user_input_raw
                    user_input_raw_set = set(user_input.split())
                    while not aliases.isdisjoint(user_input_raw_set):
                        alias = aliases.intersection(user_input_raw_set).pop()
                        user_input = user_input.replace(
                            alias, settings["aliases"][alias]
                        )
                        user_input_raw_set = set(user_input.split())
                    if "-:p" in user_input:
                        user_input = user_input.replace("-:p", pyperclip.paste())
                    msgs.append(user_says(user_input))
                    chat(msgs, MODEL, CONTEXT, MAX_TOKENS)
            user_input_raw = input("\n> ").strip()
