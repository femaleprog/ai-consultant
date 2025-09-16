import os
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()  


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key= os.getenv("HF_TOKEN"),
)

completion = client.chat.completions.create(
    model="openai/gpt-oss-120b:cerebras",
    messages=[
        {
            "role": "user",
            "content": "Explain the MECE framework in consulting.",
            
        }
    ],
    max_tokens=300,
    temperature=0.7,
    top_p=0.95,
)

print(completion.choices[0].message)