from typing import Literal
import openai.types.chat as openaitypes

TMESSAGE = (
    openaitypes.ChatCompletionSystemMessageParam
    | openaitypes.ChatCompletionUserMessageParam
    | openaitypes.ChatCompletionAssistantMessageParam
    | openaitypes.ChatCompletionToolMessageParam
    | openaitypes.ChatCompletionFunctionMessageParam
)

# TInput2 = {"type": _L["text"], "text": str} | {
#     "type": _L["image_url"],
#     "image_url": str,
# }

TInput = (
    dict[Literal["type"], Literal["texto"]]
    | dict[Literal["type"], Literal["image_url"]]
)
