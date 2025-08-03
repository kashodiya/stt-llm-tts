# STT-LLM-TTS

A voice conversation application that converts Speech-to-Text (STT), processes it through a Large Language Model (LLM), and converts the response back to speech using Text-to-Speech (TTS).

## Overview

This project creates an interactive voice interface where:
1. User speech is captured and converted to text
2. The text is sent to an LLM (via LiteLLM) for processing
3. The LLM's response is converted back to speech in real-time

## Features

- **Speech-to-Text**: Captures and transcribes user speech
- **LLM Integration**: Processes text through any LLM supported by LiteLLM
- **Text-to-Speech**: Converts LLM responses to natural-sounding speech
- **Streaming Support**: Two versions available:
  - `litellm.py`: Basic version that waits for complete LLM response before TTS
  - `litellm-stream.py`: Advanced version that streams LLM responses in chunks for faster TTS feedback

## Requirements

### Prerequisites
- Python 3.12+
- LiteLLM server running somewhere accessible
- Microphone and speakers/headphones
- Modern web browser with WebRTC support (Chrome, Firefox, Edge, Safari)

### System Requirements
- **CPU**: Any modern multi-core CPU (4+ cores recommended for smooth performance)
- **RAM**: Minimum 4GB, 8GB+ recommended
- **Storage**: ~500MB for application and dependencies
- **Network**: Stable internet connection for LLM API access

### Dependencies
Dependencies listed in pyproject.toml:
- fastrtc[stt] >= 0.0.19
- kokoro-onnx >= 0.4.7
- loguru >= 0.7.3
- python-dotenv >= 1.1.1

## Setup

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -e .`
5. Copy `.env.example` to `.env` and configure:
   ```
   LITELLM_SERVER_URL=your_litellm_server_url
   LITELLM_MODEL=your_preferred_model
   API_KEY=your_api_key_if_needed
   CHUNK_SIZE=100  # Optional: text chunk size for streaming version
   ```

## Usage

### Basic Version
```bash
python litellm.py
```

### Streaming Version (Recommended)
```bash
python litellm-stream.py
```

## Version Comparison

This project offers two implementations with different capabilities:

### litellm.py (Basic Version)
- Simpler implementation with fewer features
- Waits for the complete LLM response before starting TTS
- Suitable for short responses or when latency is not a concern
- Easier to understand and modify

### litellm-stream.py (Recommended)
- Streams LLM responses in chunks for faster perceived response time
- Processes text at natural breaks (periods, commas, etc.)
- Includes markdown processing to improve speech quality
- Supports additional configuration options (CHUNK_SIZE, API_KEY)
- Better user experience for longer responses

## How It Works

1. The application uses `fastrtc` to create a web interface with audio streaming capabilities
2. When you speak, the STT model transcribes your speech
3. The transcript is sent to the LiteLLM server
4. The LLM response is processed:
   - In the basic version: The complete response is converted to speech
   - In the streaming version: The response is chunked at natural breaks (periods, commas, etc.) and converted to speech in real-time
5. The speech is played back through your speakers

### FastRTC Integration

This project leverages [FastRTC](https://fastrtc.org/), a real-time communication library for Python that:
- Provides automatic voice detection and turn-taking capabilities
- Creates a web-based UI automatically with `.ui.launch()`
- Handles WebRTC connections for real-time audio streaming
- Uses the `ReplyOnPause` handler to detect when a user has finished speaking before processing their input

### Kokoro-ONNX TTS

For text-to-speech functionality, this project uses [Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx), a high-performance TTS library that:
- Supports multiple languages and voices
- Provides near real-time performance
- Uses ONNX runtime for optimized inference
- Is lightweight (~300MB for standard models, ~80MB for quantized models)

### LiteLLM Integration

This project connects to language models through [LiteLLM](https://github.com/BerriAI/litellm), which:
- Provides a unified API for accessing various LLM providers (OpenAI, Anthropic, Google, etc.)
- Enables easy switching between different models
- Supports streaming responses for real-time interactions
- Handles API key management and request formatting

## Markdown Processing

The streaming version includes a `prepare_markdown_for_speech` function that cleans up markdown formatting from LLM responses before TTS processing, improving speech quality by:
- Removing URLs, code blocks, and HTML tags
- Converting headers, bullet points, and numbered lists to plain text
- Handling bold and italic formatting

## Contributing

Contributions to this project are welcome! Here are some ways you can contribute:

1. **Bug Reports**: If you find a bug, please create an issue with detailed steps to reproduce it
2. **Feature Requests**: Suggest new features or improvements
3. **Code Contributions**: Submit pull requests with bug fixes or new features
4. **Documentation**: Help improve or translate the documentation
5. **Testing**: Test the application on different platforms and with different LLM providers

## License

[Add license information here]

## Acknowledgments

This project is built using several open-source libraries:
- [FastRTC](https://fastrtc.org/) for real-time audio communication
- [Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx) for text-to-speech
- [LiteLLM](https://github.com/BerriAI/litellm) for LLM integration
- [python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management

## Conclusion

STT-LLM-TTS provides a simple yet powerful way to create voice-based conversational interfaces with any LLM. By combining speech-to-text, language model processing, and text-to-speech technologies, it enables natural voice interactions that can be used for various applications including virtual assistants, accessibility tools, educational platforms, and more.
