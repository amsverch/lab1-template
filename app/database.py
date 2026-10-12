import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  # <-- Важно!

# 1. Сначала создаём Base (это должно быть всегда, независимо от тестов)
Base = declarative_base()

# 2. Потом определяем URL и engine с логикой переключения
if os.environ.get("PYTEST_CURRENT_TEST"):
    DATABASE_URL = "sqlite:///./test.db"
    connect_args = {"check_same_thread": False}
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://program:test@db:5432/persons")
    connect_args = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
