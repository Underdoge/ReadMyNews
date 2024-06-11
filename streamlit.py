""" This is the Streamlit version of the app. """

import os

import azure.cognitiveservices.speech as speech_sdk
from audiorecorder import audiorecorder
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import AzureOpenAI

import streamlit as st
from streamlit.components.v1 import html
from util.language import detect_language
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
from util.speech import speech_to_text_streamlit, text_to_speech_streamlit

load_dotenv()

speech_ai_key = os.getenv('SPEECH_KEY')
speech_ai_region = os.getenv('SPEECH_REGION')
speech_config = speech_sdk.SpeechConfig(speech_ai_key, speech_ai_region)

ai_endpoint = os.getenv('LANGUAGE_ENDPOINT')
ai_key = os.getenv('LANGUAGE_KEY')
credential = AzureKeyCredential(ai_key)
text_analytics_client = TextAnalyticsClient(endpoint=ai_endpoint,
                                            credential=credential)

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


st.title("Read My News :newspaper::microphone::sound:")

if "messages" not in st.session_state:
    st.session_state.messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant that helps users get news \
article recommendations. You have access to several tools and sometimes you \
may need to call multiple tools in sequence to get answers for your users. \
Don't return the article ID. User can press the up arrow to start/stop recor \
ding."
    }
]

chat_roles = ["user", "assistant"]

for message in st.session_state.messages:
    if message["role"] in chat_roles and message["content"] is not None:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


with st.sidebar:
    st.title("Instructions")
    st.header("Press the up arrow to start/stop recording.")
    audio = audiorecorder("Record", "Stop")


user_input = st.chat_input("What can I help you with?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    lang = detect_language(text_analytics_client, [user_input])
    lang = "es-MX" if lang == "Spanish" else "en-US"
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        assistant_response = run_multiturn_conversation(
            client, model_name,
            st.session_state.messages, tools, available_functions
        )
        if hasattr(assistant_response, "choices"):
            text_to_speech_streamlit(
                speech_config, assistant_response.choices[0].message.content,
                lang)
            st.write(assistant_response.choices[0].message.content)
            st.audio("sounds/response.wav", autoplay=True)
        elif assistant_response == "content_filter":
            content_filtered_msg = get_content_filtering_message(lang)
            text_to_speech_streamlit(
                speech_config, content_filtered_msg,
                lang)
            st.write(content_filtered_msg)
            st.audio("sounds/response.wav", autoplay=True)
        else:
            print(assistant_response)
    if assistant_response != "content_filter":
        st.session_state.messages.append(
            {"role": "assistant",
                "content": assistant_response.choices[0].message.content})
    else:
        st.session_state.messages.append(
            {"role": "assistant",
                "content": content_filtered_msg})
    audio = None


if audio is not None and len(audio) > 0:
    audio.export("sounds/prompt.wav", format="wav")
    prompt, lang = speech_to_text_streamlit(speech_config)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        assistant_response = run_multiturn_conversation(
            client, model_name,
            st.session_state.messages, tools, available_functions
        )
        if hasattr(assistant_response, "choices"):
            text_to_speech_streamlit(
                    speech_config,
                    assistant_response.choices[0].message.content,
                    lang)
            st.write(assistant_response.choices[0].message.content)
            st.audio("sounds/response.wav", autoplay=True)
        elif assistant_response == "content_filter":
            content_filtered_msg = get_content_filtering_message(lang)
            text_to_speech_streamlit(
                speech_config, content_filtered_msg,
                lang)
            st.write(content_filtered_msg)
            st.audio("sounds/response.wav", autoplay=True)
        else:
            print(assistant_response)
    if assistant_response != "content_filter":
        st.session_state.messages.append(
            {"role": "assistant",
                "content": assistant_response.choices[0].message.content})
    else:
        st.session_state.messages.append(
            {"role": "assistant",
                "content": content_filtered_msg})
    audio = None


# This code allows the user to use the up arrow to stop/start recording
code = """
    recording = false
    window.parent.document.addEventListener("keydown", function (e) {
        if (e.key == "ArrowUp")
            if (!recording) {
                console.log("Start recording");
                const iframe = window.parent.document.querySelector('[title="audiorecorder.audiorecorder"]');
                const streamlitDoc = iframe.contentDocument || iframe.contentWindow.document;
                buttons = Array.from(streamlitDoc.querySelectorAll('button'));
                record_button = buttons.find((el) => el.innerText === "Record");
                record_button.click();
                recording = true
            } else {
                console.log("Stop recording");
                const iframe2 = window.parent.document.querySelector('[title="audiorecorder.audiorecorder"]');
                const streamlitDoc2 = iframe2.contentDocument || i2frame.contentWindow.document;
                buttons = Array.from(streamlitDoc2.querySelectorAll('button'));
                stop_button = buttons.find((el) => el.innerText === "Stop");
                stop_button.click();
                recording = false
            }
    });

"""
my_html = f"<script>{code}</script>"
html(my_html)
