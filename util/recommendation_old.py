from dotenv import load_dotenv
import os

# Import namespaces
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
import azure.cognitiveservices.speech as speech_sdk

def main():

    global speech_config
    # Get Configuration Settings
    load_dotenv()
    language_service_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
    language_service_key = os.getenv('LS_CONVERSATIONS_KEY')
    cls_project = os.getenv('PROJECT')
    deployment_slot = os.getenv('DEPLOYMENT')
    speech_ai_key = os.getenv('SPEECH_KEY')
    speech_ai_region = os.getenv('SPEECH_REGION')
    speech_config = speech_sdk.SpeechConfig(speech_ai_key, speech_ai_region)

    text_to_speech("Hello, what can I help you with today?", "en")
    text_to_speech("Hola, ¿en qué te puedo ayudar hoy?", "es")

    userText = ''
    while True:
        try :
            userText, language = speech_to_text()
            if userText == 'Quit.' or userText == 'Salir.':
                break
            if userText.lower() != 'quit.' and userText.lower() != 'salir.':

                # Create a client for the Language service model
                client = ConversationAnalysisClient(
                    language_service_endpoint, AzureKeyCredential(language_service_key))

                with client:
                    query = userText
                    result = client.analyze_conversation(
                        task={
                            "kind": "Conversation",
                            "analysisInput": {
                                "conversationItem": {
                                    "participantId": "1",
                                    "id": "1",
                                    "modality": "text",
                                    "language": "en",
                                    "text": query
                                },
                                "isLoggingEnabled": False
                            },
                            "parameters": {
                                "projectName": cls_project,
                                "deploymentName": deployment_slot,
                                "verbose": True
                            }
                        }
                    )

                top_intent = result["result"]["prediction"]["topIntent"]
                entities = result["result"]["prediction"]["entities"]

                print("view top intent:")
                print("\ttop intent: {}".format(result["result"]["prediction"]["topIntent"]))
                print("\tcategory: {}".format(result["result"]["prediction"]["intents"][0]["category"]))
                print("\tconfidence score: {}\n".format(result["result"]["prediction"]["intents"][0]["confidenceScore"]))

                print("view entities:")
                for entity in entities:
                    print("\tcategory: {}".format(entity["category"]))
                    print("\ttext: {}".format(entity["text"]))
                    print("\tconfidence score: {}".format(entity["confidenceScore"]))

                print("query: {}".format(result["result"]["query"]))

                # Apply the appropriate action
                if top_intent == 'RecommendMovie':
                    # Check for entities
                    match language:
                        case "en-US":
                            text_to_speech("Sure, calling the movie recommendation model.", "en")
                        case "es-MX":
                            text_to_speech("Claro, llamando al modelo de recomendación de películas.", "es")
                    # Call RecommendMovie()
                
                elif top_intent == 'RecommendTvShow':
                    match language:
                        case "en-US":
                            text_to_speech("Sure, calling the tv show recommendation model.", "en")
                        case "es-MX":
                            text_to_speech("Claro, llamando al modelo de recomendación de series de televisión.", "es")
                
                elif top_intent == 'Quit':
                    match language:
                        case "en-US":
                            text_to_speech("Goodbye!.", "en")
                        case "es-MX":
                            text_to_speech("¡Hasta luego!", "es")
                    break

                else:
                    # Some other intent (for example, "None") was predicted
                    match language:
                        case "en-US":
                            text_to_speech('Try asking me for a movie recommendation.', "en")
                        case "es-MX":
                            text_to_speech('Intenta pedirme una recomendación de una película.', "es")

        except Exception as ex:
            print(ex)
            break


def text_to_speech(text: str, lang: str) -> None:
    match lang:
        case "es":
            speech_config.speech_synthesis_voice_name = "es-MX-CarlotaNeural"
        case "en":
            speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
    # speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural' # change this
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    

    # Synthesize spoken output
    speak = speech_synthesizer.speak_text_async(text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)


def speech_to_text():
    command = ''
    language = ''
    language_config = speech_sdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "es-MX"])

    # Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config, auto_detect_source_language_config=language_config)

    # Process speech input
    print("Speak now...")
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        language = speech.properties[speech_sdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
        print("Command:", command)
        print("Language:", language)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return command, language

if __name__ == "__main__":
    main()
