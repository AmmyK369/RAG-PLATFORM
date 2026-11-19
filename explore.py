import json

with open("data/squad/dev-v2.0.json", encoding="utf-8") as f:
    squad=json.load(f)
    
articles = squad["data"]
print("Number of articles:", len(articles))


first=articles[4]
print("Title:", first["title"])
print("Paragraphs:", len(first["paragraphs"]))
print("First paragraph:", first["paragraphs"][0]["context"][:300])
print("A question:", first["paragraphs"][0]["qas"][0])