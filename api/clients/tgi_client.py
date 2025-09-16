from text_generation import Client

client = Client("http://localhost:8080", timeout=300)
out = client.generate("Explain the MECE framework in consulting.", max_new_tokens=64)
print(out.generated_text)
