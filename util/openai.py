""" This module defines the functions to interact with the OpenAI service."""

import inspect
import json

from openai import AzureOpenAI


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

def run_multiturn_conversation(client: AzureOpenAI, model_name: str,
                               messages: list, tools: list,
                               available_functions: json) -> None:
    """ This function will process the user's prompt, get a response from
    Azure OpenAI, check if a function call was suggested and if so, make the
    call and send the function response to OpenAI so it uses the result to
    reply to the user.

    Args:
        client (AzureOpenAI): the Azure OpenAI client.
        model_name (str): the OpenAI model name.
        messages (list): the history of the conversation.
        tools (list): a list with the functions' definitions.
        available_functions (dict): a dictionary with a key for each function.
    """

    try:
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

    except Exception:
            response = "content_filter"

    return response
