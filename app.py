""" This is the app's main module which makes the calls to the Azure OpenAI
using the Python SDK.

"""

import inspect
import json
import os

import azure.cognitiveservices.speech as speech_sdk
from dotenv import load_dotenv
from openai import AzureOpenAI

from util.news import (
    NEWS_ARTICLE_ABSTRACT_BY_TITLE,
    NEWS_RECS_BY_CATEGORY,
    get_article_abstract_by_title,
    get_random_news_by_category,
)
from util.speech import speech_to_text, text_to_speech


def check_args(function: callable, args: list) -> bool:
    """ This function is used to check that all arguments are provided to the
    called function.

    Args:
        function (function): the called function
        args (list): the list of provided arguments

    Returns:
        bool: True if all required arguments were provided, otherwise False.
    """
    sig = inspect.signature(function)
    params = sig.parameters

    for name in args:
        if name not in params:
            return False

    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True

def run_multiturn_conversation(messages: list, tools: list,
                               available_functions: json) -> None:
    """ This function will process the user's prompt, get a response from
    Azure OpenAI, check if a function call was suggested and if so, make the
    call and send the function response to OpenAI so it uses the result to
    reply to the user.

    Args:
        messages (list): the history of the conversation.
        tools (list): a list with the functions' definitions.
        available_functions (dict): a dictionary with a key for each function.
    """
    response = client.chat.completions.create(
        messages=messages,
        tools=tools,
        tool_choice="auto",
        model=model_name,
        temperature=0,
    )

    while response.choices[0].finish_reason == "tool_calls":
        response_message = response.choices[0].message
        print("Recommended Function call:")
        print(response_message.tool_calls[0])
        print()

        function_name = response_message.tool_calls[0].function.name

        if function_name not in available_functions:
            return "Function " + function_name + " does not exist"
        function_to_call = available_functions[function_name]

        function_args = json.loads(
            response_message.tool_calls[0].function.arguments)
        if check_args(function_to_call, function_args) is False:
            return "Invalid number of arguments for function: " + function_name
        function_response = function_to_call(**function_args)

        print("Output of function call:")
        print(function_response)
        print()

        messages.append({
            "role": response_message.role,
            "function_call": {
                "name": response_message.tool_calls[0].function.name,
                "arguments": response_message.tool_calls[0].function.arguments,
            },
            "content": None,
        })

        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )

        print("Messages in next request:")
        for message in messages:
            print(message)
        print()

        response = client.chat.completions.create(
            messages=messages,
            tools=tools,
            tool_choice="auto",
            model=model_name,
            temperature=0,
        )

    return response


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
        NEWS_RECS_BY_CATEGORY,
        NEWS_ARTICLE_ABSTRACT_BY_TITLE
    ]

    available_functions = {
        "get_random_news_by_category":get_random_news_by_category,
        "get_article_abstract_by_title": get_article_abstract_by_title
    }

    next_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that helps users get news \
article recommendations. You have access to several tools and sometimes you \
may need to call multiple tools in sequence to get answers for your users, \
but make sure not to modify the news article titles in any way, or the other \
tools that use the titles won't work.",
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
            next_messages, tools, available_functions
        )
        if hasattr(assistant_response, "choices"):
            print("OpenAI:", assistant_response.choices[0].message.content)
            text_to_speech(
                speech_config, assistant_response.choices[0].message.content,
                lang)
        else:
            print(assistant_response)
