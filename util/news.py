"""This module defines the news recommendaion related functions for OpenAI."""

import os.path
from zipfile import ZipFile

import polars as pl
import requests
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

from util.language import translate_text


def download_news_articles() -> None:
    """ Downloads and extracts the news articles dataset. """

    url = "https://mind201910small.blob.core.windows.net/release/MINDsmall_dev.zip"
    response = requests.get(url, allow_redirects=True, timeout=60)

    with open("data/MINDsmall_dev.zip", 'wb') as file:
        file.write(response.content)

    with ZipFile("data/MINDsmall_dev.zip", "r") as zip_file:
        zip_file.extractall("data/MINDsmall_dev")


def load_news_articles() -> pl.LazyFrame:
    """ Loads the news articles and returns them in a polars Lazy Frame.

    Returns:
        LazyFrame: a polars Lazy Frame with the news articles.
    """

    if not os.path.isfile("data/MINDsmall_dev/news.tsv"):
        download_news_articles()

    news_lf = pl.read_csv("data/MINDsmall_dev/news.tsv",
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


def load_news_article_engagement() -> pl.LazyFrame:
    """ Loads the article engagements and returns them in a polars Lazy Frame.

    Returns:
        LazyFrame: a polars Lazy Frame with the news article engagements.
    """

    if not os.path.isfile("data/MINDsmall_dev/behaviors.tsv"):
        download_news_articles()

    behaviors_lf = pl.read_csv("data/MINDsmall_dev/behaviors.tsv",
                       separator="\t",
                       has_header=False,
                       schema={"impression_id" : pl.datatypes.Int64,
                               "user_id" : pl.datatypes.String,
                               "time" : pl.datatypes.String,
                               "history" : pl.datatypes.String,
                               "impressions" : pl.datatypes.String,
                               },
                        ignore_errors=True)

    return behaviors_lf


def get_article_category_by_id(news_lf: pl.DataFrame, id: str) -> str:
    """ Get an article's category by it's news_id.

    Args:
        news_lf (DataFrame): a DataFrame with all the news articles.
        id (str): The article's news_id

    Returns:
        str: the article's category
    """

    category = news_lf.filter(
        pl.col("news_id") == id
    ).select(
        pl.col("category")
    )

    category = category.to_numpy()
    if len(category) > 0:
        return category[0][0]


def get_articles_with_click_counts() -> pl.DataFrame:
    """ Returns the news articles by category with click counts.

    Args:
        number (int): the number of news articles by category to return.
        category (str): the category of news articles to return.
        lang (str): the target language to translate the news.

    Returns:
        DataFrame: the articles DataFrame with a new column with click counts.
    """

    news_lf = load_news_articles()
    behaviors_lf = load_news_article_engagement()
    # get all engagements in a list
    all_clicks = behaviors_lf.select(
        pl.col("impressions")
    ).rows()
    # dict to store clicks per news article ID
    clicks_per_article_id = {}
    for clicks_group in all_clicks:
        clicks = clicks_group[0].split(" ")
        for click in clicks:
            if click[-1] != "0":
                article_id = click[:-2]
                if article_id not in clicks_per_article_id:
                    category = get_article_category_by_id(news_lf,
                                                            article_id)
                    clicks_per_article_id[article_id] = {
                        "clicks": int(click[-1]),
                        "category": category}
                else:
                    clicks_per_article_id[
                        article_id]["clicks"] += int(click[-1])
    # for each clicks_per_article_id
    print(pl.DataFrame(clicks_per_article_id))


NEWS_RECS_BY_CATEGORY = {
    "type": "function",
    "function": {
        "name": "get_random_news_by_category",
        "description": "Returns the provided number of news article headlines \
from a given category. This function requires at least one category to work.",
        "parameters": {
            "type": "object",
            "properties": {
                "number": { "type": "number" },
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
                },
                "lang": { "type": "string" }
            },
            "required": ["number", "category", "lang"]
        },
    },
}


