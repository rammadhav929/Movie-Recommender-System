import pickle
import streamlit as st
import requests
from youtube_search import YoutubeSearch
import base64


def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = (
        """
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    """
        % bin_str
    )
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background("model/img.png")


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    if "poster_path" in data:
        poster_path = data["poster_path"]
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image+Available"


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(
            movies.iloc[i[0]].title + " (" + year[i[0]] + ")"
        )

    return recommended_movie_names, recommended_movie_posters


def get_youtube_url(search_query):
    results = YoutubeSearch(search_query, max_results=1).to_dict()
    if results:
        video_id = results[0]["id"]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        return youtube_url
    return None


# Styling for titles and other elements
st.markdown(
    """
    <style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
    }
    .movie-title{
     font-size: 15px;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
    }
   
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">Movie Recommender System</div>', unsafe_allow_html=True
)

movies = pickle.load(open("model/movie_list.pkl", "rb"))
similarity = pickle.load(open("model/similarity.pkl", "rb"))
year = pickle.load(open("model/years.pkl", "rb"))

movie_list = movies["title"].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button("Show Recommendation"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    st.session_state.recommended_movies = recommended_movie_names
    st.session_state.recommended_posters = recommended_movie_posters

# Display recommendations if they exist
if (
    "recommended_movies" in st.session_state
    and "recommended_posters" in st.session_state
):
    st.markdown('<div class="sub-title">Recommendations</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f'<div class="movie-title">{st.session_state.recommended_movies[0]}</div>',
            unsafe_allow_html=True,
        )
        st.image(st.session_state.recommended_posters[0])
    with col2:
        st.markdown(
            f'<div class="movie-title">{st.session_state.recommended_movies[1]}</div>',
            unsafe_allow_html=True,
        )
        st.image(st.session_state.recommended_posters[1])
    with col3:
        st.markdown(
            f'<div class="movie-title">{st.session_state.recommended_movies[2]}</div>',
            unsafe_allow_html=True,
        )
        st.image(st.session_state.recommended_posters[2])
    with col4:
        st.markdown(
            f'<div class="movie-title">{st.session_state.recommended_movies[3]}</div>',
            unsafe_allow_html=True,
        )
        st.image(st.session_state.recommended_posters[3])
    with col5:
        st.markdown(
            f'<div class="movie-title">{st.session_state.recommended_movies[4]}</div>',
            unsafe_allow_html=True,
        )
        st.image(st.session_state.recommended_posters[4])


st.markdown('<div class="sub-title">Watch Trailer</div>', unsafe_allow_html=True)
with st.form("trailer_form"):
    name = st.text_input("Type Movie Name")
    submit = st.form_submit_button("Play Trailer")
    if submit and name:
        video_url = get_youtube_url(name + " trailer")
        st.video(video_url, format="video/mp4", start_time=0)
