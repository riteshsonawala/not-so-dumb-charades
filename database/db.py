import json
import random
from pathlib import Path
from typing import List, Optional

from api.models import Movie, Industry, Difficulty, Decade, TitleComplexity


class MovieDatabase:
    def __init__(self):
        self._movies: List[Movie] = []
        self._load_movies()

    def _load_movies(self):
        db_path = Path(__file__).parent / "movies.json"
        with open(db_path, "r") as f:
            data = json.load(f)

        self._movies = [
            Movie(
                id=m["id"],
                title=m["title"],
                year=m["year"],
                industry=Industry(m["industry"]),
                description=m["description"],
                actors=m["actors"],
                decade=Decade(m["decade"]),
                title_complexity=TitleComplexity(m.get("title_complexity", "simple"))
            )
            for m in data["movies"]
        ]

    def get_all_movies(self) -> List[Movie]:
        return self._movies

    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        for movie in self._movies:
            if movie.id == movie_id:
                return movie
        return None

    def filter_movies(
        self,
        industry: Optional[Industry] = None,
        difficulty: Optional[Difficulty] = None,
        decade: Optional[Decade] = None
    ) -> List[Movie]:
        filtered = self._movies

        if industry:
            filtered = [m for m in filtered if m.industry == industry]

        if difficulty:
            if difficulty == Difficulty.EASY:
                # Easy: Recent movies with simple titles
                filtered = [m for m in filtered if m.year >= 2010 and m.title_complexity == TitleComplexity.SIMPLE]
            else:
                # Difficult: Older movies OR complex titles (any year)
                filtered = [m for m in filtered if m.year < 2010 or m.title_complexity == TitleComplexity.COMPLEX]

        if decade:
            filtered = [m for m in filtered if m.decade == decade]

        return filtered

    def get_random_movie(
        self,
        industry: Optional[Industry] = None,
        difficulty: Optional[Difficulty] = None,
        decade: Optional[Decade] = None,
        exclude_ids: Optional[List[int]] = None
    ) -> Optional[Movie]:
        filtered = self.filter_movies(industry, difficulty, decade)

        if exclude_ids:
            filtered = [m for m in filtered if m.id not in exclude_ids]

        if not filtered:
            return None

        # When difficulty is "difficult", give 3x weight to complex titles
        if difficulty == Difficulty.DIFFICULT:
            weights = [3 if m.title_complexity == TitleComplexity.COMPLEX else 1 for m in filtered]
            return random.choices(filtered, weights=weights, k=1)[0]

        return random.choice(filtered)


db = MovieDatabase()