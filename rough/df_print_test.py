import pandas as pd

data = {"up": {"yes": {"a": [1, 2, 3],
                       "b": [1, 2, 3]},
               "no": {"a": [1, 2, 3],
                      "b": [1, 2, 3]}
               },
        "down": {"yes": {"a": [1, 2, 3],
                         "b": [1, 2, 3]},
                 "no": {"a": [1, 2, 3],
                        "b": [1, 2, 3]}
                 }
        }

df = pd.DataFrame.from_dict(data, orient="index")

print(df)
