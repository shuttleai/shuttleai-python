#!/usr/bin/env python


from shuttleai import ShuttleAI
from shuttleai.schemas.chat.completions import ChatMessage  # Helper for messages


def main() -> None:
    model = "claude-3.7-sonnet"

    client = ShuttleAI()

    chat_response = client.chat.completions.create(
        model=model,
        messages=[ChatMessage(role="user", content="what is 5 plus 3")],
        reasoning_effort="low"
    )
    print("Thinking:", chat_response.first_choice.message.reasoning_content)
    print("\n")
    print("Final Response:", chat_response.choices[0].message.content)
    # Output:
    #  Thinking:  This is a simple arithmetic problem. I need to compute 5 + 3.
    #    5 + 3 = 8
    #
    #    So the answer is 8.
    #
    #  Final Response:  5 plus 3 equals 8.


if __name__ == "__main__":
    main()
