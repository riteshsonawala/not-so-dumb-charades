from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class Industry(str, Enum):
    HOLLYWOOD = "hollywood"
    BOLLYWOOD = "bollywood"


class Difficulty(str, Enum):
    EASY = "easy"
    DIFFICULT = "difficult"


class TitleComplexity(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"


class Decade(str, Enum):
    SIXTIES = "60s"
    SEVENTIES = "70s"
    EIGHTIES = "80s"
    NINETIES = "90s"
    TWO_THOUSANDS = "2000s"
    TWENTY_TENS = "2010s"
    TWENTY_TWENTIES = "2020s"


class Movie(BaseModel):
    id: int
    title: str
    year: int
    industry: Industry
    description: str
    actors: List[str]
    decade: Decade
    title_complexity: TitleComplexity = TitleComplexity.SIMPLE


class MovieFilters(BaseModel):
    industry: Optional[Industry] = None
    difficulty: Optional[Difficulty] = None
    decade: Optional[Decade] = None


class GameSession(BaseModel):
    movies_shown: List[Movie] = []
    current_movie: Optional[Movie] = None
    filters: MovieFilters = MovieFilters()