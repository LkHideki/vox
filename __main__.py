import os, pyperclip, json, sys
from src.vox import cli_quick_answer, chat, user_says
from src.custom_types import TMESSAGE

CONFIGS_PATH = os.path.sep.join(
    os.path.dirname(__file__).split(os.path.sep) + ["configs.json"]
)

with open(CONFIGS_PATH, "r", encoding="utf-8") as fp:
    settings = json.load(fp)

CONTEXT = settings["system"].strip()
MAX_TOKENS = settings["max_tokens"]
MODEL: str = settings["models"]["gpt4"]
cli_args: list[str] = [x.strip() for x in sys.argv[1:]]
if "3" in cli_args:
    MODEL = settings["models"]["gpt3"]
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
            case ":model":
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
                ALL_MSGS = "\n\n".join([f"{x['role']}: {x['content']}" for x in msgs])
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
                    user_input = user_input.replace(alias, settings["aliases"][alias])
                    user_input_raw_set = set(user_input.split())
                if "-:p" in user_input:
                    user_input = user_input.replace("-:p", pyperclip.paste())
                msgs.append(user_says(user_input))
                chat(msgs, MODEL, CONTEXT, MAX_TOKENS)
        user_input_raw = input("\n> ").strip()
