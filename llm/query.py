import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class MilonQuery:
    def __init__(self):
        self.client = OpenAI()
        self.prompt_id = os.getenv("MILON_PROMPT_ID")
        self.prompt_version = os.getenv("MILON_PROMPT_VERSION")
        self.vector_store_id = os.getenv("MILON_VECTOR_STORE_ID")
        self.previous_response_id = None

    def query(self, text: str) -> str:
        try:
            params = {
                "prompt": {"id": self.prompt_id, "version": self.prompt_version},
                "input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}],
                "reasoning": {},
                "tools": [{"type": "file_search", "vector_store_ids": [self.vector_store_id]}],
                "max_output_tokens": 2048,
                "store": True
            }

            if self.previous_response_id:
                params["previous_response_id"] = self.previous_response_id

            response = self.client.responses.create(**params)
            self.previous_response_id = response.id

            if not hasattr(response, "output") or not response.output:
                return ""

            texts = []
            for item in response.output:
                if item.type == "message" and hasattr(item, "content"):
                    for content_item in item.content:
                        if content_item.type == "output_text" and content_item.text:
                            texts.append(content_item.text)

            return "\n\n".join(texts).strip()

        except Exception as e:
            return f"Error: {str(e)}"


# Default instance
milon = MilonQuery()

if __name__ == "__main__":
    # First request
    res1 = milon.query("What are the steps for onboarding?")
    print("Response 1:")
    print(res1)

    # Second request continues the conversation
    res2 = milon.query("תסביר את הבעיה, לא הבנתי")
    print("\nResponse 2:")
    print(res2)
