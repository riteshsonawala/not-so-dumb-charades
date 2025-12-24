import streamlit as st
import random
import json
from pathlib import Path

st.set_page_config(
    page_title="Not So Dumb Charades",
    page_icon="🎬",
    layout="centered"
)

# Load movies directly (no separate API needed)
@st.cache_data
def load_movies():
    db_path = Path(__file__).parent / "database" / "movies.json"
    with open(db_path, "r") as f:
        data = json.load(f)
    return data["movies"]

def get_random_movie(movies, filters, exclude_ids):
    filtered = movies

    # Filter by industry
    if filters.get("industry") and filters["industry"] != "I Don't Care":
        industry = filters["industry"].lower()
        filtered = [m for m in filtered if m["industry"] == industry]

    # Filter by difficulty
    if filters.get("difficulty"):
        difficulty = filters["difficulty"].lower()
        if difficulty == "easy":
            # Easy: Recent movies with simple titles
            filtered = [m for m in filtered if m["year"] >= 2010 and m.get("title_complexity", "simple") == "simple"]
        else:
            # Difficult: Older movies OR complex titles
            filtered = [m for m in filtered if m["year"] < 2010 or m.get("title_complexity", "simple") == "complex"]

    # Filter by decade
    if filters.get("decade") and filters["decade"] != "Any":
        decade = filters["decade"]
        filtered = [m for m in filtered if m["decade"] == decade]

    # Exclude already shown movies
    if exclude_ids:
        filtered = [m for m in filtered if m["id"] not in exclude_ids]

    if not filtered:
        return None

    # When difficulty is "difficult", give 3x weight to complex titles
    if filters.get("difficulty", "").lower() == "difficult":
        weights = [3 if m.get("title_complexity", "simple") == "complex" else 1 for m in filtered]
        return random.choices(filtered, weights=weights, k=1)[0]

    return random.choice(filtered)


# Initialize session state
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

# Load movies once
movies = load_movies()


def fetch_random_movie():
    return get_random_movie(movies, st.session_state.filters, st.session_state.shown_ids)


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
            help="Easy = Recent simple titles, Difficult = Older or complex titles"
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