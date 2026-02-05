"""Simple OpenAI client example - ask a question and get a response."""

import os

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:

    load_dotenv()
    load_dotenv(".env.local", override=True)

    print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

    # Initialize the client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Simple question
    question = "What is the capital of France?"

    # Using Chat Completions API (most common)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    )

    # Get the answer
    answer = response.choices[0].message.content
    print(f"Question: {question}")
    print(f"Answer: {answer}")


# ---------------------------------------------------------
# Alternative: Using the Responses API (simpler for one-off)
# ---------------------------------------------------------
# response2 = client.responses.create(
#     model="gpt-4.1-mini",
#     instructions="You are a helpful assistant.",
#     input="What is 2 + 2?",
# )

# print(f"\nResponses API answer: {response2.output_text}")

if __name__ == "__main__":
    main()
