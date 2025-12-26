import streamlit as st
import random
import json
from pathlib import Path

st.set_page_config(
    page_title="Not So Dumb Charades",
    page_icon="🎬",
    layout="centered"
)

# Color scheme for categories
CATEGORY_COLORS = {
    "movie": {"bg": "#3498db", "name": "Movie"},      # Blue
    "dialogue": {"bg": "#e74c3c", "name": "Dialogue"}, # Red
    "song": {"bg": "#27ae60", "name": "Song"}          # Green
}

# Load data directly (no separate API needed)
@st.cache_data
def load_movies():
    db_path = Path(__file__).parent / "database" / "movies.json"
    with open(db_path, "r") as f:
        data = json.load(f)
    # Add category field and normalize industry
    for m in data["movies"]:
        m["category"] = "movie"
        m["display_text"] = m["title"]
        if m["industry"] == "hollywood":
            m["industry"] = "international"
    return data["movies"]

@st.cache_data
def load_songs():
    db_path = Path(__file__).parent / "database" / "songs.json"
    with open(db_path, "r") as f:
        data = json.load(f)
    # Add category field
    for s in data["songs"]:
        s["category"] = "song"
        s["display_text"] = s["title"]
    return data["songs"]

@st.cache_data
def load_dialogues():
    db_path = Path(__file__).parent / "database" / "dialogues.json"
    with open(db_path, "r") as f:
        data = json.load(f)
    # Add category field
    for d in data["dialogues"]:
        d["category"] = "dialogue"
        d["display_text"] = d["dialogue"]
    return data["dialogues"]

def get_all_items(category, movies, songs, dialogues):
    """Get items based on selected category"""
    if category == "Movies":
        return movies
    elif category == "Songs":
        return songs
    elif category == "Dialogues":
        return dialogues
    else:  # Mix
        return movies + songs + dialogues

def get_random_item(items, filters, exclude_ids):
    filtered = items

    # Filter by industry
    if filters.get("industry") and filters["industry"] != "I Don't Care":
        industry = filters["industry"].lower()
        filtered = [m for m in filtered if m["industry"] == industry]

    # Filter by difficulty
    if filters.get("difficulty"):
        difficulty = filters["difficulty"].lower()
        if difficulty == "easy":
            # Easy: Recent items with simple titles
            filtered = [m for m in filtered if m["year"] >= 2010 and m.get("title_complexity", "simple") == "simple"]
        else:
            # Difficult: Older items OR complex titles
            filtered = [m for m in filtered if m["year"] < 2010 or m.get("title_complexity", "simple") == "complex"]

    # Filter by decade
    if filters.get("decade") and filters["decade"] != "Any":
        decade = filters["decade"]
        filtered = [m for m in filtered if m["decade"] == decade]

    # Exclude already shown items (using category + id to make unique)
    if exclude_ids:
        filtered = [m for m in filtered if f"{m['category']}_{m['id']}" not in exclude_ids]

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
if "current_item" not in st.session_state:
    st.session_state.current_item = None
if "item_history" not in st.session_state:
    st.session_state.item_history = []
if "shown_ids" not in st.session_state:
    st.session_state.shown_ids = []
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# Load all data once
movies = load_movies()
songs = load_songs()
dialogues = load_dialogues()


def fetch_random_item():
    category = st.session_state.filters.get("category", "Mix")
    items = get_all_items(category, movies, songs, dialogues)
    return get_random_item(items, st.session_state.filters, st.session_state.shown_ids)


def start_game():
    st.session_state.game_started = True
    st.session_state.item_history = []
    st.session_state.shown_ids = []
    st.session_state.show_history = False
    item = fetch_random_item()
    if item:
        st.session_state.current_item = item
        st.session_state.item_history.append(item)
        st.session_state.shown_ids.append(f"{item['category']}_{item['id']}")


def next_item():
    item = fetch_random_item()
    if item:
        st.session_state.current_item = item
        st.session_state.item_history.append(item)
        st.session_state.shown_ids.append(f"{item['category']}_{item['id']}")
    else:
        st.warning("No more items available with the selected filters!")


def end_game():
    st.session_state.game_started = False
    st.session_state.current_item = None
    st.session_state.show_history = False


def toggle_history():
    st.session_state.show_history = not st.session_state.show_history


