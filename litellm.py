import requests
import json
import os
from dotenv import load_dotenv
from fastrtc import ReplyOnPause, Stream, get_stt_model, get_tts_model

# Load environment variables from .env file
load_dotenv()

# Configuration for your LiteLLM server from environment variables
LITELLM_SERVER_URL = os.getenv("LITELLM_SERVER_URL")
LITELLM_MODEL = os.getenv("LITELLM_MODEL")

stt_model = get_stt_model()
tts_model = get_tts_model()

def echo(audio):
    transcript = stt_model.stt(audio)
    print(f"User: {transcript}")
    # Prepare the payload for the LiteLLM server
    payload = {
        "model": LITELLM_MODEL,
        "messages": [
            {"role": "user", "content": transcript}
        ]
    }
    # Make the HTTP request to the LiteLLM server
    try:
        response = requests.post(
            f"{LITELLM_SERVER_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        response_json = response.json()
        response_text = response_json["choices"][0]["message"]["content"]
        print(f"LLM: {response_text}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling LiteLLM server: {e}")
        response_text = "Sorry, I am unable to connect to the language model at the moment."
        
    for audio_chunk in tts_model.stream_tts_sync(response_text):
        yield audio_chunk

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")
stream.ui.launch()