def get_random_news_by_category(number: int, category: str, lang: str) -> str:
    """ Retrieves random news articles by the given category, and returns
        their title.

    Args:
        number (int): the number of news articles by category to return.
        category (str): the category of news articles to return.
        lang (str): the target language to translate the news.

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
    ).sample(n=number).rows()

    for article in news_by_cat:
        title_and_id = "Title: \"" + article[0] + "\", \
ID: \"" + article[1] + "\""
        if lang != "en":
            load_dotenv()
            translator_endpoint = os.getenv('TRANSLATOR_ENDPOINT')
            translator_region = os.getenv('TRANSLATOR_REGION')
            translator_key = os.getenv('TRANSLATOR_KEY')
            credential = AzureKeyCredential(translator_key)
            translator_client = TextTranslationClient(credential=credential,
                                                      endpoint=translator_endpoint,
                                                      region=translator_region)
            title_and_id = translate_text(translator_client,
                                          title_and_id,
                                          lang)
        news_articles.append(title_and_id)

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
                "title": { "type": "string" },
                "lang": { "type": "string" }
            },
            "required": ["title", "lang"],
        },
    },
}


def get_article_abstract_by_title(title: str, lang: str) -> str:
    """ Retrieves a news article's abstract by the given title.

    Args:
        title (str): the title of the article to return.
        lang (str): the target language to translate the news.

    Returns:
        str: the news article's abstract.
    """
    news_lf = load_news_articles()
    abstract = news_lf.filter(
        pl.col("title") == title
    ).select(
        pl.col("abstract")
    )

    abstract = abstract.to_series().to_list()
    if len(abstract) > 0:
        abstract = abstract[0]
        if lang != "en":
            load_dotenv()
            translator_endpoint = os.getenv('TRANSLATOR_ENDPOINT')
            translator_region = os.getenv('TRANSLATOR_REGION')
            translator_key = os.getenv('TRANSLATOR_KEY')
            credential = AzureKeyCredential(translator_key)
            translator_client = TextTranslationClient(credential=credential,
                                                      endpoint=translator_endpoint,
                                                      region=translator_region)
            abstract = translate_text(translator_client,
                                      abstract,
                                      lang)
        return abstract
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
                "id": { "type": "string" },
                "lang": { "type": "string" }
            },
            "required": ["id", "lang"],
        },
    },
}


def get_article_abstract_by_id(id: str, lang: str) -> str:
    """ Retrieves a news article's abstract by the id.

    Args:
        id (str): the id of the article to return.
        lang (str): the target language to translate the news.

    Returns:
        str: the news article's abstract.
    """
    news_lf = load_news_articles()
    abstract = news_lf.filter(
        pl.col("news_id") == id
    ).select(
        pl.col("abstract")
    )

    abstract = abstract.to_series().to_list()
    if len(abstract) > 0:
        abstract = abstract[0]
        if lang != "en":
            load_dotenv()
            translator_endpoint = os.getenv('TRANSLATOR_ENDPOINT')
            translator_region = os.getenv('TRANSLATOR_REGION')
            translator_key = os.getenv('TRANSLATOR_KEY')
            credential = AzureKeyCredential(translator_key)
            translator_client = TextTranslationClient(credential=credential,
                                                      endpoint=translator_endpoint,
                                                      region=translator_region)
            abstract = translate_text(translator_client,
                                      abstract,
                                      lang)
        return abstract
    else:
        return "Abstract not found."


if __name__ == "__main__":
    print(get_random_news_by_category(2, "sports", "en"))
    print(get_article_abstract_by_title("Saints QB Drew Brees will reportedly start Sunday against Cardinals", "en"))
    print(get_article_abstract_by_id("N46279", "en"))
    print(get_article_category_by_id(load_news_articles(), "N46279"))
    get_articles_with_click_counts()