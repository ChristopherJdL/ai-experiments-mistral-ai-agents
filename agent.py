import os
from mistralai import Mistral, FunctionResultEntry
import json
from tools.flight.flight_tool import get_flight_data_by_callsign, FETCH_FLIGHT_BY_CALLSIGN_TOOL_DEFINITION

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key)

flight_agent = client.beta.agents.create(model="mistral-medium-2505",
                                            description="Specialized flight tracking agent that automatically identifies flight callsigns and numbers from user queries to retrieve real-time flight status, departure/arrival information, and operational updates using aviation data APIs.",
                                            name="Flight Agent",
                                            tools=[FETCH_FLIGHT_BY_CALLSIGN_TOOL_DEFINITION],
                                            instructions="""
                                            Flight tracking agent specialized in providing real-time flight status, departure, and arrival updates.

                                            Automatically identifies and extracts flight callsigns or numbers from user queries in the following formats:
                                            - IATA/ICAO Code + Number: "UA1234", "UAL1234", "DL890", "DAL890"

                                            When a flight identifier is detected:
                                            1. Extracts the callsign/number
                                            2. Calls the fetch_flight_by_callsign tool
                                            3. Returns structured flight status, departure, and arrival updates

                                            Focus on clear, concise, and accurate flight tracking responses.

                                            Examples:
                                            - "What’s the status of United 1234?" → Call tool with "UAL1234"
                                            - "Is Delta 890 delayed?" → Call tool with "DAL890"
                                            """)

conversation_beginning = True
response = None
recent_conversation_id = None

while True:
    inp = input(">")

    if conversation_beginning:
        response = client.beta.conversations.start(
            agent_id=flight_agent.id,
            inputs=[{"role": "user", "content": inp}],
            store=True
        )
    elif not conversation_beginning:
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
    conversation_beginning = False
