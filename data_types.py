from typing import TypedDict


class Movie(TypedDict):
    name: str
    year: int


movie: Movie = {"name": "Blade Runner", "year": 1982}

movie["year"] = "s"

word: bool = movie.year
