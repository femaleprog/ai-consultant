from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)

def chat(messages, **kwargs):
    resp = client.chat.completions.create(
        model=os.getenv("MODEL_ID", "openai/gpt-oss-20b"),
        messages=messages,
        max_tokens=kwargs.get("max_tokens", 300),
        temperature=kwargs.get("temperature", 0.7),
        top_p=kwargs.get("top_p", 1.0),
    )
    return resp.choices[0].message.content
