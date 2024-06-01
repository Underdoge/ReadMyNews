"""This module defines the movie recommendaion related functions for OpenAI."""

import requests
from bs4 import BeautifulSoup

HEADERS = {
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK\
it/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}

MOVIE_RECS_BY_GENRE = {
    "type": "function",
    "function": {
        "name": "get_movie_recommendations_by_genre",
        "description": "Recommend 3 movies from the given genre. This function\
 requires at least one genre to function correctly.",
        "parameters": {
            "type": "object",
            "properties": {
                "num": { "type": "number"},
                "genres": {
                    "type": "string",
                    "enum": [
                        "Action",
                        "Adventure",
                        "Animation",
                        "Biography",
                        "Comedy",
                        "Crime",
                        "Documentary",
                        "Drama",
                        "Family",
                        "Fantasy",
                        "Film-Noir",
                        "History",
                        "Horror",
                        "Music",
                        "Musical",
                        "Mystery",
                        "Romance",
                        "Sci-Fi",
                        "Short",
                        "Sport",
                        "Thriller",
                        "War",
                        "Western"
                    ]
                }
            },
            "required": ["num", "genres"],
        },
    },
}

def get_movie_recommendations_by_genre(num: int, genres: str) -> str:
    """ Retrieves movies based on genre from IMDB and returns their title,
        description, rating and vote count, all in a single line.

    Args:
        num (int): the number of movies to return
        genres (str): the genres to include in the search

    Returns:
        str: the title, description, rating and vote count of each movie
    """
    url = 'https://www.imdb.com/search/title/?genres=' + genres + '&title_type\
=feature'
    print("IMDB URL:", url)
    response = requests.get(url, headers=HEADERS)  # noqa: S113
    soup = BeautifulSoup(response.text, "html.parser")
    titles = [a.text[3:] for a in soup.select(
            'h3.ipc-title__text')]
    desc = [a.text for a in soup.select(
            'div.ipc-html-content-inner-div')]
    rating = [a.text[:3] for a in soup.select(
            'span.ipc-rating-star--base') if a.text != "Rate"]
    votes = [a.text[5:-1] for a in soup.select(
            'span.ipc-rating-star--base') if a.text != "Rate"]
    title_i = 0
    title_and_info = []
    while title_i < num:
        if rating[title_i] == '':
            title_and_info.append("Title: \"" + titles[title_i] + "\
\", description: \"" + desc[title_i] + "\", rating not available yet")
        else:
            title_and_info.append("Title: \"" + titles[title_i] + "\
\", description: \"" + desc[title_i] + "\
\", rating: " + rating[title_i] + "\
, votes: " + votes[title_i])
        title_i += 1
    return ". ".join(title_and_info[:num])

if __name__ == "__main__":
    print(get_movie_recommendations_by_genre(2, "Horror"))
