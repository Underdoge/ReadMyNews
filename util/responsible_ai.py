""" This module retrieves the system response in various languages if the user
triggers content filtering.
"""

import os

from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

from util.language import translate_text

CONTENT_FILTERING_MSG = "I'm sorry, but I'm not able to answer your request \
because it triggered our content filtering system. Please try again using \
more appropiate language."


def get_content_filtering_message(lang: str) -> str:
    """ Retrieve the content filtering message translated to the provided
        language.

    Args:
        lang (str): the target language.

    Returns:
        str: the content filtering message, translated if lang != "en-US"
    """

    if lang != "en-US":
        load_dotenv()
        translator_endpoint = os.getenv('TRANSLATOR_ENDPOINT')
        translator_region = os.getenv('TRANSLATOR_REGION')
        translator_key = os.getenv('TRANSLATOR_KEY')
        credential = AzureKeyCredential(translator_key)
        translator_client = TextTranslationClient(credential=credential,
                                                    endpoint=translator_endpoint,
                                                    region=translator_region)
        content_filtering_msg = translate_text(translator_client,
                                    CONTENT_FILTERING_MSG,
                                    lang)
    else:
        content_filtering_msg = CONTENT_FILTERING_MSG

    return content_filtering_msg
