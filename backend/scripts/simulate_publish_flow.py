#!/usr/bin/env python3
"""Simula la generación de adaptaciones para varias redes y publica REAL sólo en Facebook.

Flujo:
- Genera adaptaciones simuladas para: facebook, instagram, twitter, linkedin, tiktok
- Para cada adaptación: si plataforma == facebook y no se especifica --dry-run, hace POST real a Graph API /{page_id}/photos
- Para las demás redes registra una publicación simulada en `logs/simulated_publish.log`

Usar:
  python scripts/simulate_publish_flow.py \
    --title "Título ejemplo" \
    --body "Cuerpo del post" \
    --image-url "https://ejemplo.com/imagen.jpg" \
    --page-id 851521531380035 \
    --access-token "TU_PAGE_ACCESS_TOKEN"

Opciones:
  --dry-run   : no realizará la llamada real a Facebook (todo simulado)

Requisitos:
  pip install requests
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import List, Dict

import requests


LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
SIM_LOG = os.path.join(LOG_DIR, "simulated_publish.log")


def create_adaptations(title: str, body: str, image_url: str | None) -> List[Dict]:
    """Genera adaptaciones simples por plataforma.

    Este es un simulador ligero; en el flujo real las adaptaciones vendrían del adaptador LLM.
    """
    adaptations = []
    base_caption = f"{title} — {body}"

    adaptations.append({
        "platform": "facebook",
        "caption": base_caption + "\n(Adaptado para Facebook)",
        "media_url": image_url,
    })

    adaptations.append({
        "platform": "instagram",
        "caption": title + " — versión Instagram\n#universidad",
        "media_url": image_url,
    })

    adaptations.append({
        "platform": "twitter",
        "caption": (title + " — " + (body[:200] if body else ""))[:280],
        "media_url": image_url,
    })

    adaptations.append({
        "platform": "linkedin",
        "caption": title + " — artículo académico resumido",
        "media_url": image_url,
    })

    adaptations.append({
        "platform": "tiktok",
        "caption": title + " — clip corto (simulado)",
        "media_url": None,  # tiktok expects video; here we simulate
        "video_url": image_url,  # en demo usamos la imagen como referencia
    })

    return adaptations


def log_simulated_publish(platform: str, caption: str, media_url: str | None):
    now = datetime.utcnow().isoformat() + "Z"
    entry = {"time": now, "platform": platform, "caption": caption, "media_url": media_url}
    with open(SIM_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def publish_facebook_photo(page_id: str, image_url: str, caption: str, access_token: str, graph_version: str = "v24.0"):
    endpoint = f"https://graph.facebook.com/{graph_version}/{page_id}/photos"
    data = {"url": image_url, "caption": caption, "access_token": access_token}
    resp = requests.post(endpoint, data=data, timeout=30)
    try:
        return resp.status_code, resp.json()
    except ValueError:
        return resp.status_code, {"text": resp.text}


def main():
    parser = argparse.ArgumentParser(description="Simular adaptaciones y publicar REAL sólo en Facebook Page")
    parser.add_argument("--title", required=True, help="Título del post")
    parser.add_argument("--body", required=False, default="", help="Cuerpo del post")
    parser.add_argument("--image-url", required=False, default=None, help="URL pública de la imagen")
    parser.add_argument("--page-id", required=False, default="851521531380035", help="Facebook Page ID")
    parser.add_argument("--access-token", required=False, help="Page Access Token (si omitido, Facebook será simulado)")
    parser.add_argument("--dry-run", action="store_true", help="Si se especifica, NO hará la llamada real a Facebook")
    parser.add_argument("--graph-version", required=False, default="v24.0", help="Graph API version (default v24.0)")

    args = parser.parse_args()

    adaptations = create_adaptations(args.title, args.body, args.image_url)

    print("Generadas adaptaciones:\n")
    for a in adaptations:
        print(f"- {a['platform']}: caption='{a['caption'][:80]}', media_url={a.get('media_url') or a.get('video_url')}")

    print("\nProcesando publicaciones (simuladas excepto Facebook)...\n")

    summary = []
    for a in adaptations:
        platform = a["platform"]
        caption = a.get("caption", "")
        media_url = a.get("media_url") or a.get("video_url")

        if platform == "facebook":
            if args.dry_run or not args.access_token:
                print("[Facebook] --dry-run o sin token, simulando publicación")
                log_simulated_publish("facebook", caption, media_url)
                summary.append({"platform": "facebook", "status": "simulated"})
            else:
                print("[Facebook] Publicando REAL a la Page...")
                status_code, payload = publish_facebook_photo(args.page_id, media_url, caption, args.access_token, args.graph_version)
                if status_code >= 400 or (isinstance(payload, dict) and payload.get("error")):
                    print("  ❌ Error al publicar en Facebook:", payload)
                    summary.append({"platform": "facebook", "status": "error", "response": payload})
                else:
                    print("  ✅ Facebook response:", payload)
                    summary.append({"platform": "facebook", "status": "published", "response": payload})
        else:
            # Simular para las demás plataformas
            print(f"[{platform.capitalize()}] Simulado: publicar (no se realiza llamada real)")
            log_simulated_publish(platform, caption, media_url)
            summary.append({"platform": platform, "status": "simulated"})

    print("\nResumen:")
    for s in summary:
        print("-", s)


if __name__ == "__main__":
    main()
