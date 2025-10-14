import google.generativeai as genai

genai.configure(api_key="your own API key")

models = genai.list_models()
for m in models:
    print(m.name)

