import os
from mistralai import Mistral, FunctionResultEntry
from tools.flight.flight_tool import get_flight_data_by_callsign, FETCH_FLIGHT_BY_CALLSIGN_TOOL_DEFINITION
import json

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key)

flight_agent = client.beta.agents.create(model="mistral-medium-2505",
                                          description="Agent for flight tracking. Capable of getting real-time flight information.",
                                          name="Simple Agent",
                                          tools=[FETCH_FLIGHT_BY_CALLSIGN_TOOL_DEFINITION],
                                          instructions="You're an agent which aim is to help with queries related to aviation." +
                                          "You're capable of getting real-time information about a flight with a tool that requires specific callsign or flight number.")

first_start = True
response = None
recent_conversation_id = None

while True:
    inp = input(">")
    #under the hood prompt enhancement.
    
    if first_start:
        response = client.beta.conversations.start(
            agent_id=flight_agent.id,
            inputs=[{"role": "user", "content": inp}],
            store=True
        )
    elif not first_start:
        response = client.beta.conversations.append(
            conversation_id=recent_conversation_id,
            inputs = [{"role": "user", "content": inp}]
        )


    if response.outputs[-1].type == "function.call":
        if response.outputs[-1].name == "get_flight_data_by_callsign":
            function_result = get_flight_data_by_callsign(**json.loads(response.outputs[-1].arguments))
            user_function_calling_entry = FunctionResultEntry(
                tool_call_id=response.outputs[-1].tool_call_id,
                result=json.dumps(function_result),
            )

            recent_conversation_id = response.conversation_id

            response = client.beta.conversations.append_stream(
                conversation_id=response.conversation_id,
                inputs=[user_function_calling_entry]
            )
            
            for chunk in response:
                if chunk.event.startswith("message.output"):
                    print(chunk.data.content, end= "")
                
    elif response.outputs[-1].type.startswith("message.output"):
        recent_conversation_id = response.conversation_id
        print(response.outputs[-1].content)
    first_start = False
