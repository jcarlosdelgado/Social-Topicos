#!/usr/bin/env python3
"""CLI que usa la base de datos (SQLAlchemy) para create -> adapt -> review -> publish.

Requisitos:
- Tener `DATABASE_URL` en el entorno y la DB inicializada (`app.db.init_db()`)
- `pip install requests python-dotenv` (python-dotenv ya se usa en app.db)

Comandos:
  create --title --body [--image-url]
  adapt  --post-id
  review --post-id
  publish --post-id [--access-token] [--dry-run]

Este script creará filas en `posts`, `adaptations` y `publish_jobs`.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import Optional

import requests
from sqlalchemy.orm import Session

from app import db as app_db
from app import models


def create_post(db: Session, title: str, body: str, image_url: Optional[str]) -> models.Post:
    p = models.Post(title=title, body=body)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_adaptations(db: Session, post: models.Post, image_url: Optional[str]):
    # Aquí puedes reemplazar por llamada a adaptador LLM real
    title = post.title
    body = post.body
    base_caption = f"{title} — {body}"
    items = [
        ("facebook", {"caption": base_caption + "\n(Adaptado para Facebook)", "media_url": image_url}),
        ("instagram", {"caption": title + " — versión Instagram\n#universidad", "media_url": image_url}),
        ("twitter", {"caption": (title + " — " + (body[:200] if body else ""))[:280], "media_url": image_url}),
        ("linkedin", {"caption": title + " — artículo académico resumido", "media_url": image_url}),
        ("tiktok", {"caption": title + " — clip corto (simulado)", "media_url": None, "video_url": image_url}),
    ]

    created = []
    for platform, content in items:
        a = models.Adaptation(post_id=post.id, platform=platform, content=content)
        db.add(a)
        created.append(a)

    db.commit()
    return created


def publish_fb(page_id: str, image_url: Optional[str], caption: str, access_token: str, graph_version: str = "v24.0"):
    endpoint = f"https://graph.facebook.com/{graph_version}/{page_id}/photos"
    data = {"url": image_url, "caption": caption, "access_token": access_token}
    resp = requests.post(endpoint, data=data, timeout=30)
    try:
        return resp.status_code, resp.json()
    except ValueError:
        return resp.status_code, {"text": resp.text}


def cmd_create(args):
    with app_db.SessionLocal() as db:
        p = create_post(db, args.title, args.body, args.image_url)
        print(f"Created post id={p.id}")


def cmd_adapt(args):
    with app_db.SessionLocal() as db:
        post = db.get(models.Post, int(args.post_id))
        if not post:
            print("Post not found")
            return
        adaptations = create_adaptations(db, post, post.body and post.body and args.image_url or None)
        print(f"Created {len(adaptations)} adaptations for post id={post.id}")


def cmd_review(args):
    with app_db.SessionLocal() as db:
        post = db.get(models.Post, int(args.post_id))
        if not post:
            print("Post not found")
            return
        print(f"Post id={post.id} title={post.title}")
        for a in post.adaptations:
            print(f"- Adaptation id={a.id} platform={a.platform} content={json.dumps(a.content, ensure_ascii=False)}")


def cmd_publish(args):
    fb_token = args.access_token or os.environ.get("FB_PAGE_ACCESS_TOKEN")
    page_id = args.page_id or os.environ.get("FB_PAGE_ID")

    with app_db.SessionLocal() as db:
        post = db.get(models.Post, int(args.post_id))
        if not post:
            print("Post not found")
            return

        for a in post.adaptations:
            job = models.PublishJob(post_id=post.id, adaptation_id=a.id, platform=a.platform, status="PENDING")
            db.add(job)
            db.commit()
            db.refresh(job)

            media_url = a.content.get("media_url") or a.content.get("video_url")
            caption = a.content.get("caption", "")

            if a.platform == "facebook":
                if args.dry_run or not fb_token or not page_id:
                    print("[Facebook] dry-run or missing token/page_id -> simulated")
                    job.status = "SIMULATED"
                    job.result = {"simulated": True}
                    db.add(job)
                    db.commit()
                else:
                    print("[Facebook] Publishing real...")
                    status_code, payload = publish_fb(page_id, media_url, caption, fb_token, args.graph_version)
                    job.status = "ERROR" if status_code >= 400 or (isinstance(payload, dict) and payload.get("error")) else "COMPLETED"
                    job.result = payload
                    db.add(job)
                    db.commit()
                    print("  ->", job.status, payload)
            else:
                print(f"[{a.platform}] simulated publish")
                job.status = "SIMULATED"
                job.result = {"simulated": True}
                db.add(job)
                db.commit()


def main():
    parser = argparse.ArgumentParser(description="DB-backed flow manager")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("create")
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=False, default="")
    p.add_argument("--image-url", required=False, default=None)

    p = sub.add_parser("adapt")
    p.add_argument("--post-id", required=True)

    p = sub.add_parser("review")
    p.add_argument("--post-id", required=True)

    p = sub.add_parser("publish")
    p.add_argument("--post-id", required=True)
    p.add_argument("--access-token", required=False)
    p.add_argument("--page-id", required=False)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--graph-version", required=False, default="v24.0")

    args = parser.parse_args()
    if args.cmd == "create":
        cmd_create(args)
    elif args.cmd == "adapt":
        cmd_adapt(args)
    elif args.cmd == "review":
        cmd_review(args)
    elif args.cmd == "publish":
        cmd_publish(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
