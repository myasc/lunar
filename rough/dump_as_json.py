import json

dict_to_dump = {
    "api_key": "bt77",
    "api_secret": "bt77"
}

filename = "../../api_credentials.json"
with open(filename, "w") as f:
    json.dump(dict_to_dump, f)
