import google.generativeai as genai

genai.configure(api_key="AIzaSyBH4COoxm0QRQpMC3il4GYEDna2kVbtzG0")

models = genai.list_models()
for m in models:
    print(m.name)
