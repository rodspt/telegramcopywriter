from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://telegram_user:telegram_pass@postgres:5432/telegram_videos")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, unique=True, index=True)
    channel_name = Column(String)
    file_name = Column(String)
    file_path = Column(String)
    file_size = Column(BigInteger)  # em bytes (suporta arquivos grandes)
    description = Column(Text, nullable=True)
    downloaded_at = Column(DateTime, default=datetime.utcnow)
    message_date = Column(DateTime)
    is_downloaded = Column(Boolean, default=False)
    file_unique_id = Column(String, unique=True, index=True)


def init_db():
    """Cria as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

