import asyncio
import base64
import json
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from gemini_live import GeminiLive

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MODEL = os.getenv("MODEL", "gemini-2.5-flash-native-audio-preview-12-2025")

SYSTEM_PROMPT_1 = (
    "You are a Lead Qualifier bot for a local home renovation company. Introduce yourself first. "
    "Your job is to filter incoming calls by asking three specific 'Yes/No' questions. "
    "Ask them one by one:\n"
    "1) Do you own your home?\n"
    "2) Is your budget over $10,000?\n"
    "3) Are you looking to start within 3 months?\n"
    "If the user answers 'Yes' to all three questions, classify them as a 'Hot Lead', "
    "tell them you will transfer the call to a human agent, and then call the `end_call` function with `isLead=true`. "
    "If the user answers 'No' to any of the questions, politely thank them for their time, explain that you are not a good fit for their needs right now, and then call the `end_call` function with `isLead=false`. "
    "Be concise, friendly, and natural."
)

SYSTEM_PROMPT_2 = (
    "You are a prototype voice bot for 'QuickRupee,' a digital lending startup filtering applicants for immediate Personal Loans. "
    "Your task is to act as an inbound voice bot that screens callers based on three critical eligibility checks. "
    "Ask them one by one:\n"
    "1) Are you a salaried employee?\n"
    "2) Is your monthly 'in-hand' salary above ₹25,000?\n"
    "3) Do you reside in a metro city (e.g., Delhi, Mumbai, or Bangalore)?\n"
    "If the user answers 'Yes' to all three, mark them as 'Eligible', play a message saying an agent will call back within 10 minutes, and then call the `end_call` function with `isLead=true`. "
    "If they answer 'No' to any question, gently inform them they do not meet current criteria, and then call the `end_call` function with `isLead=false`. "
    "Be concise, professional, and empathetic."
)

TOOL_DEF = {
    "function_declarations": [
        {
            "name": "end_call",
            "description": "Ends the call. Call this function when the user has answered all qualifying questions, or when they answer 'No' to any qualifying question and the call should be ended.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "isLead": {
                        "type": "BOOLEAN",
                        "description": "True if the user answered 'Yes' to all three questions. False if they answered 'No' to any question."
                    }
                },
                "required": ["isLead"]
            }
        }
    ]
}


# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Gemini Live."""
    api_key = websocket.query_params.get("api_key") or os.getenv("GEMINI_API_KEY")
    bot_selection = websocket.query_params.get("bot", "bot1")

    await websocket.accept()

    if not api_key:
        logger.error("No API key provided.")
        await websocket.close(code=1008)
        return

    system_prompt = SYSTEM_PROMPT_2 if bot_selection == "bot2" else SYSTEM_PROMPT_1

    logger.info(f"WebSocket connection accepted. Bot: {bot_selection}")

    audio_input_queue = asyncio.Queue()


    async def audio_output_callback(data):
        try:
            await websocket.send_bytes(data)
        except Exception as e:
            logger.debug(f"Error sending audio: {e}")

    async def audio_interrupt_callback():
        # The event queue handles the JSON message, but we might want to do something else here
        pass

    transcripts = []

    async def end_call(isLead: bool):
        """Ends the call with customer and sends transcript."""
        logger.info(f"Bot invoked end_call. isLead: {isLead}")
        final_msg = {
            "type": "call_ended",
            "isLead": isLead,
            "transcript": transcripts
        }
        try:
            # Send the data to the customer UI
            await websocket.send_json(final_msg)
            # Close the connection
            await websocket.close()
        except Exception as e:
            logger.error(f"Error in end_call to customer ui: {e}")
        return "Call ended successfully."

    gemini_client = GeminiLive(
        api_key=api_key, model=MODEL, input_sample_rate=16000,
        tools=[TOOL_DEF], tool_mapping={"end_call": end_call}, system_instruction=system_prompt
    )

    async def receive_from_client():
        try:
            while True:
                message = await websocket.receive()
                
                if message.get("type") == "websocket.disconnect":
                    logger.info("WebSocket disconnected by client")
                    break

                if message.get("bytes"):
                    await audio_input_queue.put(message["bytes"])

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected (exception)")
        except Exception as e:
            logger.error(f"Error receiving from client: {e}")

    async def run_session():
        try:
            async for event in gemini_client.start_session(
                audio_input_queue=audio_input_queue,
                audio_output_callback=audio_output_callback,
                audio_interrupt_callback=audio_interrupt_callback,
            ):
                if event:
                    if event.get("type") in ["user", "gemini"]:
                        transcripts.append(event)
                        
                    # Forward events (transcriptions, etc) to client
                    try:
                        # Since end_call might already close the websocket, check state or just try
                        await websocket.send_json(event)
                    except Exception as e:
                        logger.debug(f"Error sending event: {e}")
                        break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Gemini session: {e}")

    receive_task = asyncio.create_task(receive_from_client())
    session_task = asyncio.create_task(run_session())

    done, pending = await asyncio.wait(
        [receive_task, session_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    # Ensure websocket is closed if not already
    try:
        await websocket.close()
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="localhost", port=port)
