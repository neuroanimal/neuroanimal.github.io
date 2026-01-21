import datetime
import os
import time

from openai import OpenAI


prompt = "Napisz w którym wieku na świecie pojawili się pierwsi Słowianie."

my_openai_api_key = os.environ.get("OPENAI_API_KEY")
print(f"Using OpenAI API key: {my_openai_api_key}")
if my_openai_api_key is None:
  print("Please set OpenAI API key in environment variable OPENAI_API_KEY")
  exit(1)

client = OpenAI(api_key=my_openai_api_key)

models = [
  #"gpt-3.5-turbo",
  #"gpt-3.5-turbo-16k",
  #"gpt-3.5-turbo-instruct",
  #"gpt-3.5-turbo-instruct-0914",
  #"gpt-3.5-turbo-1106",
  #"gpt-3.5-turbo-0125",
  "gpt-4o-mini",
  "gpt-5-nano",
]

elapsed = []
for selected_model in models:
  print(f"Sending client response request to LLM model {selected_model}")
  tic = time.time_ns()
  response = client.responses.create(
    model=selected_model,
    input=prompt
  )
  toc = time.time_ns()
  tec = toc - tic
  elapsed.append(tec)
  print(f"Response from server of LLM model {selected_model}: {response.output_text}\n")
  time.sleep(1)

  print(f"Sending client chat completion request to LLM model {selected_model}")
  tic = time.time_ns()
  response = client.chat.completions.create(
    model=selected_model,
    messages=[{"role": "user", "content": prompt}]
  )
  toc = time.time_ns()
  tec = toc - tic
  elapsed.append(tec)
  print(f"Chat completion from LLM model {selected_model}: {response.choices[0].message.content}\n")
  time.sleep(1)

print("Performance measurements:")
print("  Legend:")
print("    NS1 -- elapsed Timestamp[ns] using Method 1")
print("    NS2 -- elapsed Timestamp[ns] using Method 2")
print("    DT1 -- elasped DateTime format using Method 1")
print("    DT2 -- elapsed DateTime format using Method 2")
print("    LLM -- name with version of the LLM model used")
print("  NS1  NS2  DT1  DT2  LLM")
i = 0
for selected_model in models:
  ns1 = elapsed[i]
  i += 1
  ns2 = elapsed[i]
  i += 1
  dt1 = datetime.datetime.fromtimestamp(ns1/1000000000).strftime('%H:%M:%S,%f')
  dt2 = datetime.datetime.fromtimestamp(ns2/1000000000).strftime('%H:%M:%S,%f')
  print(f"  {ns1}  {ns2}  {dt1}  {dt2}  {selected_model}")