def get_item_details(item):
    """Get display details based on item category"""
    if item["category"] == "movie":
        return {
            "Year": item["year"],
            "Industry": item["industry"].title(),
            "Actors": ", ".join(item.get("actors", [])),
            "Description": item.get("description", "")
        }
    elif item["category"] == "song":
        return {
            "Year": item["year"],
            "Artist": item.get("artist", ""),
            "Industry": item["industry"].title()
        }
    else:  # dialogue
        return {
            "Year": item["year"],
            "Movie": item.get("movie", ""),
            "Industry": item["industry"].title()
        }


st.title("🎬 Not So Dumb Charades")
st.markdown("---")

if not st.session_state.game_started:
    st.subheader("Game Setup")

    # Category selection
    category = st.selectbox(
        "Select Category",
        ["Mix", "Movies", "Songs", "Dialogues"],
        help="Choose what to play with - or mix them all!"
    )

    col1, col2 = st.columns(2)

    with col1:
        industry = st.selectbox(
            "Select Industry",
            ["I Don't Care", "International", "Bollywood"],
            help="Choose content origin"
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
        "category": category,
        "industry": industry,
        "difficulty": difficulty,
        "decade": decade
    }

    st.markdown("---")

    # Show category legend
    st.markdown("**Color Legend:**")
    legend_cols = st.columns(3)
    with legend_cols[0]:
        st.markdown(f'<span style="background-color: {CATEGORY_COLORS["movie"]["bg"]}; color: white; padding: 5px 10px; border-radius: 5px;">🎬 Movie</span>', unsafe_allow_html=True)
    with legend_cols[1]:
        st.markdown(f'<span style="background-color: {CATEGORY_COLORS["dialogue"]["bg"]}; color: white; padding: 5px 10px; border-radius: 5px;">💬 Dialogue</span>', unsafe_allow_html=True)
    with legend_cols[2]:
        st.markdown(f'<span style="background-color: {CATEGORY_COLORS["song"]["bg"]}; color: white; padding: 5px 10px; border-radius: 5px;">🎵 Song</span>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🎮 Start Game", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    if st.session_state.show_history:
        st.subheader("📜 Game History")

        if st.session_state.item_history:
            for i, item in enumerate(st.session_state.item_history, 1):
                cat_info = CATEGORY_COLORS[item["category"]]
                with st.expander(f"{i}. [{cat_info['name']}] {item['display_text'][:50]}{'...' if len(item['display_text']) > 50 else ''} ({item['year']})"):
                    details = get_item_details(item)
                    for key, value in details.items():
                        if value:
                            st.write(f"**{key}:** {value}")
        else:
            st.info("No items shown yet!")

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
        item = st.session_state.current_item

        if item:
            cat_info = CATEGORY_COLORS[item["category"]]

            st.markdown(f"### Item #{len(st.session_state.item_history)}")

            # Category tag
            cat_emoji = "🎬" if item["category"] == "movie" else ("🎵" if item["category"] == "song" else "💬")
            st.markdown(
                f'<div style="text-align: center; margin-bottom: 10px;">'
                f'<span style="background-color: {cat_info["bg"]}; color: white; padding: 8px 20px; border-radius: 20px; font-weight: bold;">'
                f'{cat_emoji} {cat_info["name"].upper()}'
                f'</span></div>',
                unsafe_allow_html=True
            )

            # Main display with category-specific color
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {cat_info["bg"]} 0%, {cat_info["bg"]}cc 100%);
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                ">
                    <h1 style="color: white; font-size: 2rem; margin: 0; line-height: 1.4;">
                        {item['display_text']}
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("⏭️ Next", use_container_width=True, type="primary"):
                    next_item()
                    st.rerun()

            with col2:
                if st.button("📜 History", use_container_width=True):
                    toggle_history()
                    st.rerun()

            with col3:
                if st.button("🏁 End Game", use_container_width=True, type="secondary"):
                    end_game()
                    st.rerun()

            with st.expander("🔍 Reveal Details"):
                details = get_item_details(item)
                for key, value in details.items():
                    if value:
                        st.write(f"**{key}:** {value}")

        else:
            st.error("Failed to load item. Please try again.")
            if st.button("🔄 Retry", use_container_width=True):
                start_game()
                st.rerun()


st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Made for fun charades nights!</p>",
    unsafe_allow_html=True
)
