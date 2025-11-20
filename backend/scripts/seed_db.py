#!/usr/bin/env python3
"""Script de utilidad para poblar la base de datos con datos de ejemplo.

Uso:
  1. Asegúrate de haber arrancado Postgres y Redis via docker-compose (ver README).
  2. Exporta las variables de entorno (ej. `source env_setup.sh`).
  3. Arranca la API (uvicorn) y opcionalmente un worker Celery.
  4. Ejecuta este script desde la carpeta `backend/`:
     python scripts/seed_db.py

El script inserta varios `Post`, genera adaptaciones usando el adaptador mock
y encola `PublishJob`s (si Redis está activo y el worker corre, se procesarán).
"""

from datetime import datetime
from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import SessionLocal, init_db
from app import models
from app.llm.adapter import generate_and_store_adaptations
from app.tasks import publish_adaptation


SAMPLE_POSTS = [
    {
        "title": "Lanzamiento de nuevo producto",
        "body": "Hoy lanzamos nuestra nueva línea de productos sostenibles pensados para mejorar la vida urbana.",
    },
    {
        "title": "Evento comunitario este fin de semana",
        "body": "Únete al evento de limpieza del barrio este sábado. Trae guantes y ganas de colaborar.",
    },
    {
        "title": "Convocatoria de empleo: Desarrollador/a",
        "body": "Buscamos un desarrollador backend con experiencia en Python y APIs para unirse a nuestro equipo.",
    },
]


def seed():
    # show which DATABASE_URL is being used (helps avoid sqlite/postgres confusion)
    import os
    print("Using DATABASE_URL:", os.environ.get("DATABASE_URL"))
    init_db()
    db = SessionLocal()
    try:
        created_posts = []
        for p in SAMPLE_POSTS:
            post = models.Post(title=p["title"], body=p["body"])
            db.add(post)
            db.commit()
            db.refresh(post)
            print(f"Created post id={post.id} title='{post.title}'")
            created_posts.append(post)

            # generate and store adaptations for main platforms
            targets = ["facebook", "instagram", "tiktok", "linkedin", "whatsapp"]
            adapters = generate_and_store_adaptations(db, post.id, post.title, post.body, [], targets)
            print(f"  -> Created {len(adapters)} adaptations for post {post.id}")

            # create publish jobs for each adaptation and enqueue them
            for a in adapters:
                job = models.PublishJob(post_id=post.id, adaptation_id=a.id, platform=a.platform, status="PENDING")
                db.add(job)
                db.commit()
                db.refresh(job)
                print(f"    -> Created job id={job.id} platform={job.platform}")
                # enqueue the task so worker can process it (requires Redis + worker)
                try:
                    task = publish_adaptation.delay(job.id)
                    job.task_id = task.id
                    db.add(job)
                    db.commit()
                    print(f"       enqueued task_id={task.id}")
                except Exception as e:
                    print(f"       could not enqueue task (is Redis up?): {e}")

        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
