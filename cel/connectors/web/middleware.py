from fastapi import FastAPI, Request
import httpx
from loguru import logger as log
from typing import List, Dict

app = FastAPI()


messages_storage: List[str] = []

@app.post("/middleware/handle-message")
async def handle_message(request: Request):
    try:
        data = await request.json()
        log.debug(f"Received message from backend: {data}")

        message = data["message"]

        messages_storage.append(message)

        if "END" in message:
            full_message = " ".join(messages_storage)
            messages_storage.clear() 
            return {"full_message": full_message}

        return {"status": "partial", "message": "Message part received"}

    except Exception as e:
        log.error(f"Error in middleware: {e}")
        return {"status": "error", "message": str(e)}


