#!/usr/bin/env python


from shuttleai import ShuttleAI
from shuttleai.schemas.chat.completions import ChatMessage, DeltaMessage, MCPHeaders, MCPTool  # helpers


def main() -> None:
    model = "shuttle-3.5"

    client = ShuttleAI()

    chat_response = client.chat.completions.create(
        model=model,
        messages=[ChatMessage(role="user", content="what is my most used model")],
        tools=[
            MCPTool(
                server_label="ShuttleAI MCP",
                server_url="https://mcp.shuttleai.com/mcp", # ?api_key=shuttle-1234" OR headers below
                headers=MCPHeaders(authorization="Bearer shuttle-1234"),
                require_approval="never"  # or "always" (see examples/stream_chat_with_mcp_require_approval.py)
            )
        ],
        stream=True
    )
    for chat in chat_response:
        delta = chat.first_choice.delta
        assert isinstance(delta, DeltaMessage)
        print(delta.content or "", end="", flush=True)


if __name__ == "__main__":
    main()
