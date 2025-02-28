import requests
import time
import json

API_KEY = 'VQ8Z2SX-D65MRZY-HQQ634Z-1QHAKWT'
url = 'https://api.kinopoisk.dev/v1.4/movie'
headers = {'accept': 'application/json', 'X-API-KEY': API_KEY}

limit = 2000
films = []
page = 1
min_votes = 10000

while len(films) < limit:
    params = {
        "field": "rating.kp",
        "search": "7-10",
        "sortField": "rating.kp",
        "sortType": "-1",
        "limit": 10,
        "page": page
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        movies = data.get("docs", [])

        for movie in movies:
            title = movie.get("name") or movie.get("alternativeName") or movie.get("enName") or "Без названия"
            votes = movie.get("votes", {}).get("kp", 0)
            poster = movie.get("poster", {}).get("url")
            description = movie.get("description")
            if votes >= min_votes and poster and description:
                films.append({
                    "id": movie["id"],
                    "title": title,
                    "rating": movie.get("rating", {}).get("kp", "Нет рейтинга"),
                    "votes": votes,
                    "year": movie.get("year", "Неизвестен"),
                    "description": description,
                    "genres": [g["name"] for g in movie.get("genres", [])],  # Жанры
                    "countries": [c["name"] for c in movie.get("countries", [])],  # Страны
                    "duration": movie.get("movieLength", "Неизвестно"),  # Длительность
                    "poster": poster,  # Постер
                    "tags": movie.get("tags", []) or ["Нет тегов"],  # Теги
                    "slogan": movie.get("slogan", "Нет слогана")  # Слоган
                })

                print(f"Добавлен фильм: {title}")

                if len(films) >= limit:
                    break

    else:
        print(f"Ошибка: {response.status_code}")
        break

    page += 1
    time.sleep(0.3)


with open("movies.json", "w", encoding="utf-8") as file:
    json.dump(films, file, ensure_ascii=False, indent=4)

print("Файл movies.json сохранён!")
