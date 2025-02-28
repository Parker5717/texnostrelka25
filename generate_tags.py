import os
import time
from mistralai import Mistral
import json

api_key = 'ySCnKUIRLsNjp2ZVx1JCajSivQBP9Znb'
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

def generate_tags(description):
    prompt = f"""
    Прочитай описание фильма и предложи от 5 до 10 тегов, которые лучше всего его описывают.
    Используй темы, жанры, атмосферу и ключевые особенности фильма.
    Теги должны быть в форме списка (например: ["дружба", "приключения", "юмор"]).
    Описание фильма: {description}
    Cписок тегов:
    """

    model = "mistral-small-latest"
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
    return chat_response.choices[0].message.content


with open("movies.json", "r", encoding="utf-8") as file:
    movies = json.load(file)

for movie in movies:
    movie["tags"] = generate_tags(movie["description"])
    movie["tags"] = json.loads(movie["tags"])
    time.sleep(4)
    print(movie["tags"])

with open("movies_with_tags.json", "w", encoding="utf-8") as file:
    json.dump(movies, file, ensure_ascii=False, indent=4)

print('ВСЕ ГОТОВО!')


