import os
from openai import OpenAI

prompt = "Napisz w którym wieku na świecie pojawili się pierwsi Słowianie."

my_openai_api_key = os.environ.get("OPENAI_API_KEY")
print(f"Using OpenAI API key: {my_openai_api_key}")
if my_openai_api_key is None:
    print("Please set OpenAI API key in environment variable OPENAI_API_KEY")
    exit(1)

client = OpenAI(api_key=my_openai_api_key)

# response = client.responses.create(
#     model="gpt-5-nano",
#     input=prompt
# )
# print(response.output_text)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
print(response.choices[0].message.content)


