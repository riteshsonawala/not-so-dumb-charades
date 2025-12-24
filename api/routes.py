from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional

from api.models import Movie, Industry, Difficulty, Decade
from database.db import db

router = APIRouter(prefix="/api", tags=["movies"])


@router.get("/health")
def health_check():
    return {"status": "healthy", "movie_count": len(db.get_all_movies())}


@router.get("/movies", response_model=List[Movie])
def get_movies(
    industry: Optional[Industry] = Query(None, description="Filter by industry"),
    difficulty: Optional[Difficulty] = Query(None, description="Filter by difficulty"),
    decade: Optional[Decade] = Query(None, description="Filter by decade")
):
    return db.filter_movies(industry, difficulty, decade)


@router.get("/movies/random", response_model=Movie)
def get_random_movie(
    industry: Optional[Industry] = Query(None, description="Filter by industry"),
    difficulty: Optional[Difficulty] = Query(None, description="Filter by difficulty"),
    decade: Optional[Decade] = Query(None, description="Filter by decade"),
    exclude: Optional[str] = Query(None, description="Comma-separated IDs to exclude")
):
    exclude_ids = None
    if exclude:
        try:
            exclude_ids = [int(x.strip()) for x in exclude.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid exclude IDs format")

    movie = db.get_random_movie(industry, difficulty, decade, exclude_ids)
    if not movie:
        raise HTTPException(status_code=404, detail="No movies found matching criteria")
    return movie


@router.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    movie = db.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie