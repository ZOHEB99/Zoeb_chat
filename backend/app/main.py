from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.llm_service import LLMService, LLMServiceError

llm_service = LLMService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await llm_service.close()


app = FastAPI(
    title="FitCoach Health Chatbot API",
    description="Proactive health and fitness AI assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=30)


class ChatResponse(BaseModel):
    reply: str
    provider: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from the user.")

    try:
        result = await llm_service.chat(
            [{"role": message.role, "content": message.content} for message in request.messages]
        )
    except LLMServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(**result)
