"""
Run from anywhere:
    python scripts/init_db.py
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.sqlalchemy_connect import engine, Base
from models.sqlalchemy_models import User, ChatHistory  # noqa: F401


def init_db():
    print(f"Connecting to: {engine.url}")
    print(f"Tables registered in metadata: {list(Base.metadata.tables.keys())}")

    if not Base.metadata.tables:
        print("ERROR: No tables found in metadata.")
        return

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  ✓ {table.name}")


if __name__ == "__main__":
    init_db()