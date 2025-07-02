import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key)

simple_agent = client.beta.agents.create(model="mistral-medium-2505",
                                          description="A simple Agent with persistent state",
                                          name="Simple Agent",
                                          tools=[{"type": "web_search"}],)
response = client.beta.conversations.start(
    agent_id=simple_agent.id,
    inputs="There's an event tomorrow right? in the plaza of Trafalgar square about McLaren and Sonic? Please tell me what the sonic booth  will be about and search social media about the latest updates ",
    #store=False
)

print(response.outputs)