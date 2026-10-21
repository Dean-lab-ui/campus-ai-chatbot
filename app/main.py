from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.ai_provider import OpenAIProvider


STATIC_DIRECTORY = Path(__file__).resolve().parent / "static"


app = FastAPI(title="Campus AI Chatbot")

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIRECTORY),
    name="static",
)


ai_provider = OpenAIProvider()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def show_chat_interface():
    return FileResponse(STATIC_DIRECTORY / "index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply = ai_provider.generate_reply(
            message=request.message,
            user_id=request.user_id,
        )

        return ChatResponse(response=reply)

    except Exception as error:
        print(f"AI request failed: {error}")

        raise HTTPException(
            status_code=502,
            detail="The AI provider request failed.",
        ) from error