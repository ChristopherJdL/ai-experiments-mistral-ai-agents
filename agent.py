import os
from mistralai import Mistral, FunctionResultEntry
from tools.flight.flight_tool import get_flight_data_by_callsign
import json

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key)

flight_agent = client.beta.agents.create(model="mistral-medium-2505",
                                          description="Agent for flight tracking. Capable of getting real-time flight information.",
                                          name="Simple Agent",
                                          tools=[{"type": "function",
                                                  
                                                  "function": {
                                                        "name": "get_flight_data_by_callsign",
                                                        "description": "Get real-time flight information.",
                                                        "parameters": {
                                                            "type": "object",
                                                            "properties": {
                                                                "flight_number": {
                                                                    "type": "string",
                                                                },
                                                            },
                                                            "required": [
                                                                "flight_number",
                                                            ]
                                                  }}}
                                                ],)

response = client.beta.conversations.start(
    agent_id=flight_agent.id,
    inputs=[{"role": "user", "content": "Whats the state of the flight TVF67NZ?"}],
    #store=False
)

if response.outputs[-1].type == "function.call":
    if response.outputs[-1].name == "get_flight_data_by_callsign":
        function_result = get_flight_data_by_callsign(**json.loads(response.outputs[-1].arguments))
        user_function_calling_entry = FunctionResultEntry(
            tool_call_id=response.outputs[-1].tool_call_id,
            result=json.dumps(function_result),
        )

        response = client.beta.conversations.append_stream(
            conversation_id=response.conversation_id,
            inputs=[user_function_calling_entry]
        )
        
        print(json.dumps(function_result))
        ## print(response.outputs[-1])
        for chunk in response:
            if chunk.event.startswith("message.output"):
                print(chunk.data.content, end= "")


   ##print(chunk["choices"]["delta"]["content"], end="", flush=True)