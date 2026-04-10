from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime
import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv

from database import create_tables, migrate_add_chart_config, get_db, User, Conversation, Message
from auth import hash_password, verify_password, create_access_token, verify_token

load_dotenv()

# Ajouter le pipeline RAG au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06_pipeline'))
from ask_database import humanize_results
from generate_sql_ollama import generate_sql
from run_query import execute_select_query
from pipeline_with_charts import RAGPipelineWithCharts

app = FastAPI(title="RAG Intelligence API", version="1.0.0")

# Security scheme for Swagger UI
security = HTTPBearer()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======== PYDANTIC SCHEMAS ========
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ConversationCreate(BaseModel):
    title: str


class MessageRequest(BaseModel):
    conversation_id: str
    message: str


class ChartConfig(BaseModel):
    type: str  # "line", "bar", "pie", "combo", "none"
    title: str = ""
    unit: str = ""
    data: dict = {}
    options: dict = {}
    statistics: dict = {}


class MessageResponse(BaseModel):
    user_message: str
    assistant_response: str
    sql_query: str
    chart_config: Optional[ChartConfig] = None


# ======== STARTUP ========
@app.on_event("startup")
def startup():
    create_tables()
    migrate_add_chart_config()
    print(" API démarrée - Tables OK")


# ======== HELPER ========
def get_token_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)):
    """Extract user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="No credentials provided")
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# ======== ROUTES ========
@app.post("/api/v1/auth/register")
def register(data: UserCreate, db = Depends(get_db)):
    """Créer un nouveau compte"""
    
    # Vérifier si utilisateur existe
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email existe")
    
    # Créer l'utilisateur
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "message": "Utilisateur créé"
    }


@app.post("/api/v1/auth/login")
def login(data: LoginRequest, db = Depends(get_db)):
    """Se connecter et obtenir un token"""
    
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    token = create_access_token({"user_id": user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@app.post("/api/v1/chat/conversations", dependencies=[Depends(security)])
def create_conversation(
    data: ConversationCreate,
    user: User = Depends(get_token_user),
    db = Depends(get_db)
):
    """Créer une nouvelle conversation"""
    
    conv = Conversation(
        id=str(uuid4()),
        user_id=user.id,
        title=data.title
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at
    }


@app.get("/api/v1/chat/conversations", dependencies=[Depends(security)])
def list_conversations(user: User = Depends(get_token_user), db = Depends(get_db)):
    """Lister les conversations de l'utilisateur"""
    
    convs = db.query(Conversation).filter(Conversation.user_id == user.id).all()
    
    return {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at
            }
            for c in convs
        ]
    }


@app.post("/api/v1/chat/message", response_model=MessageResponse, dependencies=[Depends(security)])
def chat_message(
    data: MessageRequest,
    user: User = Depends(get_token_user),
    db = Depends(get_db)
):
    """Envoyer un message et obtenir la réponse (+ graphique optionnel)"""
    
    # Vérifier que la conversation appartient à l'utilisateur
    conv = db.query(Conversation).filter(
        (Conversation.id == data.conversation_id) & (Conversation.user_id == user.id)
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Utiliser le nouveau pipeline RAG + Charts
        pipeline = RAGPipelineWithCharts()
        pipeline_result = pipeline.process_question(data.message)
        
        response = pipeline_result["response"]
        sql_query = pipeline_result["sql_query"]
        chart_config = pipeline_result.get("chart_config")
        
        # Sauvegarder les messages
        msg_user = Message(
            id=str(uuid4()),
            conversation_id=conv.id,
            role="user",
            content=data.message
        )
        msg_assistant = Message(
            id=str(uuid4()),
            conversation_id=conv.id,
            role="assistant",
            content=response,
            sql_query=sql_query,
            chart_config=json.dumps(chart_config) if chart_config else None  # Sauvegarder le chart_config en JSON
        )
        
        db.add(msg_user)
        db.add(msg_assistant)
        db.commit()
        
        # Retourner la réponse avec optionnellement un graphique
        return {
            "user_message": data.message,
            "assistant_response": response,
            "sql_query": sql_query,
            "chart_config": chart_config
        }
        
    except Exception as e:
        import traceback
        print(f" Error in chat_message: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur pipeline: {str(e)}")


@app.get("/api/v1/chat/conversations/{conversation_id}/messages", dependencies=[Depends(security)])
def get_conversation_messages(conversation_id: str, authorization: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Récupérer tous les messages d'une conversation"""
    
    # Extraire le token
    token = authorization.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Vérifier que la conversation appartient à l'utilisateur
    conversation = db.query(Conversation).filter(
        (Conversation.id == conversation_id) &
        (Conversation.user_id == user.id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Récupérer tous les messages ordonnés par date
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    message_list = []
    for msg in messages:
        chart_config = None
        if msg.chart_config:
            try:
                chart_config = json.loads(msg.chart_config)
            except:
                chart_config = None
        
        message_list.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "sql_query": msg.sql_query,
            "chart_config": chart_config,
            "created_at": msg.created_at
        })
    
    return {
        "conversation_id": conversation_id,
        "messages": message_list
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
