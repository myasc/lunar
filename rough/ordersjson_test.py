import json
import datetime as dt
import os

dict_ = {}
dict_["type"] = "request"
dict_["price"] = 99
dict_["qty"] = 1807
dict_["orderid"] = "99ZK"
dict_["createdat"] = str(dt.datetime.now().isoformat())

file_path = "/Users/asc/Documents/atdv/Lunar/rough/test_order2.json"


def save_dictionary_to_json_file(dictionary, json_file_path):
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json_file.write("[]")

    with open(json_file_path, "r+") as json_file:
        data = json.load(json_file)
        data.append(dictionary)
        json_file.seek(0)
        json.dump(data, json_file)


def read_latest_json_todict(json_file_path):
    if not os.path.exists(json_file_path):
        return {}
    else:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
        latest_timestamp = dt.datetime.fromisoformat(data[0]["createdat"])
        latest_dict = data[0]
        if len(data) > 1:
            for dict_ in data:
                timestamp = dt.datetime.fromisoformat(dict_["createdat"])
                if timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_dict = dict_

        return latest_dict


save_dictionary_to_json_file(dict_, file_path)

dict_ = read_latest_json_todict(file_path)
print(dict_)
