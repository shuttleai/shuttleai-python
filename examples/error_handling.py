#!/usr/bin/env python

import orjson

from shuttleai import ShuttleAI
from shuttleai.exceptions import ShuttleAIAPIException, ShuttleAIException
from shuttleai.schemas.chat.completions import ChatMessage


def main() -> None:
    model = "shuttle-dino-001"

    client = ShuttleAI()

    try:
        chat_response = client.chat.completions.create(
            model=model,
            messages=[ChatMessage(role="dinosaur", content="what is 5 plus 3")],
        )
        print(chat_response.choices[0].message.content)
    except ShuttleAIException as e:
        if isinstance(e, ShuttleAIAPIException):
            print(orjson.dumps(orjson.loads(e.message), option=orjson.OPT_INDENT_2).decode())
            # optionally grab status code with e.http_status and headers with e.headers
        else:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
