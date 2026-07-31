"""FastAPI backend: runs vision -> ReAct agent, with a streaming variant for live progress."""

import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import run_agent, stream_agent
from vision import classify_leaf

app = FastAPI(title="Crop Treatment Advisor")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Deliberately sync, not async: the work below is blocking network I/O, so FastAPI runs this
# in a worker thread. As "async def" it would block the event loop and stall every other request.
@app.post("/analyze")
def analyze(
    file: UploadFile = File(...),
    city: str = Form(...),
    state: str = Form(""),
):
    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(400, "Empty image upload.")

    try:
        diagnosis = classify_leaf(image_bytes, file.content_type or "image/jpeg")
        result = run_agent(diagnosis, city, state)
    except Exception as exc:
        raise HTTPException(500, f"Analysis failed: {exc}")

    return {
        "diagnosis": diagnosis,
        "recommendation": result["answer"],
        "trace": result["trace"],
    }


@app.post("/analyze/stream")
def analyze_stream(
    file: UploadFile = File(...),
    city: str = Form(...),
    state: str = Form(""),
):
    """Same work as /analyze, but emits newline-delimited JSON events as it happens, so the
    UI can show the diagnosis immediately and narrate each tool call while the agent works."""
    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(400, "Empty image upload.")

    def events():
        def line(obj):
            return json.dumps(obj) + "\n"

        try:
            yield line({"type": "status", "message": "Analysing the leaf photo..."})
            diagnosis = classify_leaf(image_bytes, file.content_type or "image/jpeg")
            yield line({"type": "diagnosis", "data": diagnosis})

            for event in stream_agent(diagnosis, city, state):
                yield line(event)
        except Exception as exc:
            yield line({"type": "error", "message": str(exc)})

    return StreamingResponse(events(), media_type="application/x-ndjson")
