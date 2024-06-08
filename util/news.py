"""This module defines the news recommendaion related functions for OpenAI."""

import os.path
from zipfile import ZipFile

import polars as pl
import requests

NEWS_RECS_BY_CATEGORY = {
    "type": "function",
    "function": {
        "name": "get_random_news_by_category",
        "description": "Returns the provided number of news article headlines \
from a given category. This function requires at least one category to work.",
        "parameters": {
            "type": "object",
            "properties": {
                "number": { "type": "number"},
                "category": {
                    "type": "string",
                    "enum": [
                        'sports',
                        'travel',
                        'health',
                        'news',
                        'movies',
                        'tv',
                        'entertainment',
                        'video',
                        'lifestyle',
                        'finance',
                        'kids',
                        'weather',
                        'northamerica',
                        'autos',
                        'foodanddrink',
                        'music'
                    ]
                }
            },
            "required": ["number", "category"],
        },
    },
}


def download_news_articles() -> None:
    """ Downloads and extracts the news articles dataset. """

    url = "https://mind201910small.blob.core.windows.net/release/MINDsmall_dev.zip"
    response = requests.get(url, allow_redirects=True)

    with open("data/MINDsmall_dev.zip", 'wb') as file:
        file.write(response.content)

    with ZipFile("data/MINDsmall_dev.zip", "r") as zip_file:
        zip_file.extractall("data/MINDsmall_dev")


def load_news_articles() -> pl.LazyFrame:
    """ Loads the news articles and returns them in a polars Lazy Frame.

    Returns:
        pl.LazyFrame: _description_
    """

    if not os.path.isfile("data/MINDsmall_dev/news.tsv"):
        download_news_articles()

    news_lf = pl.scan_csv("data/MINDsmall_dev/news.tsv",
                       separator="\t",
                       has_header=False,
                       schema={"news_id" : pl.datatypes.String,
                               "category" : pl.datatypes.String,
                               "subcategory" : pl.datatypes.String,
                               "title" : pl.datatypes.String,
                               "abstract" : pl.datatypes.String,
                               "url" : pl.datatypes.String,
                               "title_entities" : pl.datatypes.String,
                               "abstract_entities" : pl.datatypes.String},
                        ignore_errors=True)

    news_lf = news_lf.with_columns(
        pl.col("abstract").fill_null("No abstract")
    )
    return news_lf


def get_random_news_by_category(number: int, category: str) -> str:
    """ Retrieves random news articles by the given category, and returns
        their title.

    Args:
        number (int): the number of news articles by category to return.
        category (str): the category of news articles to return.

    Returns:
        str: the title and ID of each news article.
    """
    news_lf = load_news_articles()
    news_articles = []

    news_by_cat = news_lf.filter(
        pl.col("category") == category
    ).select(
        pl.col("title"),
        pl.col("news_id")
    ).collect().sample(n=number).rows()
    for article in news_by_cat:
        news_articles.append("Title: \"" + article[0] + "\", \
ID: \"" + article[1] + "\"")

    return ". ".join(news_articles)


NEWS_ARTICLE_ABSTRACT_BY_TITLE = {
    "type": "function",
    "function": {
        "name": "get_article_abstract_by_title",
        "description": "Retrieves the news article's abstract with the provide\
d title. This function requires at least one title to function correctly.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": { "type": "string"},
            },
            "required": ["title"],
        },
    },
}


def get_article_abstract_by_title(title: str) -> str:
    """ Retrieves a news article's abstract by the given title.

    Args:
        title (str): the title of the article to return.

    Returns:
        str: the news article's abstract.
    """
    news_lf = load_news_articles()
    abstract = news_lf.filter(
        pl.col("title") == title
    ).select(
        pl.col("abstract")
    ).collect()

    if len(abstract.to_series().to_list()) > 0:
        return abstract.to_series().to_list()[0]
    else:
        return "Abstract not found."


NEWS_ARTICLE_ABSTRACT_BY_ID = {
    "type": "function",
    "function": {
        "name": "get_article_abstract_by_id",
        "description": "Retrieves the news article's abstract with the provide\
d id. This function requires at least one news_id to function correctly.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": { "type": "string"},
            },
            "required": ["id"],
        },
    },
}


def get_article_abstract_by_id(id: str) -> str:
    """ Retrieves a news article's abstract by the id.

    Args:
        id (str): the id of the article to return.

    Returns:
        str: the news article's abstract.
    """
    news_lf = load_news_articles()
    abstract = news_lf.filter(
        pl.col("news_id") == id
    ).select(
        pl.col("abstract")
    ).collect()

    if len(abstract.to_series().to_list()) > 0:
        return abstract.to_series().to_list()[0]
    else:
        return "Abstract not found."


if __name__ == "__main__":
    print(get_article_abstract_by_title("Raptors' Fred VanVleet injured after \
collision with cameraman"))
    print(get_random_news_by_category(3, "sports"))
