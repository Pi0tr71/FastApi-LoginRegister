from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ścieżka do pliku bazy danych SQLite
DATABASE_URL = "sqlite:///baza_danych.db"

# Tworzenie silnika (engine) bazy danych
engine = create_engine(DATABASE_URL)

# Deklaratywna baza danych, na której bazują modele
Base = declarative_base()

# Fabryka sesji, która tworzy sesje do komunikacji z bazą danych
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
