import json

import pandas as pd

json_path = "/Users/anirudh/Documents/lunar/json_files/strategy_20231004.json"
with open(json_path,"r") as file:
    json_data = json.load(file)
print(json_data)
df = pd.DataFrame(json_data)
print(df)
print(df.columns)