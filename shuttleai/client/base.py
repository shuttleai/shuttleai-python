import logging
import os
from abc import ABC
from typing import Any, Dict, List, Literal, Optional, Union

import orjson

from shuttleai import __version__
from shuttleai._types import TimeoutTypes
from shuttleai.exceptions import ShuttleAIException
from shuttleai.schemas.chat.completions import (
    ChatMessage,
    ChatMessageMCPApprovalResponse,
    ChatNamedToolChoice,
    DeltaMCPApprovalRequestMessage,
    FunctionTool,
    MCPTool,
    ResponseFormat,
)


class ClientBase(ABC):  # noqa: B024
    _timeout: TimeoutTypes
    _api_key: Optional[str]
    _base_url: Optional[str]
    _logger: logging.Logger
    _default_chat_model: str
    _default_image_model: str
    _default_audio_speech_model: str
    _version: str

    # client options
    api_key: str
    base_url: str

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: TimeoutTypes = 120.0,
    ):
        self._timeout = timeout
        self._api_key = api_key or os.getenv("SHUTTLEAI_API_KEY")
        if not self._api_key:
            raise ShuttleAIException("API key not provided. Please set SHUTTLEAI_API_KEY environment variable.")

        self._base_url = base_url or os.getenv("SHUTTLEAI_API_BASE")
        if not self._base_url:
            self._base_url = "https://api.shuttleai.com/v1"

        self.api_key = self._api_key
        self.base_url = self._base_url

        self._logger = logging.getLogger(__name__)
        self._default_chat_model = "shuttle-3.5"
        self._default_image_model = "shuttle-jaguar"
        self._default_video_model = "sora"
        self._default_audio_speech_model = "eleven_turbo_v2_5"
        self._version = __version__

        if "shuttleai.com" not in self.base_url and "shuttleai.app" not in self.base_url:
            if "api.openai.com" not in self.base_url:
                self._logger.warning(
                    "You are using an **unofficial, unverified** non-ShuttleAI URL. \
                    This is not recommended and may lead to malfunctions. \
                    Your data could be at risk since you are using a 3rd party. \
                    Please use the official ShuttleAI API URL: https://api.shuttleai.com/v1"
                )
            else:
                self._logger.warning(
                    "You are using the official, verified OpenAI API URL. \
                    This library is not meant to replace the OpenAI SDK. \
                    If you wish to use the OpenAI API, consider using their SDK respectively. \
                    Otherwise, please use the official ShuttleAI API URL: https://api.shuttleai.com/v1"
                )
            self._default_chat_model = "gpt-4o-mini"
            self._default_image_model = "dall-e-3"
            self._default_audio_speech_model = "whisper-1"

        self._logger.info(f"ShuttleAI API client initialized with base URL: {self._base_url}")

    def _build_sampling_params(
        self,
        max_tokens: Optional[int],
        temperature: Optional[float],
        top_p: Optional[float],
    ) -> Dict[str, Any]:
        return {
            k: v
            for k, v in {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }.items()
            if v is not None
        }

    def _parse_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        parsed = []
        for message in messages:
            if isinstance(message, ChatMessage):
                msg = message.model_dump(mode="json", exclude_none=True)
            elif (
                isinstance(message, ChatMessageMCPApprovalResponse)
                or isinstance(message, DeltaMCPApprovalRequestMessage)
            ):
                msg = message.model_dump(mode="json", exclude_none=True)
            else:
                msg = message
            if isinstance(msg.get("content"), list):
                for part in msg["content"]:
                    if part.get("type") == "image_url" and isinstance(part.get("image_url"), str):
                        part["image_url"] = {"url": part["image_url"], "detail": "auto"}
            parsed.append(msg)
        return parsed

    def _parse_tools(self, tools: List[Any]) -> List[Dict[str, Any]]:
        parsed = []
        for tool in tools:
            if isinstance(tool, (FunctionTool, MCPTool)):
                t = tool.model_dump(mode="json", exclude_none=True)
            else:
                t = tool
            # For backward compat if flat function
            if t.get("type") == "function" and "function" not in t:
                func = {
                    "name": t["name"],
                    "description": t.get("description"),
                    "parameters": t.get("parameters"),
                }
                t = {"type": "function", "function": func}
            parsed.append(t)
        return parsed

    def _parse_tool_choice(self, tool_choice: Any) -> Any:
        if isinstance(tool_choice, ChatNamedToolChoice):
            return tool_choice.model_dump(mode="json", exclude_none=True)
        elif isinstance(tool_choice, dict):
            return tool_choice
        elif isinstance(tool_choice, str):
            return tool_choice
        return None

    def _parse_response_format(self, response_format: Any) -> Optional[Dict[str, Any]]:
        if isinstance(response_format, ResponseFormat):
            return response_format.model_dump(mode="json", exclude_none=True)
        elif isinstance(response_format, dict):
            return response_format
        return None

    def _make_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        if "model" not in request_data:
            request_data["model"] = getattr(self, f"_default_{endpoint}_model")
        self._logger.debug(f"{endpoint.capitalize()} request: {request_data}")
        return request_data

    def _make_chat_request(
        self,
        messages: List[Any],
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Optional[Any] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        response_format: Optional[Any] = None,
        reasoning_effort: Optional[Literal["none", "minimal", "low", "high"]] = None,
        stream: Optional[bool] = None,
    ) -> Dict[str, Any]:
        request_data: Dict[str, Any] = {
            "messages": self._parse_messages(messages),
        }
        if model:
            request_data["model"] = model
        if tools:
            request_data["tools"] = self._parse_tools(tools)
        if tool_choice:
            request_data["tool_choice"] = self._parse_tool_choice(tool_choice)
        if response_format:
            request_data["response_format"] = self._parse_response_format(response_format)
        if reasoning_effort:
            request_data["reasoning_effort"] = reasoning_effort
        if stream is not None:
            request_data["stream"] = stream
        if stop is not None:
            request_data["stop"] = stop
        if frequency_penalty is not None:
            request_data["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            request_data["presence_penalty"] = presence_penalty
        request_data.update(self._build_sampling_params(max_tokens, temperature, top_p))
        return self._make_request("chat", request_data)

    def _make_image_request(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        request_data: Dict[str, Any] = {
            "prompt": prompt,
        }
        if model:
            request_data["model"] = model
        return self._make_request("image", request_data)

    def _make_video_request(
        self,
        prompt: str,
        model: str = "sora",
        width: int = 480,
        height: int = 480,
        n_seconds: int = 5,
        # n_variants: int = 1,
    ) -> Dict[str, Any]:
        request_data: Dict[str, Any] = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "n_seconds": n_seconds,
            # "n_variants": n_variants,
        }
        return self._make_request("video", request_data)

    def _make_audio_speech_request(
        self,
        input: str,
        model: str = "eleven_turbo_v2_5",
        voice: Optional[str] = None,
    ) -> Dict[str, Any]:
        request_data: Dict[str, Any] = {
            "input": input,
            "model": model,
            **({"voice": voice} if voice else {}),
        }
        return self._make_request("audio_speech", request_data)

    def _make_audio_trans_request(  # translations/transcriptions share similar request/response schemas
        self,
        file: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        request_data: Dict[str, Any] = {
            "file": file,
        }
        if model:
            request_data["model"] = model
        return self._make_request("audio_trans", request_data)

    def _process_line(self, line: Union[str, bytes]) -> Optional[Dict[str, Any] | Any]:
        line = line.encode("utf-8") if isinstance(line, str) else line
        if line.startswith(b"data: "):
            line = line[6:].strip()
            if line != b"[DONE]":
                return orjson.loads(line)
        return None
