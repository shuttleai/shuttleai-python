#!/usr/bin/env python


from shuttleai import ShuttleAI
from shuttleai.schemas.chat.completions import ChatMessage, MCPHeaders, MCPTool  # helpers


def main() -> None:
    model = "shuttle-3.5"

    client = ShuttleAI()

    chat_response = client.chat.completions.create(
        model=model,
        messages=[ChatMessage(role="user", content="do you have access to any mcp tools")],
        tools=[
            MCPTool(
                server_label="ShuttleAI MCP",
                server_url="https://mcp.shuttleai.com/mcp", # ?api_key=shuttle-1234" OR headers below
                headers=MCPHeaders(authorization="Bearer shuttle-1234")
            )
        ]
    )
    print(chat_response.choices[0].message.content)


if __name__ == "__main__":
    main()
