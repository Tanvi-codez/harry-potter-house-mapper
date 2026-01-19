import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")
nltk.download('punkt_tab')

nltk.download("stopwords")

stop_words = set(stopwords.words("english"))
model = SentenceTransformer("all-MiniLM-L6-v2")

house_files = {
    "Gryffindor": "Gryffindor.txt",
    "Hufflepuff": "HUFFLEPUFF.txt",
    "Ravenclaw": "ravenclaw.txt",
    "Slytherin": "Slytherin.txt"
}

def clean_text(text):
    tokens = word_tokenize(text.lower())
    return [w for w in tokens if w.isalnum() and w not in stop_words]

def map_users_to_houses(chat_path="_chat.txt"):
    with open(chat_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    rows = []
    for line in lines:
        if " - " in line and ": " in line:
            try:
                part = line.split(" - ")[1]
                name, msg = part.split(": ", 1)
                rows.append([name.strip(), msg.strip()])
            except:
                pass

    df = pd.DataFrame(rows, columns=["User", "Message"])
    df["tokens"] = df["Message"].apply(clean_text)
    


    grouped = df.groupby("User")["tokens"].sum()
    user_keywords = grouped.to_dict()

    # Encode house texts
    house_vectors = {}
    for house, file in house_files.items():
        with open(file, "r", encoding="utf-8") as f:
            text = " ".join(clean_text(f.read()))
        house_vectors[house] = model.encode([text])[0]

    results = {}

    for user, words in user_keywords.items():
        combined = " ".join(words)
        user_vec = model.encode([combined])[0]

        scores = {}
        for house, h_vec in house_vectors.items():
            scores[house] = float(
                cosine_similarity([user_vec], [h_vec])[0][0]
            )

        final_house = max(scores, key=scores.get)

        results[user] = {
            "scores": {h: round(s, 4) for h, s in scores.items()},
            "assigned_house": final_house
        }

    return results
