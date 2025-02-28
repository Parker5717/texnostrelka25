import streamlit as st
import json
from sentence_transformers import SentenceTransformer, util
import torch
import os
import numpy as np
from datetime import datetime

# Загрузка базы фильмов
movies_file = r"C:\Users\CubeUser\PycharmProjects\TehnostrelkaProd\movies_with_tags_and_comments.json"
with open(movies_file, "r", encoding="utf-8") as file:
    movies = json.load(file)

# Загрузка модели (только один раз)
if "model" not in st.session_state:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    st.session_state.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)

# Загрузка или кеширование эмбеддингов
if "desc_embeddings" not in st.session_state:
    embedding_file = "movie_embeddings.npy"
    if os.path.exists(embedding_file):
        st.session_state.desc_embeddings = torch.tensor(np.load(embedding_file)).to(device)
    else:
        descriptions = [movie["description"] for movie in movies]
        st.session_state.desc_embeddings = st.session_state.model.encode(descriptions, convert_to_tensor=True)
        np.save(embedding_file, st.session_state.desc_embeddings.cpu().numpy())

# Функции поиска
def exact_search(query):
    query_lower = query.lower()
    return [
        movie for movie in movies
        if query_lower in movie["title"].lower() or any(query_lower in tag.lower() for tag in movie["tags"])
    ]


def semantic_search(query, top_n=10):
    query_embedding = st.session_state.model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, st.session_state.desc_embeddings)[0]
    top_indexes = similarities.argsort(descending=True)[:top_n]
    return [movies[int(i)] for i in top_indexes]

# UI Настройки
st.set_page_config(page_title="Поиск фильмов", layout="wide")
st.markdown("""
    <style>
    .movie-container {
        position: relative;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .movie-poster img {
        height: 250px !important;
        width: 180px !important;
        object-fit: cover;
        border-radius: 10px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .movie-title {
        font-size: 10px;
        text-align: center;
        margin-top: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .stButton > button {
        display: block;
        margin: 10px auto 0 auto;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
    }
    a {
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# Поиск фильма
st.title("🎬 Поиск фильмов")
search_query = st.text_input("🔍 Введите название фильма или тег", "").strip()

filtered_movies = exact_search(search_query)
if not filtered_movies and search_query:
    filtered_movies = semantic_search(search_query)

# Отображение фильма при выборе
if "selected_movie" in st.session_state:
    movie = st.session_state.selected_movie
    st.header(f"🎬 {movie['title']} ({movie['year']})")
    st.image(movie["poster"], width=300)
    st.write(f"**Рейтинг:** {movie['rating']}")
    st.write(f"**Голоса:** {movie['votes']}")
    st.write(f"**Жанры:** {', '.join(movie['genres'])}")
    st.write(f"**Страны:** {', '.join(movie['countries'])}")
    st.write(f"**Описание:** {movie['description']}")
    st.write(f"**Теги:** {', '.join(movie['tags'])}")

    # Комментарии
    st.subheader("💬 Комментарии")
    if "comments" not in movie:
        movie["comments"] = []

    if movie["comments"]:
        for comment in sorted(movie["comments"], key=lambda x: x["timestamp"], reverse=True):
            st.write(f"🕒 {comment['timestamp']}")
            st.info(comment["text"])
    else:
        st.write("Пока нет комментариев. Будьте первым!")

    # Форма добавления комментариев
    st.subheader("📝 Оставить комментарий")
    user_comment = st.text_area("Напишите ваш отзыв...", key="comment_input")

    if st.button("💬 Отправить"):
        if user_comment.strip():
            comment_data = {
                "text": user_comment.strip(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            movie["comments"].append(comment_data)

            # Сохраняем комментарий в JSON
            with open(movies_file, "w", encoding="utf-8") as file:
                json.dump(movies, file, ensure_ascii=False, indent=4)

            st.success("✅ Комментарий добавлен!")
            st.rerun()
        else:
            st.warning("⚠️ Комментарий не может быть пустым!")

    if st.button("🔙 Назад к списку фильмов"):
        del st.session_state.selected_movie
        st.rerun()
    st.stop()

# Отображение списка фильмов
num_columns = 7
cols = st.columns(num_columns)
for index, movie in enumerate(filtered_movies):
    with cols[index % num_columns]:
        with st.container():
            st.markdown(f"<div class='movie-container'>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-poster'><img src='{movie['poster']}'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-title'>{movie['title']} ({movie['year']})</div>", unsafe_allow_html=True)
            if st.button("Подробнее", key=movie['id']):
                st.session_state.selected_movie = movie
                st.rerun()
            st.markdown(f"</div>", unsafe_allow_html=True)
