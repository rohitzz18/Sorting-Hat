import pandas as pd
import re
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- PARSER ----------
pattern = re.compile(
    r'(\d{1,2}/\d{1,2}/\d{2,4}),\s'
    r'(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm))\s-\s'
    r'([^:]+):(.*)'
)

def parse_whatsapp_chat(file_path):
    messages = []
    current = None

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            match = pattern.match(line)

            if match:
                if current:
                    messages.append(current)

                current = {
                    "sender": match.group(3).strip(),
                    "message": match.group(4).strip()
                }
            else:
                if current and line.strip():
                    current["message"] += " " + line.strip()

        if current:
            messages.append(current)

    return pd.DataFrame(messages)

# ---------- LOAD + CLEAN ----------
df = parse_whatsapp_chat("hogwarts_chat.txt")

media_placeholders = {
    "<Media omitted>", "image omitted", "video omitted",
    "audio omitted", "sticker omitted", "gif omitted"
}
df = df[~df["message"].isin(media_placeholders)]
df = df[df["message"].str.strip() != ""]

system_keywords = (
    "joined|left|added|removed|changed|created group|"
    "messages are end-to-end|group icon|security code"
)
df = df[~df["sender"].str.contains(system_keywords, case=False, na=False)]

# ---------- AGGREGATE ----------
combined = (
    df.groupby("sender")["message"]
      .apply(lambda x: " ".join(x))
      .reset_index()
)

# ---------- HOUSE PROFILES ----------
house_profiles = {
    "Gryffindor": """
    Stand up against injustice,Brave,chill people,don't get very tensed too quickly, bold, confident, action-oriented, fearless in uncertainty,Excellent Planner,
    Speaks with conviction and emotional strength,Sacrifice, Can sacrifice themselves for greater good, can even die for loving ones,
    Often pushes others to act instead of waiting, portrays heroism, leadership,
    Expresses strong opinions and stands by them,“Sometimes doing the right thing is more important than thinking about the risk.”,
    Believes that courage matters more than comfort,Courage isn’t the absence of fear—it’s choosing to act despite it,
    Willing to take responsibility even when the outcome is risky,
    Uses energetic, motivating,Bold, confident, outspoken, fearless, direct, takes initiative,
    expresses strong opinions, energetic and courageous language
    """,

    "Ravenclaw": """
    Strange sometimes, People think we are strange because we ask questions they never think to ask, Studying all day,Facts,Figures,Clever,Analytical, logical, knowledge-oriented, structured thinking,Book lovers,study a lot, toppers,
    problem solving, thoughtful explanations, intellectual tone,
    Analytical, logical, thoughtful, knowledge-oriented, reflective,
    Prefers reasoning before acting,
    Breaks problems into smaller logical steps,
    Asks questions to gain deeper understanding,
    Values accuracy, clarity, and well-supported arguments,
    Speaks in a calm, structured, and intellectual tone,
    Believes wisdom comes from careful thought and learning.
    """,

    "Hufflepuff": """
    Supportive, loyal, friendly, empathetic, cooperative,
    encouraging language, emotional support, kindness,
    Supportive, loyal, empathetic, cooperative, patient.
    Prioritizes people and relationships over outcomes.
    Uses encouraging and reassuring language.
    Often expresses concern for others' well-being.
    Believes teamwork and fairness lead to success.
    Communicates warmth, kindness, and emotional understanding.
    Values trust, dedication, and mutual support.
    """,
    "Slytherin": """

    Believes in Topmost position nothing else,Strategic, persuasive, competitive, devilish, can do anything for power, selfish,
    clever wording, tactical thinking, influence-driven language,
    self obsessed,Bully others,Dark magic believers, dicriminate between pure and impure races, villains,
    Thinks several steps ahead before acting,cunning like a fox,sly,
    Uses language to influence outcomes effectively,
    Focuses on efficiency and advantage,
    Evaluates risks and opportunities carefully,
    Communicates with precision and controlled confidence,
    Believes success comes from planning and intelligent positioning.
    """
}

# ---------- EMBEDDINGS ----------
model = SentenceTransformer("all-MiniLM-L6-v2")

house_names = list(house_profiles.keys())
house_embeddings = model.encode(list(house_profiles.values()))

user_embeddings = model.encode(combined["message"].tolist())

# ---------- SIMILARITY ----------
similarity = cosine_similarity(user_embeddings, house_embeddings)

top2 = np.argsort(similarity, axis=1)[:, -2:][:, ::-1]

# ---------- FINAL JSON ----------
output = {}

for idx, user in enumerate(combined["sender"]):
    scores = similarity[idx]
    output[user] = {
        "primary_house": house_names[top2[idx][0]],
        "secondary_house": house_names[top2[idx][1]],
        "scores": {
            house_names[i]: float(scores[i]) for i in range(len(house_names))
        }
    }

with open("character_user_mapping.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ character_user_mapping.json generated")