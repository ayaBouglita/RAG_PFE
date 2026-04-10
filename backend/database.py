from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Connection SQL Server - Simple
SQL_SERVER = os.getenv("SQL_SERVER", "Malek")
SQL_DATABASE = os.getenv("SQL_DATABASE", "DW_Energie")

# Utiliser pyodbc avec Windows Authentication (Trusted Connection)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect=DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes"

print(f"📊 Connecting to SQL Server: {SQL_SERVER}/{SQL_DATABASE}")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ======== MODÈLES ========
class User(Base):
    __tablename__ = "app_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    __tablename__ = "app_conversations"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"))
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "app_messages"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("app_conversations.id"))
    role = Column(String(20))
    content = Column(Text)
    sql_query = Column(Text, nullable=True)
    chart_config = Column(Text, nullable=True)  # Stocker le JSON du graphique
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Créer les tables si elles n'existent pas"""
    Base.metadata.create_all(bind=engine)


def migrate_add_chart_config():
    """Ajouter la colonne chart_config si elle n'existe pas"""
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'app_messages' 
                AND COLUMN_NAME = 'chart_config'
            """))
            if result.fetchone():
                print("✓ Colonne chart_config existe déjà")
                return
            
            # Ajouter la colonne si elle n'existe pas
            conn.execute(text("""
                ALTER TABLE app_messages
                ADD chart_config TEXT NULL
            """))
            conn.commit()
            print("✓ Colonne chart_config ajoutée avec succès")
        except Exception as e:
            print(f"⚠ Migration chart_config: {e}")
