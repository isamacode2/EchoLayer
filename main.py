from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.post("/realtime")
async def realtime_proxy(request: Request):
    body = await request.body()

    # Debug logs (safe to keep for now)
    print("BODY LENGTH:", len(body))
    print("FIRST 300 CHARS:")
    print(body[:300])

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            "https://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/sdp",
            },
            content=body,
        )

    return Response(content=r.content, media_type="application/sdp")

# IMPORTANT: mount static LAST so it doesn't steal /realtime
app.mount("/", StaticFiles(directory=".", html=True), name="static")