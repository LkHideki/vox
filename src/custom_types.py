from typing import Literal
import openai.types.chat as openaitypes

TMESSAGE = (
    openaitypes.ChatCompletionSystemMessageParam
    | openaitypes.ChatCompletionUserMessageParam
    | openaitypes.ChatCompletionAssistantMessageParam
    | openaitypes.ChatCompletionToolMessageParam
    | openaitypes.ChatCompletionFunctionMessageParam
)

TInput = (
    dict[Literal["type"], Literal["texto"]]
    | dict[Literal["type"], Literal["image_url"]]
)
