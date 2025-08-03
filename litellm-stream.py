import requests
import json
import os
import re
from dotenv import load_dotenv
from fastrtc import ReplyOnPause, Stream, get_stt_model, get_tts_model

# Load environment variables from .env file
load_dotenv()

# Configuration for your LiteLLM server from environment variables
LITELLM_SERVER_URL = os.getenv("LITELLM_SERVER_URL")
LITELLM_MODEL = os.getenv("LITELLM_MODEL")

# Optional configuration from environment variables with defaults
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 100))  # Text chunk size before TTS
API_KEY = os.getenv("API_KEY", "")  # API key if needed

stt_model = get_stt_model()
tts_model = get_tts_model()

def echo(audio):
    transcript = stt_model.stt(audio)
    print(f"User: {transcript}")
    
    # Prepare the payload for the LiteLLM server with stream=True
    payload = {
        "model": LITELLM_MODEL,
        "messages": [
            {"role": "user", "content": transcript}
        ],
        "stream": True  # Enable streaming
    }
    
    # Set up headers with API key if provided
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    # Make the HTTP request to the LiteLLM server with streaming
    try:
        response = requests.post(
            f"{LITELLM_SERVER_URL}/v1/chat/completions",
            json=payload,
            headers=headers,
            stream=True  # Enable streaming on the request
        )
        response.raise_for_status()
        
        # Process the streaming response
        accumulated_text = ""
        pending_text = ""
        
        for line in response.iter_lines():
            if line:
                # Skip the "data: " prefix and parse the JSON
                line_text = line.decode('utf-8')
                if line_text.startswith("data: "):
                    json_str = line_text[6:]  # Remove "data: " prefix
                    
                    # Skip "[DONE]" message at the end
                    if json_str.strip() == "[DONE]":
                        continue
                    
                    try:
                        chunk = json.loads(json_str)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                content = delta["content"]
                                accumulated_text += content
                                pending_text += content
                                
                                # Check if we have enough text to speak
                                if pending_text.endswith((".", "!", "?", ":", ";", "\n")) or len(pending_text) > CHUNK_SIZE:
                                    print(f"TTS chunk: {pending_text}")
                                    plain_text = prepare_markdown_for_speech(pending_text)
                                    for audio_chunk in tts_model.stream_tts_sync(plain_text):
                                        yield audio_chunk
                                    pending_text = ""
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON: {e}")
                        continue
                        
        # Speak any remaining text
        if pending_text:
            print(f"Final TTS chunk: {pending_text}")
            for audio_chunk in tts_model.stream_tts_sync(pending_text):
                yield audio_chunk
                
        print(f"Full LLM response: {accumulated_text}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling LiteLLM server: {e}")
        error_message = "Sorry, I am unable to connect to the language model at the moment."
        for audio_chunk in tts_model.stream_tts_sync(error_message):
            yield audio_chunk

def prepare_markdown_for_speech(text):
    """Convert markdown text to be more suitable for text-to-speech synthesis."""
    
    # Replace URLs with a simple mention
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    # Remove standalone URLs
    text = re.sub(r'https?://\S+', 'link', text)
    
    # Handle headers by removing # symbols
    text = re.sub(r'^#+\s*(.*?)$', r'\1', text, flags=re.MULTILINE)
    
    # Handle bold text (**text** or __text__)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Handle italic text (*text* or _text_)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Handle code blocks and inline code
    text = re.sub(r'```.*?\n(.*?)```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Handle bullet points
    text = re.sub(r'^\s*[\*\-\+]\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
    
    # Handle numbered lists
    text = re.sub(r'^\s*\d+\.\s+(.*?)$', r'\1', text, flags=re.MULTILINE)
    
    # Handle blockquotes
    text = re.sub(r'^\s*>\s*(.*?)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")
stream.ui.launch()