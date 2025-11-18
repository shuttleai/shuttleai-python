from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, field_validator

from shuttleai.exceptions import ShuttleAIException
from shuttleai.schemas.common import UsageInfo


class ToolType(str, Enum):
    function = "function"
    mcp = "mcp"


class ImageURL(BaseModel):
    url: str
    detail: Literal["auto", "low", "high"] = "auto"


class ChatMessageContentPartText(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ChatMessageContentPartImage(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: Union[str, ImageURL]

    @field_validator("image_url", mode="before")
    @classmethod
    def validate_image_url(cls, v: Any) -> ImageURL:
        if isinstance(v, str):
            return ImageURL(url=v)
        elif isinstance(v, ImageURL):
            return v
        raise ValueError("image_url must be a string or ImageURL instance")


ChatMessageContentPart = Union[ChatMessageContentPartText, ChatMessageContentPartImage]


class Function(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class FunctionTool(BaseModel):
    type: Literal["function"] = "function"
    function: Function


class MCPHeaders(BaseModel):
    authorization: str


class MCPTool(BaseModel):
    type: Literal["mcp"] = "mcp"
    server_label: str
    server_url: str
    allowed_tools: Optional[List[str]] = None
    require_approval: Literal["always", "never"] = "always"
    headers: Optional[MCPHeaders] = None


Tool = Union[FunctionTool, MCPTool]


class FunctionCall(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str = "call_null"
    type: str
    function: FunctionCall


class NamedFunction(BaseModel):
    name: str


class ChatNamedToolChoice(BaseModel):
    type: Literal["function"] = "function"
    function: NamedFunction


class ChatMessage(BaseModel):
    role: str
    content: Optional[Union[str, List[ChatMessageContentPart]]] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class ChatResponseMessage(BaseModel):
    role: str = "assistant"
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class FinishReason(str, Enum):
    stop = "stop"
    length = "length"
    tool_calls = "tool_calls"


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[FinishReason]


class ChatCompletionStreamResponse(BaseModel):
    id: str
    model: str
    choices: List[ChatCompletionResponseStreamChoice]
    created: Optional[int] = None
    object: Optional[str] = None
    usage: Optional[UsageInfo] = None

    @property
    def first_choice(self) -> ChatCompletionResponseStreamChoice:
        return self.choices[0]

    def print_chunk(self) -> None:
        try:
            print(f"Request ID: {self.id}")
            print(f"Model: {self.model}")
            print(f"Created: {self.created}")
            print(f"Usage: {self.usage}")
            for choice in self.choices:
                print(f"Index: {choice.index}")
                print(f"Delta: {choice.delta}")
                print(f"Finish Reason: {choice.finish_reason}")
        except Exception as e:
            raise ShuttleAIException(f"Error printing response: {e}") from e


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatResponseMessage
    finish_reason: Optional[FinishReason]


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo

    @property
    def first_choice(self) -> ChatCompletionResponseChoice:
        return self.choices[0]

    def print(self) -> None:
        try:
            print(f"Model: {self.model}")
            print(f"Created: {self.created}")
            print(f"Usage: {self.usage}")
            for choice in self.choices:
                print(f"Index: {choice.index}")
                print(f"Message: {choice.message}")
                print(f"Finish Reason: {choice.finish_reason}")
        except Exception as e:
            raise ShuttleAIException(f"Error printing response: {e}") from e


class ResponseFormat(BaseModel):
    type: Literal["text", "json_object"] = "text"
