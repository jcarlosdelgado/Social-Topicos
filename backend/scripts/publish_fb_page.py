#!/usr/bin/env python3
"""Publicar una imagen en una Facebook Page usando Graph API v24.0.

Ejemplo:
  python scripts/publish_fb_page.py \
    --page-id 851521531380035 \
    --image-url https://ejemplo.com/imagen.jpg \
    --caption "Este es el texto que irá arriba de la imagen" \
    --access-token "TU_PAGE_ACCESS_TOKEN"

Requisitos:
  pip install requests
"""
import argparse
import sys
import requests


def publish(page_id: str, image_url: str, caption: str, access_token: str, graph_version: str = "v24.0"):
    """Publica una imagen (por URL) en la página indicada.

    Retorna (ok: bool, response_json_or_text).
    """
    endpoint = f"https://graph.facebook.com/{graph_version}/{page_id}/photos"
    data = {
        "url": image_url,
        "caption": caption,
        "access_token": access_token,
    }
    try:
        resp = requests.post(endpoint, data=data, timeout=30)
    except requests.RequestException as exc:
        return False, {"error": str(exc)}

    try:
        payload = resp.json()
    except ValueError:
        return False, {"error": "Respuesta no JSON", "text": resp.text}

    if resp.status_code >= 400 or "error" in payload:
        return False, payload

    return True, payload


def main():
    parser = argparse.ArgumentParser(description="Publicar imagen en Facebook Page (Graph API)")
    parser.add_argument("--page-id", required=False, default="851521531380035", help="ID de la Page (por defecto: 851521531380035)")
    parser.add_argument("--image-url", required=True, help="URL pública de la imagen a publicar")
    parser.add_argument("--caption", required=False, default="", help="Texto/caption para la publicación")
    parser.add_argument("--access-token", required=True, help="Page Access Token con permisos para publicar")
    parser.add_argument("--graph-version", required=False, default="v24.0", help="Versión del Graph API (por defecto: v24.0)")

    args = parser.parse_args()

    ok, result = publish(args.page_id, args.image_url, args.caption, args.access_token, args.graph_version)
    if ok:
        print("✅ Publicación enviada correctamente:")
        print(result)
        sys.exit(0)
    else:
        print("❌ Error al publicar:")
        print(result)
        sys.exit(1)


if __name__ == "__main__":
    main()
