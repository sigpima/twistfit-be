"""One-off ops script: sync quiz question/option images and the full
catalog_models roster from the local dev database into production.

Non-destructive:
- quiz_questions/quiz_options: UPDATEs image_url only, matched by
  sort_order (question count/structure already matches between dev and
  prod — this only backfills the images added after prod was last seeded).
- catalog_models: UPDATEs existing rows (matched by `image` path) and
  INSERTs any of dev's 16 models missing from prod (prod currently only
  has the original 8). Never deletes rows.

Usage:
    cd backend && source venv/bin/activate
    PROD_DB_URL="postgresql+psycopg://user:password@host:5432/dbname?sslmode=require" \\
        python3 scripts/sync_quiz_and_models_to_prod.py
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def main() -> None:
    prod_db_url = os.environ.get("PROD_DB_URL")
    if not prod_db_url:
        print("ERROR: set the PROD_DB_URL env var to the target production database before running this.")
        sys.exit(1)

    from sqlalchemy import create_engine, text
    from app.db.session import SessionLocal
    from app.domains.quiz.models import QuizQuestion
    from app.domains.model_catalog.models import CatalogModel

    dev = SessionLocal()
    questions = dev.query(QuizQuestion).order_by(QuizQuestion.sort_order).all()
    models = dev.query(CatalogModel).order_by(CatalogModel.id).all()

    prod = create_engine(prod_db_url)
    with prod.begin() as conn:
        for q in questions:
            conn.execute(
                text("UPDATE quiz_questions SET image_url = :img WHERE sort_order = :so"),
                {"img": q.image_url, "so": q.sort_order},
            )
            for o in q.options:
                conn.execute(
                    text(
                        """
                        UPDATE quiz_options SET image_url = :img
                        WHERE sort_order = :oso
                          AND question_id = (SELECT id FROM quiz_questions WHERE sort_order = :qso)
                        """
                    ),
                    {"img": o.image_url, "oso": o.sort_order, "qso": q.sort_order},
                )
        print(f"[1/2] synced quiz image_url for {len(questions)} questions")

        updated, inserted = 0, 0
        for m in models:
            existing_id = conn.execute(
                text("SELECT id FROM catalog_models WHERE image = :image"), {"image": m.image}
            ).scalar()
            payload = {
                "name": m.name,
                "image": m.image,
                "side_image": m.side_image,
                "dossier_image": m.dossier_image,
                "pose_count": m.pose_count,
                "tagline": m.tagline,
                "undertone": m.undertone,
                "height": m.height,
                "body_shape": m.body_shape,
                "waist": m.waist,
                "personal_color": m.personal_color,
            }
            if existing_id:
                payload["id"] = existing_id
                conn.execute(
                    text(
                        """
                        UPDATE catalog_models SET
                            name=:name, side_image=:side_image, dossier_image=:dossier_image,
                            pose_count=:pose_count, tagline=:tagline, undertone=:undertone, height=:height,
                            body_shape=:body_shape, waist=:waist, personal_color=:personal_color,
                            updated_at=now()
                        WHERE id=:id
                        """
                    ),
                    payload,
                )
                updated += 1
            else:
                conn.execute(
                    text(
                        """
                        INSERT INTO catalog_models
                            (name, image, side_image, dossier_image, pose_count, tagline, undertone,
                             height, body_shape, waist, personal_color, created_at, updated_at)
                        VALUES
                            (:name, :image, :side_image, :dossier_image, :pose_count, :tagline, :undertone,
                             :height, :body_shape, :waist, :personal_color, now(), now())
                        """
                    ),
                    payload,
                )
                inserted += 1
        print(f"[2/2] catalog_models: updated {updated}, inserted {inserted}")
    print("DONE")
    dev.close()


if __name__ == "__main__":
    main()
