""" This module defines the functions for text-to-speech and speech-to-text."""
import azure.cognitiveservices.speech as speech_sdk
from azure.cognitiveservices.speech import SpeechConfig

PROPERTIES = speech_sdk.PropertyId
ADSLR = PROPERTIES.SpeechServiceConnection_AutoDetectSourceLanguageResult

def text_to_speech(speech_config: SpeechConfig, text: str, lang: str) -> None:
    """ Synthetizes the provided text as sound.

    Args:
        speech_config (SpeechConfig): the speech client credentials
        text (str): the text to speak
        lang (str): the language of the text
    """

    match lang:
        case "es-MX":
            speech_config.speech_synthesis_voice_name = "es-MX-CarlotaNeural"
        case "en-US":
            speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingu\
alNeural"

    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    speak = speech_synthesizer.speak_text_async(text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)


def text_to_speech_streamlit(speech_config: SpeechConfig,
                             text: str, lang: str) -> None:
    """ Synthetizes the provided text as sound and saves it to an audio file
        for Streamlit to reproduce.

    Args:
        speech_config (SpeechConfig): the speech client credentials
        text (str): the text to speak
        lang (str): the language of the text
    """

    match lang:
        case "es-MX":
            speech_config.speech_synthesis_voice_name = "es-MX-CarlotaNeural"
        case "en-US":
            speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingu\
alNeural"

    audio_config = speech_sdk.audio.AudioOutputConfig(
        filename="sounds/response.wav")
    speech_synthesizer = speech_sdk.SpeechSynthesizer(
        speech_config, audio_config)

    speak = speech_synthesizer.speak_text_async(text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)


def speech_to_text(speech_config: SpeechConfig) -> tuple[str, str]:
    """ Transcribes the sound from the microphone into text.

    Args:
        speech_config (SpeechConfig): the speech client credentials

    Returns:
        tuple[str, str]: a tuple with the text and language detected.
    """

    text = ''
    language = ''
    language_config = speech_sdk.languageconfig.AutoDetectSourceLanguageConfig(
                                                languages=["en-US", "es-MX"])

    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(
        speech_config, audio_config,
        auto_detect_source_language_config=language_config)

    print("Speak now...")
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        text = speech.text
        language = speech.properties[ADSLR]
        print("Text:", text)
        print("Language:", language)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    return text, language


def speech_to_text_streamlit(speech_config: SpeechConfig) -> tuple[str, str]:
    """ Transcribes the sound from an audio file into text.

    Args:
        speech_config (SpeechConfig): the speech client credentials.

    Returns:
        tuple[str, str]: a tuple with the text and language detected.
    """

    text = ''
    language = ''
    language_config = speech_sdk.languageconfig.AutoDetectSourceLanguageConfig(
                                                languages=["en-US", "es-MX"])

    audio_config = speech_sdk.AudioConfig(filename='sounds/prompt.wav')
    speech_recognizer = speech_sdk.SpeechRecognizer(
        speech_config, audio_config,
        auto_detect_source_language_config=language_config)

    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        text = speech.text
        language = speech.properties[ADSLR]
        print("Text:", text)
        print("Language:", language)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    return text, language
