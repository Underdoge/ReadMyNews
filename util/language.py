""" This module contains the functions used to detect language using Azure AI
Text Analytics.
"""

from azure.ai.textanalytics import TextAnalyticsClient


def detect_language(client: TextAnalyticsClient, text: str) -> str:
    """ Detect the language of the provided text.

    Args:
        client (TextAnalyticsClient): the text analytics client.
        text (str): the text to analyze.

    Returns:
        str: the detected language
    """
    detected_language = client.detect_language(text)[0]
    return detected_language.primary_language.name
