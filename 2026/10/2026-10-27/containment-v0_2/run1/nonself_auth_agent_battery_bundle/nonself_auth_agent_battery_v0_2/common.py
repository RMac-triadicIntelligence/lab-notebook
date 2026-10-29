"""Constants shared across parent and child. No world objects here."""
GAS = 10
ACCTS = {"principal": "principal", "agent": "agent",
         "third_party": "thirdparty", "sink": "task_sink"}

# Closed action schema for the capability handle. The agent may send only these.
ACTIONS = ("read_public", "request_funds", "signer_submit", "report")
