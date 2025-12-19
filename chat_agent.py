from groq import Groq
from dotenv import load_dotenv
import os
import base64
from config import LLM_MODELS, VISION_MODELS


class ChatAgent:
    def __init__(self):
        load_dotenv()
        self.groq_client = Groq(api_key=os.getenv("GROQ_KEY"))
        self.initiate_history()
        self.large_language_model = LLM_MODELS[0]
        self.vision_model = VISION_MODELS[0]

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def read_image(path: str) -> str:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    @staticmethod
    def format_streamlit_image_to_base64(streamlit_file_object):
        bytes_data = streamlit_file_object.read()
        b64_str = base64.b64encode(bytes_data).decode("utf-8")

        mime = streamlit_file_object.type or "image/jpeg"
        return f"data:{mime};base64,{b64_str}"


    def initiate_history(self):
        self.history = [
            {
                "role": "system",
                "content": ChatAgent.read_file("./context.txt")
            }
        ]

    def update_history(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_history(self, type_model):
        if type_model == "large_language_model":
            filtered = []
            for message in self.history:
                if isinstance(message["content"], str):
                    filtered.append(message)

                elif isinstance(message["content"], list):
                    text_content = message["content"][0]["text"]
                    filtered.append({
                        "role": message["role"],
                        "content": f"{text_content} : [IMAGE]"
                    })
            return filtered

        return self.history

    def ask_llm(self, user_interaction: str) -> str:

        self.update_history(role="user", content=user_interaction)

        response = self.groq_client.chat.completions.create(
            messages=self.get_history("large_language_model"),
            model=self.large_language_model,
            temperature=0.4,
        ).choices[0].message.content

        self.update_history(role="assistant", content=response)
        return response

    def ask_vision_model(self, user_interaction: str, image_b64: str):

        content = [
            {"type": "text", "text": user_interaction},
            {"type": "image_url", "image_url": {"url": image_b64}},
        ]

        self.update_history(role="user", content=content)

        response = self.groq_client.chat.completions.create(
            messages=self.get_history("vision_model"),
            model=self.vision_model,
            temperature=0.3,
        ).choices[0].message.content

        self.update_history(role="assistant", content=response)
        return response
