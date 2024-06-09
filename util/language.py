""" This module contains the functions used to detect language using Azure AI
Text Analytics.
"""

from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.translation.text import TextTranslationClient


def detect_language(client: TextAnalyticsClient, text: str) -> str:
    """ Detect the language of the provided text.

    Args:
        client (TextAnalyticsClient): the Azure AI text analytics client.
        text (str): the text to analyze.

    Returns:
        str: the detected language
    """
    detected_language = client.detect_language(text)[0]
    return detected_language.primary_language.name


def translate_text(client: TextTranslationClient,
                   text: str, target_lang: str) -> str:
    """ Translate the given text to the target_lang.

    Args:
        client (TextTranslationClient): the Azure AI Translator client.
        text (str): the text to stranslate.
        target_lang (str): the target language to translate it to.

    Returns:
        str: the translated text.
    """

    input_text_elements = [text]
    translation_response = client.translate(
        body=input_text_elements, to_language=[target_lang])
    translation = translation_response[0] if translation_response else None
    if translation:
        for translated_text in translation.translations:
            return translated_text.text
