#!/usr/bin/env python


from shuttleai import ShuttleAI
from shuttleai.schemas.chat.completions import (
    Any,
    ChatMessage,
    ChatMessageMCPApprovalResponse,
    DeltaMCPApprovalRequestMessage,
    DeltaMessage,
    MCPHeaders,
    MCPTool,
)  # helpers


def main() -> None:
    model = "shuttle-3.5"

    client = ShuttleAI()

    history: list[Any] = [
        ChatMessage(role="user", content="what is my most used model")
    ]

    tools = [
        MCPTool(
            server_label="ShuttleAI MCP",
            server_url="https://mcp.shuttleai.com/mcp", # ?api_key=shuttle-1234" OR headers below
            headers=MCPHeaders(authorization="Bearer shuttle-1234"),
            require_approval="always"  # or "never" (see examples/stream_chat_with_mcp.py)
        )
    ]

    chat_response = client.chat.completions.create(
        model=model,
        messages=history,
        tools=tools,
        stream=True
    )

    all_text = ""
    for chat in chat_response:
        delta = chat.first_choice.delta
        if isinstance(delta, DeltaMCPApprovalRequestMessage):
            print("\n\nReceived MCP Approval Request:", delta)
            approve_input = input("Approve? (y/n): ").strip().lower()
            approve = (approve_input == "y")
            approval_response = ChatMessageMCPApprovalResponse(
                approve=approve,
                approval_request_id=delta.id,
            )
            if all_text:
                # optionally append the assistant message with all text so far
                history.append(ChatMessage(role="assistant", content=all_text))
            history.append(delta)  # add the MCP approval request message
            history.append(approval_response) # add the MCP approval response to history

            print("\nSending MCP Approval Response:", approval_response, "\n")
            # print("\nCurrent conversation history:", history, "\n")

            chat_response = client.chat.completions.create(
                model=model,
                messages=history,
                tools=tools,
                stream=True
            )

            for chat in chat_response:
                delta = chat.first_choice.delta
                assert isinstance(delta, DeltaMessage)
                if delta.content:
                    print(delta.content, end="", flush=True)

        elif isinstance(delta, DeltaMessage):
            content = delta.content
            if content is not None:
                all_text += content
                print(content, end="", flush=True)


if __name__ == "__main__":
    main()
