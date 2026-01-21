from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from pprint import pprint as pp
# from ppretty import ppretty as pp

import asyncio
import nest_asyncio
import importlib
import os


AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")

os.environ["OPENAI_API_BASE"]="http://localhost:11434/v1"


def gpt4o_mini_agent_using_google_adk(agent_name, agent_descr, agent_instr):
    agent = LlmAgent(
            name=agent_name,
            description=agent_descr,
            instruction=agent_instr,
            model=AGENT_MODEL
    )
    return agent

# Define an asynchronous function to send a query to the agent and handle its response
async def call_agent_async(query: str):
    print(f"\n>>> User Query: {query}")

    # Package the user's query into ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    # Iterate through streamed agent responses
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response(): # Check if this is the final message from the agent
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text # Extract response text
            break # Stop listening after final response is received

    print(f"<<< Agent Response: {final_response_text}")


importlib.invalidate_caches()
nest_asyncio.apply()  # Required for async in notebooks


gpt4o_mini_welcome_agent = gpt4o_mini_agent_using_google_adk(
    "WelcomeAgent",
    "An agent that welcomes the user.",
    "Please always greet an user politely"
)
print(f"Agent '{gpt4o_mini_welcome_agent.name}' created. More details below:")
# pp(dir(gpt4mini_agent), show_protected=True, show_static=True, show_properties=True)
# pp(dir(gpt4mini_agent))
pp(vars(gpt4o_mini_welcome_agent), indent=2)


# Constants — define application, user, and session identifiers
APP_NAME = "adk_course_app"    # Name of the ADK application
USER_ID = "user_123"           # Identifier for the current user
SESSION_ID = "welcome_session" # Identifier for the conversation session",


# Set up session service and create a session
session_service = InMemorySessionService()
asyncio.run(
    session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
)

# Set up a runner to orchestrate the agent
runner = Runner(agent=gpt4o_mini_welcome_agent, app_name=APP_NAME, session_service=session_service)

# Run the interaction
asyncio.run(call_agent_async("Hi there!"))


