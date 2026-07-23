# FitCoach AI — Health & Fitness Chatbot

Two-container architecture for AWS deployment:

- **Frontend:** Next.js (port 3000)
- **Backend:** FastAPI (port 8000) with Gemini primary + OpenRouter fallback

## Architecture

```
Browser → Next.js (3000) → FastAPI (8000) → Gemini API
                                      ↘ OpenRouter (fallback)
```

## Quick Start (Docker)

1. Copy environment file (or use the existing `.env` for local testing):

```bash
cp .env.example .env
```

2. Add your API keys to `.env`:

```env
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

3. Run both containers:

```bash
docker compose up --build
```

4. Open **http://localhost:3000**

Backend health check: **http://localhost:8000/health**

## Local Development (Without Docker)

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## GitHub Secrets (Production)

| Secret | Description |
|--------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `OPENROUTER_API_KEY` | OpenRouter fallback key |
| `AWS_ACCESS_KEY_ID` | AWS deploy credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS deploy credentials |

## Project Structure

```
backend/
  app/main.py          # FastAPI routes + CORS
  app/llm_service.py   # Gemini + OpenRouter
  app/prompts.py       # Health/fitness system prompt
  Dockerfile

frontend/
  src/app/             # Next.js pages
  src/components/Chat.tsx
  Dockerfile

docker-compose.yml
.github/workflows/deploy-aws.yml
```

## Security

- `.env` is gitignored — never commit API keys
- Use GitHub Secrets for production deployment
- General wellness guidance only — not medical advice
