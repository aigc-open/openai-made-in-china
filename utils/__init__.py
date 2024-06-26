import functools
import os
import time
import time
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from loguru import logger
from sparkai.core.utils.function_calling import convert_to_openai_tool


def logger_execute_time(doc="执行时间"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """计算方法执行时间，并输出执行时间"""
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"{doc}: {execution_time}")
            return result

        return wrapper

    return decorator





class FunctionCall(BaseModel):
    name: Optional[str] = None
    arguments: str


class ToolCall(BaseModel):
    index: Optional[int] = None
    id: Optional[str] = None
    function: FunctionCall
    type: Optional[str] = "function"


class Function(BaseModel):
    name: str
    description: Optional[str] = Field(default="")
    parameters: Optional[dict] = None


class Tool(BaseModel):
    type: Literal["function", "code_interpreter"] = "function"
    function: Optional[Function] = None


class ChatMessage(BaseModel):
    role: Optional[str] = None
    tool_call_id: Optional[str] = None
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    tool_calls: Optional[List[ToolCall]] = None

    def __str__(self) -> str:
        if self.role == "system":
            return f"system:\n{self.content}\n"

        elif self.role == "function":
            return f"function name={self.name}:\n{self.content}\n"

        elif self.role == "user":
            if self.content is None:
                return "user:\n</s>"
            else:
                return f"user:\n</s>{self.content}\n"

        elif self.role == "assistant":
            if self.content is not None and self.function_call is not None:
                return f"assistant:\n{self.content}\nassistant to={self.function_call.name}:\n{self.function_call.arguments}</s>"

            elif self.function_call is not None:
                return f"assistant to={self.function_call.name}:\n{self.function_call.arguments}</s>"

            elif self.content is None:
                return "assistant"

            else:
                return f"assistant:\n{self.content}\n"

        else:
            raise ValueError(f"Unsupported role: {self.role}")


class ChatInput(BaseModel):
    messages: List[ChatMessage]
    functions: Optional[List[Function]] = None
    tools: Optional[List[Tool]] = None
    temperature: float = 0.9
    stream: bool = False
    model: str = None
    stop: list[str] = None
    key: str = None


class Choice(BaseModel):
    message: ChatMessage
    finish_reason: str = "stop"
    index: int = 0

    @classmethod
    def from_message(cls, message: ChatMessage, finish_reason: str):
        return cls(message=message, finish_reason=finish_reason)


class ChatCompletion(BaseModel):
    id: str
    object: str = "chat.completion"
    created: float = Field(default_factory=time.time)
    choices: List[Choice]


class StreamChoice(BaseModel):
    delta: ChatMessage
    finish_reason: Optional[str] = "stop"
    index: int = 0


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: float = Field(default_factory=time.time)
    choices: List[StreamChoice]
