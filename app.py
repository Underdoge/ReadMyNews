""" This is the app's main module which makes the calls to Azure OpenAI using
the Python SDK.

"""

import inspect
import json
import os

import azure.cognitiveservices.speech as speech_sdk
from dotenv import load_dotenv
from openai import AzureOpenAI

from util.news import (
    MOST_ENGAGED_NEWS_BY_CATEGORY,
    NEWS_ARTICLE_ABSTRACT_BY_ID,
    NEWS_ARTICLE_ABSTRACT_BY_TITLE,
    get_article_abstract_by_id,
    get_article_abstract_by_title,
    get_most_engaged_news_by_category,
)
from util.openai import run_multiturn_conversation
from util.responsible_ai import get_content_filtering_message
from util.speech import speech_to_text, text_to_speech

if __name__ == "__main__":

    load_dotenv()

    speech_ai_key = os.getenv('SPEECH_KEY')
    speech_ai_region = os.getenv('SPEECH_REGION')
    speech_config = speech_sdk.SpeechConfig(speech_ai_key, speech_ai_region)

    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key = os.getenv("AZURE_OPENAI_KEY"),
        api_version = os.getenv("OPENAI_API_VERSION"),
    )

    model_name = os.getenv("MODEL_NAME")

    tools = [
        MOST_ENGAGED_NEWS_BY_CATEGORY,
        NEWS_ARTICLE_ABSTRACT_BY_TITLE,
        NEWS_ARTICLE_ABSTRACT_BY_ID
    ]

    available_functions = {
        "get_most_engaged_news_by_category": get_most_engaged_news_by_category,
        "get_article_abstract_by_title": get_article_abstract_by_title,
        "get_article_abstract_by_id": get_article_abstract_by_id
    }

    next_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that helps users get news \
article recommendations. You have access to several tools and sometimes you \
may need to call multiple tools in sequence to get answers for your users. \
Don't return the article ID. User can press the up arrow to start/stop recor \
ding."
        }
    ]

    while True:

        prompt, lang = speech_to_text(speech_config)
        next_messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        assistant_response = run_multiturn_conversation(
            client, model_name, next_messages, tools, available_functions
        )
        if hasattr(assistant_response, "choices"):
            print("OpenAI:", assistant_response.choices[0].message.content)
            text_to_speech(
                speech_config, assistant_response.choices[0].message.content,
                lang)
        elif assistant_response == "content_filter":
            content_filtered_msg = get_content_filtering_message(lang)
            text_to_speech(
                speech_config, content_filtered_msg,
                lang)
        else:
            print(assistant_response)
