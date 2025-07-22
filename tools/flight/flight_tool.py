import sys
import requests
from tools.flight.relative_location_tool import get_location_with_type

ENDPOINT = "https://opendata.adsb.fi/api/v2/callsign/{callsign}"
TIMEOUT  = 10          # seconds
CALLSIGN = "N718FX"    # remplacez par le callsign de votre choix


def get_flight_data_by_callsign(callsign: str) -> dict | None:
    url = ENDPOINT.format(callsign=callsign)
    try:
        resp = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException:
        return {"error": "internal error occurred."}

    if resp.status_code != 200:
        sys.stderr.write(f"[HTTP {resp.status_code}] {resp.reason}\n")
        return {"error": "non-ok HTTP response code."}

    try:
        data = resp.json()
    except ValueError:
        sys.stderr.write("[Error] JSON Parsing Error\n")
        return None

    if not data.get("ac"):
        sys.stderr.write("[Info] Aucun aéronef actif pour ce callsign\n")
        return None
    
    latitude, longitude = data["ac"][0]["lat"], data["ac"][0]["lon"]
    flying_over = get_location_with_type(latitude, longitude)

    return {"flying_over": flying_over} | data


if __name__ == "__main__":
    result = get_flight_data_by_callsign(CALLSIGN)
    if result:
        # Affiche le premier enregistrement trouvé
        print(result["ac"][0])


# JSON Schema for AI Function Calling
FETCH_FLIGHT_BY_CALLSIGN_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_flight_data_by_callsign",
        "description": "Retrieves comprehensive real-time and historical flight data from OpenSky Network API based on flight number or callsign. Returns current position, altitude, velocity, route information, and historical flights.",
        "parameters": {
            "type": "object",
            "properties": {
                "callsign": {
                    "type": "string",
                    "description": "The flight number or callsign to search for (e.g., 'DLH441', 'UAL123', 'AF1234'). Can be with or without airline prefix."
                }
            },
            "required": ["callsign"],
            "additionalProperties": False
        }
    }
}