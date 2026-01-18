import json
import numpy as np

mapping = {}

for i, row in enumerate(similarity_matrix):
    user = user_names[i]
    scores = row.tolist()
    house = house_names[np.argmax(row)]

    mapping[user] = {
        "house": house,
        "scores": scores
    }

with open("character_user_mapping.json", "w") as f:
    json.dump(mapping, f, indent=2)