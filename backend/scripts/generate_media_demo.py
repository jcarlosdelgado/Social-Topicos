#!/usr/bin/env python3
"""Demo script: generate images and short video for a sample post using the LLM adapter.

Usage:
    python scripts/generate_media_demo.py

This will call generate_and_store_adaptations for a sample post id (must exist in DB),
or it will create a demo post.
"""
from app.db import SessionLocal, init_db
from app.llm.adapter import generate_and_store_adaptations
from app import models


def main():
    init_db()
    db = SessionLocal()
    # create demo post
    post = models.Post(title="Demo: Imagen + Video", body="Este es un contenido de prueba para generar imagen y video cortos.")
    db.add(post)
    db.commit()
    db.refresh(post)

    print(f"Created post id={post.id}")

    adapted = generate_and_store_adaptations(db, post.id, post.title, post.body, [], ["facebook","instagram","tiktok","linkedin","whatsapp"]) 
    for a in adapted:
        print(f"Adaptation {a.id} platform={a.platform} content_keys={list(a.content.keys())}")

    db.close()


if __name__ == "__main__":
    main()
