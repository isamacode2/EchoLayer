from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Optional but prevents future cross-origin headaches
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

@app.post("/realtime")
async def realtime_proxy(request: Request):
    body = await request.body()

    # Quick sanity checks
    if not OPENAI_API_KEY:
        return Response(
            content="Server misconfigured: OPENAI_API_KEY is missing",
            status_code=500,
            media_type="text/plain",
        )

    # Debug logs (fine for now)
    print("BODY LENGTH:", len(body))
    print("FIRST 50 CHARS:", body[:50])

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            "https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/sdp",
            },
            content=body,
        )

    # Critical: if OpenAI returns an error, pass it through clearly
    if r.status_code != 200:
        print("OPENAI STATUS:", r.status_code)
        print("OPENAI RESPONSE HEAD:", r.text[:300])
        return Response(
            content=r.text,
            status_code=r.status_code,
            media_type="text/plain",
        )

    return Response(content=r.content, media_type="application/sdp")

# IMPORTANT: mount static LAST so it doesn't steal /realtime
app.mount("/", StaticFiles(directory=".", html=True), name="static")