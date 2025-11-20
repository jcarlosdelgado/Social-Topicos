#!/usr/bin/env python3
"""CLI para flujo: crear post -> generar adaptaciones -> revisar -> publicar.

Persistencia simple en `backend/data/posts/<id>.json` para que puedas ejecutar comandos separados.

Comandos:
  create  --title --body [--image-url]              Crea un post y retorna su id
  adapt   --id                                       Genera adaptaciones y las guarda
  review  --id                                       Muestra adaptaciones para revisión
  publish --id [--access-token] [--dry-run]         Publica: FB real (si token y no dry-run), otras simuladas
  list                                              Lista posts existentes (ids y títulos)

Ejemplo rápido (modo seguro):
  python scripts/flow_manager.py create --title "Prueba" --body "Contenido" --image-url "https://ejemplo.com/imagen.jpg"
  python scripts/flow_manager.py adapt --id 20251118T123456
  python scripts/flow_manager.py review --id 20251118T123456
  python scripts/flow_manager.py publish --id 20251118T123456 --dry-run

Requisitos: `pip install requests`
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests


BASE = Path(__file__).resolve().parents[0]
DATA_DIR = BASE / ".." / "data" / "posts"
LOG_DIR = BASE / ".." / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def now_id() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S")


def save_post(post: Dict):
    pid = post["id"]
    path = DATA_DIR / f"{pid}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(post, fh, ensure_ascii=False, indent=2)


def load_post(pid: str) -> Optional[Dict]:
    path = DATA_DIR / f"{pid}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def list_posts() -> List[Dict]:
    out = []
    for p in sorted(DATA_DIR.glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as fh:
                obj = json.load(fh)
                out.append({"id": obj.get("id"), "title": obj.get("title")})
        except Exception:
            continue
    return out


def create_adaptations(title: str, body: str, image_url: Optional[str]) -> List[Dict]:
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


def cmd_create(args):
    pid = now_id()
    post = {
        "id": pid,
        "title": args.title,
        "body": args.body,
        "image_url": args.image_url,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "adaptations": None,
    }
    save_post(post)
    print(f"Post creado: id={pid}")


def cmd_adapt(args):
    post = load_post(args.id)
    if not post:
        print("Post no encontrado. Ejecuta 'create' primero con un id válido.")
        return
    if post.get("adaptations"):
        print("Advertencia: este post ya tiene adaptaciones. Se sobrescribirán.")
    adaptations = create_adaptations(post["title"], post.get("body", ""), post.get("image_url"))
    post["adaptations"] = adaptations
    post["adapted_at"] = datetime.utcnow().isoformat() + "Z"
    save_post(post)
    print(f"Adaptaciones generadas y guardadas para post id={args.id}")


def cmd_review(args):
    post = load_post(args.id)
    if not post:
        print("Post no encontrado.")
        return
    print(f"Post id: {post['id']}")
    print("Title:", post.get("title"))
    print("Body:", post.get("body"))
    print("Image:", post.get("image_url"))
    print("")
    if not post.get("adaptations"):
        print("No hay adaptaciones todavía. Ejecuta 'adapt' para generarlas.")
        return
    print("Adaptaciones:\n")
    for a in post["adaptations"]:
        print(f"- {a['platform']}:\n    caption: {a.get('caption')}\n    media: {a.get('media_url') or a.get('video_url')}\n")


def cmd_publish(args):
    post = load_post(args.id)
    if not post:
        print("Post no encontrado.")
        return
    if not post.get("adaptations"):
        print("No hay adaptaciones. Ejecuta 'adapt' primero.")
        return

    summary = []
    for a in post["adaptations"]:
        platform = a["platform"]
        caption = a.get("caption", "")
        media_url = a.get("media_url") or a.get("video_url")

        if platform == "facebook":
            if args.dry_run or not args.access_token:
                print("[Facebook] dry-run o sin token — simulando publicación")
                log_simulated_publish({"time": datetime.utcnow().isoformat() + "Z", "platform": "facebook", "caption": caption, "media_url": media_url, "post_id": post["id"]})
                summary.append({"platform": "facebook", "status": "simulated"})
            else:
                print("[Facebook] Publicando REAL...")
                status_code, payload = publish_facebook_photo(args.page_id, media_url, caption, args.access_token, args.graph_version)
                if status_code >= 400 or (isinstance(payload, dict) and payload.get("error")):
                    print("  ❌ Error:", payload)
                    summary.append({"platform": "facebook", "status": "error", "response": payload})
                else:
                    print("  ✅ OK:", payload)
                    summary.append({"platform": "facebook", "status": "published", "response": payload})
        else:
            print(f"[{platform}] Simulado: publicar")
            log_simulated_publish({"time": datetime.utcnow().isoformat() + "Z", "platform": platform, "caption": caption, "media_url": media_url, "post_id": post["id"]})
            summary.append({"platform": platform, "status": "simulated"})

    print("\nResumen:")
    for s in summary:
        print("-", s)


def cmd_list(args):
    posts = list_posts()
    if not posts:
        print("No hay posts guardados.")
        return
    for p in posts:
        print(f"- id={p['id']}, title={p.get('title')}")


def main():
    parser = argparse.ArgumentParser(description="Flow manager: create -> adapt -> review -> publish")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=False, default="")
    p.add_argument("--image-url", required=False, default=None)

    p = sub.add_parser("adapt")
    p.add_argument("--id", required=True)

    p = sub.add_parser("review")
    p.add_argument("--id", required=True)

    p = sub.add_parser("publish")
    p.add_argument("--id", required=True)
    p.add_argument("--page-id", required=False, default="851521531380035")
    p.add_argument("--access-token", required=False)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--graph-version", required=False, default="v24.0")

    sub.add_parser("list")

    args = parser.parse_args()
    if args.cmd == "create":
        cmd_create(args)
    elif args.cmd == "adapt":
        cmd_adapt(args)
    elif args.cmd == "review":
        cmd_review(args)
    elif args.cmd == "publish":
        cmd_publish(args)
    elif args.cmd == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
