"""Stage 1: leaf photo -> disease + severity, using a vision model on OpenRouter."""

import base64
import io

from PIL import Image, ImageOps

from llm import VISION_MODEL, chat, parse_json
from prompts import VISION_PROMPT

# Phone photos are ~4000px wide. That is far more than the model needs to see lesions, and we
# pay for image tokens by resolution, so shrink the long edge to this before sending.
MAX_EDGE = 1024

FALLBACK = {
    "crop_type": "Unknown",
    "disease_identified": "Unknown",
    "severity_percent": 0,
    "confidence_score": 0,
    "visual_evidence": "The model could not read this image clearly.",
}


def shrink(image_bytes, mime_type):
    """Rotate upright, cap the long edge, re-encode as JPEG.

    Returns (bytes, mime). On failure the original bytes and mime are passed through unchanged,
    so an odd image format still reaches the model rather than failing the whole request.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)  # phone photos arrive sideways otherwise
        img = img.convert("RGB")
        img.thumbnail((MAX_EDGE, MAX_EDGE))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        out = buf.getvalue()
        print(f"[vision] image {len(image_bytes) // 1024} KB -> {len(out) // 1024} KB "
              f"at {img.width}x{img.height}", flush=True)
        return out, "image/jpeg"
    except Exception as exc:
        print(f"[vision] could not resize ({exc}), sending original", flush=True)
        return image_bytes, mime_type


def classify_leaf(image_bytes, mime_type="image/jpeg"):
    image_bytes, mime_type = shrink(image_bytes, mime_type)
    data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode()}"
    messages = [
        {"role": "system", "content": VISION_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Diagnose this crop leaf."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        },
    ]

    print("[vision] classifying leaf image", flush=True)
    # temperature=0: classification should be reproducible. At 0.2 the same photo could come
    # back as a different disease between runs, which is fatal in a live demo.
    reply = chat(messages, VISION_MODEL, temperature=0, timeout=60)
    result = parse_json(reply.get("content"))
    if result:
        print(f"[vision] {result.get('disease_identified')} "
              f"({result.get('severity_percent')}% severity)", flush=True)
        return result

    # One retry with a blunt nudge, then give up gracefully so the demo keeps working.
    messages.append(reply)
    messages.append({"role": "user", "content": "Return only the JSON object."})
    result = parse_json(chat(messages, VISION_MODEL).get("content"))
    return result or FALLBACK
