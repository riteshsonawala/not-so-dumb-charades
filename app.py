import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Not So Dumb Charades",
    page_icon="🎬",
    layout="centered"
)

if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "current_movie" not in st.session_state:
    st.session_state.current_movie = None
if "movie_history" not in st.session_state:
    st.session_state.movie_history = []
if "shown_ids" not in st.session_state:
    st.session_state.shown_ids = []
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "show_history" not in st.session_state:
    st.session_state.show_history = False


def fetch_random_movie():
    params = {}
    filters = st.session_state.filters

    if filters.get("industry") and filters["industry"] != "I Don't Care":
        params["industry"] = filters["industry"].lower()

    if filters.get("difficulty"):
        params["difficulty"] = filters["difficulty"].lower()

    if filters.get("decade") and filters["decade"] != "Any":
        params["decade"] = filters["decade"]

    if st.session_state.shown_ids:
        params["exclude"] = ",".join(map(str, st.session_state.shown_ids))

    try:
        response = requests.get(f"{API_URL}/api/movies/random", params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
    except requests.exceptions.RequestException:
        st.error("Could not connect to API. Make sure the backend is running.")
        return None


def start_game():
    st.session_state.game_started = True
    st.session_state.movie_history = []
    st.session_state.shown_ids = []
    st.session_state.show_history = False
    movie = fetch_random_movie()
    if movie:
        st.session_state.current_movie = movie
        st.session_state.movie_history.append(movie)
        st.session_state.shown_ids.append(movie["id"])


def next_movie():
    movie = fetch_random_movie()
    if movie:
        st.session_state.current_movie = movie
        st.session_state.movie_history.append(movie)
        st.session_state.shown_ids.append(movie["id"])
    else:
        st.warning("No more movies available with the selected filters!")


def end_game():
    st.session_state.game_started = False
    st.session_state.current_movie = None
    st.session_state.show_history = False


def toggle_history():
    st.session_state.show_history = not st.session_state.show_history


st.title("🎬 Not So Dumb Charades")
st.markdown("---")

if not st.session_state.game_started:
    st.subheader("Game Setup")

    col1, col2 = st.columns(2)

    with col1:
        industry = st.selectbox(
            "Select Industry",
            ["I Don't Care", "Hollywood", "Bollywood"],
            help="Choose movie industry"
        )

        difficulty = st.selectbox(
            "Select Difficulty",
            ["Easy", "Difficult"],
            help="Easy = 2010-2024, Difficult = 1960-2009"
        )

    with col2:
        decade = st.selectbox(
            "Select Decade",
            ["Any", "60s", "70s", "80s", "90s", "2000s", "2010s", "2020s"],
            help="Filter by specific decade"
        )

    st.session_state.filters = {
        "industry": industry,
        "difficulty": difficulty,
        "decade": decade
    }

    st.markdown("---")

    if st.button("🎮 Start Game", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    if st.session_state.show_history:
        st.subheader("📜 Game History")

        if st.session_state.movie_history:
            for i, movie in enumerate(st.session_state.movie_history, 1):
                with st.expander(f"{i}. {movie['title']} ({movie['year']})"):
                    st.write(f"**Industry:** {movie['industry'].title()}")
                    st.write(f"**Actors:** {', '.join(movie['actors'])}")
                    st.write(f"**Description:** {movie['description']}")
        else:
            st.info("No movies shown yet!")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Game", use_container_width=True):
                toggle_history()
                st.rerun()
        with col2:
            if st.button("🏁 End Game", use_container_width=True, type="secondary"):
                end_game()
                st.rerun()

    else:
        movie = st.session_state.current_movie

        if movie:
            st.markdown(f"### Movie #{len(st.session_state.movie_history)}")

            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                ">
                    <h1 style="color: white; font-size: 2.5rem; margin: 0;">
                        {movie['title']}
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("⏭️ Next Movie", use_container_width=True, type="primary"):
                    next_movie()
                    st.rerun()

            with col2:
                if st.button("📜 History", use_container_width=True):
                    toggle_history()
                    st.rerun()

            with col3:
                if st.button("🏁 End Game", use_container_width=True, type="secondary"):
                    end_game()
                    st.rerun()

            with st.expander("🔍 Reveal Movie Details"):
                st.write(f"**Year:** {movie['year']}")
                st.write(f"**Industry:** {movie['industry'].title()}")
                st.write(f"**Actors:** {', '.join(movie['actors'])}")
                st.write(f"**Description:** {movie['description']}")

        else:
            st.error("Failed to load movie. Please try again.")
            if st.button("🔄 Retry", use_container_width=True):
                start_game()
                st.rerun()


st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Made for fun charades nights!</p>",
    unsafe_allow_html=True
)