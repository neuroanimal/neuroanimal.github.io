import datetime
import os
import time

from openai import OpenAI
from pydantic import BaseModel


def measure_time_performance(*args, pre_msg, function, post_msg, elapsed, delay):
  print(pre_msg)
  tic = time.time_ns()
  result = function(*args)
  toc = time.time_ns()
  tec = toc - tic
  elapsed.append(tec)
  print(post_msg + str(result) + "\n")
  time.sleep(delay)


def openai_resp_api_create_simple(model, input_prompt):
  response = client.responses.create(
    model=model,
    input=input_prompt,
  )
  txt = response.output_text
  return txt


def openai_resp_api_create_custom(model, input_instruction, input_prompt, wanted_format_of_output):
  response = client.responses.create(
    model=model,
    input=[
      {
        "role": "system",
        "content": input_instruction,
      },
      {
        "role": "user",
        "content": input_prompt,
      },
    ],
    text={
      "format": wanted_format_of_output
    },
  )
  txt = response.output_text
  return txt


def openai_resp_api_parse(model, input_instruction, input_prompt, wanted_format_of_output):
  response = client.responses.parse(
    model=model,
    input=[
      {
        "role": "system",
        "content": input_instruction,
      },
      {
        "role": "user",
        "content": input_prompt,
      },
    ],
    text_format=wanted_format_of_output,
  )
  out = response.output_parsed
  return out


def openai_compl_api_create(model, input_instruction, input_prompt, wanted_format_of_output):
  response = client.chat.completions.create(
    model=model,
    messages=[
      {
        "role": "system",
        "content": input_instruction,
      },
      {
        "role": "user",
        "content": input_prompt
      }
    ],
    response_format=wanted_format_of_output
  )
  out = response.choices[0].message.content
  return out


class Etnogeneza(BaseModel):
  wiek_minimalny: str
  wiek_maksymalny: str
  grupa_etnolingwistyczna: str
  ziemie: list[str]


FORMAT_JSON_OBJECT = {"type": "json_object"}
FORMAT_JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "explanation": {"type": "string"},
          "output": {"type": "string"}
        },
        "required": ["explanation", "output"],
        "additionalProperties": False
      }
    },
    "final_answer": {"type": "string"}
  },
  "required": ["steps", "final_answer"],
  "additionalProperties": False
}
FORMAT_JSON_INSTANCE_DATA_RESP = {
  "type": "json_schema",
  "name": "expected_response",
  "schema": FORMAT_JSON_SCHEMA,
  "strict": True
}
FORMAT_JSON_INSTANCE_DATA_COMPL = {
  "type": "json_schema",
  "json_schema" : {
    "name": "expected_response",
    "schema": FORMAT_JSON_SCHEMA,
    "strict": True
  }
}
instruction = "Odpowiedz zwięźle, poprawnie, w krokach i w podanym formacie."
prompt = "Napisz w którym wieku na świecie pojawili się pierwsi Słowianie."

my_openai_api_key = os.environ.get("OPENAI_API_KEY")
print(f"Using OpenAI API key: {my_openai_api_key}\n")
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

  # method 1: responses.create() as simple answer for simple prompt
  measure_time_performance(
    selected_model, prompt,
    pre_msg=f"Sent request to LLM model {selected_model} through OpenAI Responses API using simple create(): {prompt}",
    function=openai_resp_api_create_simple,
    post_msg=f"Received response from LLM model {selected_model} through OpenAI Responses API on simple create():: ",
    elapsed=elapsed,
    delay=1,  # sleep for 1 second
  )

  # method 2: responses.create() as JSON Object answer for given prompt and instruction (with JSON keyword inside of the instruction)
  measure_time_performance(
    selected_model, instruction, prompt + " Format to obiekt JSON.", FORMAT_JSON_OBJECT,
    pre_msg=f"Sent request to LLM model {selected_model} through OpenAI Responses API using custom create(): {prompt}",
    function=openai_resp_api_create_custom,
    post_msg=f"Received response from LLM model {selected_model} through OpenAI Responses API on custom create():: ",
    elapsed=elapsed,
    delay=1,  # sleep for 1 second
  )

  # method 3: responses.create() as JSON Instance Data matching given JSON Schema for given prompt and instruction
  # TODO

  # method 4: responses.parse() as JSON Instance Data matching pydantic JSON Schema (generated from class structure given) for given prompt and instruction
  measure_time_performance(
    selected_model, instruction, prompt, Etnogeneza,
    pre_msg=f"Sent request to LLM model {selected_model} through OpenAI Responses API using parse(): {prompt}",
    function=openai_resp_api_parse,
    post_msg=f"Received response from LLM model {selected_model} through OpenAI Responses API on parse():: ",
    elapsed=elapsed,
    delay=1,  # sleep for 1 second
  )

  # method 5: responses.stream() as JSON Instance Data matching pydantic JSON Schema (generated from class structure given) for given prompt and instruction
  # TODO

  # method 6: chat_completion.create() as JSON Instance Data matching given JSON Schema for given prompt and instruction
  measure_time_performance(
    selected_model, instruction, prompt, FORMAT_JSON_INSTANCE_DATA_COMPL,
    pre_msg=f"Sent request to LLM model {selected_model} through OpenAI Completions API using create(): {prompt}",
    function=openai_compl_api_create,
    post_msg=f"Received response from LLM model {selected_model} through OpenAI Completions API on create():: ",
    elapsed=elapsed,
    delay=1,  # sleep for 1 second
  )

print("Performance measurements:")
print("  Legend:")
print("    NS1 -- elapsed Timestamp[ns] using Method 1: responses API - create simple text")
print("    NS2 -- elapsed Timestamp[ns] using Method 2: responses API - create JSON object")
print("    NS3 -- elapsed Timestamp[ns] using Method 3: responses API - create JSON instance of schema (standard JSON schema)")
print("    NS4 -- elapsed Timestamp[ns] using Method 4: responses API - parse class structure (pydantic JSON schema)")
print("    NS5 -- elapsed Timestamp[ns] using Method 5: responses API - stream class structure (pydantic JSON schema)")
print("    NS6 -- elapsed Timestamp[ns] using Method 6: completion API - create JSON instance of schema (standard JSON schema)")
print("    DT1 -- elasped DateTime format using Method 1")
print("    DT2 -- elapsed DateTime format using Method 2")
print("    DT3 -- elapsed DateTime format using Method 3")
print("    DT4 -- elapsed DateTime format using Method 4")
print("    DT5 -- elapsed DateTime format using Method 5")
print("    DT6 -- elapsed DateTime format using Method 6")
print("    LLM -- name with version of the LLM model used")
print("  NS1  NS2  NS3  NS4  NS5  NS6  DT1  DT2  DT3  DT4  DT5  DT6  LLM")
i = 0
for selected_model in models:
  ns1 = elapsed[i]
  i += 1
  ns2 = elapsed[i]
  i += 1
  dt1 = datetime.datetime.fromtimestamp(ns1/1000000000).strftime('%H:%M:%S,%f')
  dt2 = datetime.datetime.fromtimestamp(ns2/1000000000).strftime('%H:%M:%S,%f')
  print(f"  {ns1}  {ns2}  {ns3}  {ns4}  {ns5}  {ns6}  {dt1}  {dt2}  {dt3}  {dt4}  {dt5}  {dt6}  {selected_model}")


