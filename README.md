# VoiceBot SDK - Real-Time AI Conversational Agents

A custom-built Python SDK and web application demonstrating real-time voice-based conversational AI agents using advanced multimodal capabilities. This project showcases two specialized voice bots: a home renovation lead qualifier and a personal loan eligibility screener, built with a robust FastAPI backend and a clean vanilla JavaScript frontend.

## Overview

This application provides a framework for creating intelligent voice bots that can conduct structured conversations, qualify leads, and make decisions in real-time. The system leverages cutting-edge AI for natural speech processing, transcription, and automated decision-making.

## Key Features

- **Dual Bot System**: Two distinct conversational agents with specialized qualification logic
- **Real-Time Audio Processing**: Bidirectional audio streaming with low-latency response
- **Automated Lead Qualification**: Structured question flows with intelligent decision-making
- **WebSocket Communication**: Efficient real-time data exchange between frontend and backend
- **Transcription Services**: Automatic speech-to-text for both user input and AI responses
- **Tool Integration**: Custom function calling for automated actions (call termination, lead classification)
- **Cross-Platform Compatibility**: Works on modern web browsers with microphone access

## Bots Included

### 1. Home Renovation Lead Qualifier

A specialized bot for a local home renovation company that filters potential customers through three critical qualification questions:

- Home ownership verification
- Budget assessment ($10,000+ threshold)
- Timeline confirmation (within 3 months)

**Outcome**: Classifies leads as "Hot" or "Not Qualified" and handles call routing accordingly.

### 2. QuickRupee Loan Eligibility Screener

A prototype voice bot for a digital lending startup that screens personal loan applicants based on:

- Employment status (salaried employee)
- Income verification (₹25,000+ monthly in-hand salary)
- Location eligibility (metro cities: Delhi, Mumbai, Bangalore)

**Outcome**: Determines applicant eligibility and manages follow-up communication.

## Quick Start

### Prerequisites

- Python 3.8+
- A valid Gemini API key from Google AI Studio
- Modern web browser with microphone permissions

### Installation

1. **Clone and setup environment:**

   ```bash
   git clone <your-repo-url>
   cd voicebot-sdk
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API Key:**
   Create a `.env` file in the project root:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Launch the application:**

   ```bash
   python main.py
   ```

4. **Access the interface:**
   Open your browser and navigate to `http://localhost:8000`

## Architecture

### Backend Components

#### `main.py` - FastAPI Server

- Handles WebSocket connections for real-time communication
- Manages bot selection and configuration
- Processes audio streams and event routing
- Implements CORS for frontend integration

#### `gemini_live.py` - AI Engine Wrapper

- Custom wrapper around Google's Gen AI SDK
- Manages live session connections and audio streaming
- Handles tool function calls and responses
- Processes transcription events and interruptions

### Frontend Components

#### `index.html` - User Interface

- Clean, responsive web interface
- Bot selection controls
- Real-time status indicators
- Session management buttons

#### `main.js` - Application Logic

- UI state management
- Bot selection handling
- Connection lifecycle management

#### `gemini-client.js` - Communication Layer

- WebSocket client implementation
- Message routing and event handling
- Audio data transmission

#### `media-handler.js` - Audio Processing

- Microphone access and audio capture
- Real-time audio streaming
- Playback of AI responses

#### `pcm-processor.js` - Audio Worklet

- Low-level PCM audio processing
- Efficient audio data handling

## Configuration Options

### Environment Variables

- `GEMINI_API_KEY`: Your Google AI Studio API key (required)
- `MODEL`: AI model selection (default: gemini-2.5-flash-native-audio-preview-12-2025)

### Bot Selection

Pass `?bot=bot1` or `?bot=bot2` in the WebSocket URL to select the desired bot.

## API Reference

### WebSocket Endpoint: `/ws`

**Query Parameters:**

- `api_key`: Override the default API key
- `bot`: Select bot (`bot1` for renovation, `bot2` for loans)

**Message Types:**

- Audio chunks: Binary data for real-time audio
- Events: JSON objects for transcriptions, tool calls, session status

### Tool Functions

#### `end_call(isLead: boolean)`

Terminates the conversation and classifies the result.

- `isLead: true` - Qualified lead, triggers agent transfer
- `isLead: false` - Disqualified, ends session politely

## Development

### Project Structure

```
voicebot-sdk/
├── main.py                 # FastAPI application server
├── gemini_live.py          # AI session management
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
└── frontend/
    ├── index.html          # Main web interface
    ├── main.js             # UI application logic
    ├── gemini-client.js    # WebSocket communication
    ├── media-handler.js    # Audio capture/playback
    ├── pcm-processor.js    # Audio processing worklet
    └── style.css           # Interface styling
```

### Adding New Bots

1. Define a new system prompt in `main.py`
2. Add bot selection logic in the WebSocket handler
3. Update the frontend radio buttons if needed
4. Test the qualification flow

### Customization

The system is designed to be easily extensible:

- Modify system prompts for different conversation flows
- Add new tool functions for additional actions
- Customize audio settings and voice selection
- Extend the frontend for additional UI features

## Security Considerations

- Store API keys securely using environment variables
- Implement proper CORS policies for production deployment
- Validate WebSocket origins and messages
- Monitor API usage and implement rate limiting

## Troubleshooting

### Common Issues

**Microphone Access Denied:**

- Ensure HTTPS in production or localhost development
- Check browser permissions for microphone access

**WebSocket Connection Failed:**

- Verify API key is correctly set
- Check network connectivity and firewall settings
- Confirm the server is running on port 8000

**Audio Quality Issues:**

- Test microphone input levels
- Check browser compatibility for WebRTC
- Verify audio format compatibility

## Contributing

This project demonstrates custom implementation of real-time AI conversational systems. For modifications or extensions, ensure compatibility with the existing WebSocket protocol and tool function interfaces.
