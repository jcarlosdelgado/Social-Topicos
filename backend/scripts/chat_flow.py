#!/usr/bin/env python3
"""Interactivo: simula una conversación con la IA para generar adaptaciones y publicar.

Flujo:
- El usuario escribe un prompt (ej: "Hoy hay aniversario de la universidad...")
- Se generan adaptaciones para las 5 redes (simuladas)
- Se muestran en pantalla para revisión
- Si apruebas, el script publica automáticamente en Facebook (real) y simula las demás

Nota: No requiere que pegues el token en el chat; puedes pasarlo por stdin cuando se solicita o usar la variable de entorno `FB_PAGE_ACCESS_TOKEN`.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests

# Ensure the backend package root is on sys.path so `from app import ...` works
# when running this script as `python scripts/chat_flow.py` from the `backend` folder.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


BASE = Path(__file__).resolve().parents[0]
LOG_DIR = BASE / ".." / "logs"
DATA_DIR = BASE / ".." / "data" / "posts"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Use DB models when available
from app import db as app_db
from app import models


def call_ollama(prompt: str, model: str, url: str, timeout: int = 30) -> Optional[str]:
    """Call a local Ollama HTTP API. Returns the raw text response or None on error.

    Expected: Ollama listening at e.g. http://localhost:11434
    Endpoint used: POST {url}/api/generate?model={model}
    """
    try:
        endpoint = url.rstrip("/") + f"/api/generate?model={model}"
        payload = {"prompt": prompt}
        resp = requests.post(endpoint, json=payload, timeout=timeout)
        resp.raise_for_status()
        # Ollama can stream; assume body contains JSON or plain text
        return resp.text
    except requests.RequestException as exc:
        print("Ollama call failed:", exc)
        return None


def generate_adaptations_with_ollama(prompt: str, image_url: Optional[str]) -> Optional[List[Dict]]:
    """Ask Ollama to return a JSON array of adaptations.

    We send explicit instructions so the model returns JSON like:
    [ {"platform":"facebook","caption":"...","media_url":"..."}, ... ]
    If Ollama is not configured or returns invalid JSON, return None.
    """
    ollama_url = os.environ.get("OLLAMA_URL")
    ollama_model = os.environ.get("OLLAMA_MODEL")
    if not ollama_url or not ollama_model:
        return None

    system_prompt = (
        "Eres un asistente que genera adaptaciones para redes sociales. "
        "Recibe un texto y una image_url opcional y devuelve SOLO un JSON array con objetos: "
        "{\"platform\":\"facebook\", \"caption\":\"...\", \"media_url\":\"...\"}. "
        "Incluye exactamente las plataformas: facebook, instagram, twitter, linkedin, tiktok. "
        "No envíes explicaciones adicionales."
    )

    user_prompt = f"{system_prompt}\n\nTexto: {prompt}\nImageURL: {image_url or ''}\n\nResponde con el JSON sin comentarios."
    raw = call_ollama(user_prompt, ollama_model, ollama_url)
    if not raw:
        return None
    # Try to find the first JSON array in the response
    try:
        # Some models may stream text; attempt to parse the whole response as JSON
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        # Otherwise try to find first '['
    except Exception:
        pass
    # Try to extract JSON array substring
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            arr = json.loads(raw[start:end+1])
            if isinstance(arr, list):
                return arr
        except Exception:
            pass
    print("No JSON array found in Ollama response")
    return None


def create_adaptations_from_prompt(prompt: str, image_url: Optional[str]) -> List[Dict]:
    """Generate adaptations using Ollama if configured, otherwise fall back to simple local simulator."""
    # Try Ollama
    ollama_result = generate_adaptations_with_ollama(prompt, image_url)
    if ollama_result:
        return ollama_result

    # Fallback simulator
    title = prompt.split(".")[0][:80]
    body = prompt
    base_caption = f"{title} — {body}"
    adaptations = [
        {"platform": "facebook", "caption": base_caption + "\n(Adaptado para Facebook)", "media_url": image_url},
        {"platform": "instagram", "caption": title + " — versión Instagram\n#universidad", "media_url": image_url},
        {"platform": "twitter", "caption": (title + " — " + (body[:200] if body else ""))[:280], "media_url": image_url},
        {"platform": "linkedin", "caption": title + " — artículo académico resumido", "media_url": image_url},
        {"platform": "tiktok", "caption": title + " — clip corto (simulado)", "media_url": None, "video_url": image_url},
    ]
    return adaptations


def log_simulated_publish(entry: Dict):
    path = LOG_DIR / "simulated_publish.log"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def publish_facebook_photo(page_id: str, image_url: str, caption: str, access_token: str, graph_version: str = "v24.0"):
    endpoint = f"https://graph.facebook.com/{graph_version}/{page_id}/photos"
    data = {"url": image_url, "caption": caption, "access_token": access_token}
    resp = requests.post(endpoint, data=data, timeout=30)
    try:
        return resp.status_code, resp.json()
    except ValueError:
        return resp.status_code, {"text": resp.text}


def persist_post(title: str, body: str, image_url: Optional[str], adaptations: List[Dict]) -> str:
    pid = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    post = {"id": pid, "title": title, "body": body, "image_url": image_url, "adaptations": adaptations, "created_at": datetime.utcnow().isoformat() + "Z"}
    path = DATA_DIR / f"{pid}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(post, fh, ensure_ascii=False, indent=2)
    return pid


def interactive():
    print("Chat-Flow: pide adaptaciones y publica (Facebook real, otras simuladas)")
    print("Escribe tu prompt (ej: 'Hoy es aniversario de la universidad...')")
    prompt = input("Prompt: ").strip()
    if not prompt:
        print("Prompt vacío. Saliendo.")
        return

    image_url = input("(Opcional) URL pública de la imagen (enter para omitir): ").strip() or None

    print("\nGenerando adaptaciones (simuladas)...\n")
    adaptations = create_adaptations_from_prompt(prompt, image_url)

    for a in adaptations:
        print(f"--- {a['platform'].upper()} ---")
        print(a.get("caption"))
        print("media:", a.get("media_url") or a.get("video_url"))
        print()

    # Persist the post so you can re-run steps later if wanted
    title = prompt.split(".")[0][:80]
    pid = persist_post(title, prompt, image_url, adaptations)
    print(f"Post guardado con id={pid}")

    # Ask for approval
    approve = input("¿Aprobar y publicar en todas las redes? (y/N): ").strip().lower()
    if approve != "y":
        print("No publicado. Puedes revisar el post más tarde en data/posts/" + pid + ".json")
        return

    # Prepare Facebook token
    fb_token = os.environ.get("FB_PAGE_ACCESS_TOKEN")
    if not fb_token:
        fb_token = input("Introduce tu Page Access Token (se usará sólo localmente): ").strip() or None

    page_id = input("Page ID (enter para usar 851521531380035): ").strip() or "851521531380035"

    summary = []
    for a in adaptations:
        platform = a["platform"]
        caption = a.get("caption", "")
        media_url = a.get("media_url") or a.get("video_url")

        if platform == "facebook":
            if not fb_token:
                print("[Facebook] No se proporcionó token — simulando")
                log_simulated_publish({"time": datetime.utcnow().isoformat() + "Z", "platform": "facebook", "caption": caption, "media_url": media_url, "post_id": pid})
                summary.append({"platform": "facebook", "status": "simulated"})
            else:
                print("[Facebook] Publicando REAL...")
                status_code, payload = publish_facebook_photo(page_id, media_url, caption, fb_token)
                if status_code >= 400 or (isinstance(payload, dict) and payload.get("error")):
                    print("  ❌ Error:", payload)
                    summary.append({"platform": "facebook", "status": "error", "response": payload})
                else:
                    print("  ✅ OK:", payload)
                    summary.append({"platform": "facebook", "status": "published", "response": payload})
        else:
            print(f"[{platform}] Simulado: publicar (no se realiza llamada real)")
            log_simulated_publish({"time": datetime.utcnow().isoformat() + "Z", "platform": platform, "caption": caption, "media_url": media_url, "post_id": pid})
            summary.append({"platform": platform, "status": "simulated"})

    print("\nResumen:")
    for s in summary:
        print("-", s)


if __name__ == "__main__":
    interactive()
