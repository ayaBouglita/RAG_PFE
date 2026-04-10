from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import sys
import os

# Importer votre code RAG
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06_pipeline'))
from ask_database import humanize_results
from generate_sql_ollama import generate_sql
from run_query import execute_select_query
from retrieve import Retriever

from database import User, Conversation, Message, get_db
from auth import hash_password, verify_password, create_access_token, verify_token


router = APIRouter()


# ======== PYDANTIC SCHEMAS ========
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class MessageRequest(BaseModel):
    conversation_id: str
    message: str


class MessageResponse(BaseModel):
    user_message: str
    assistant_response: str
    sql_query: str


class ConversationCreate(BaseModel):
    title: str


class MessageListItem(BaseModel):
    id: str
    role: str
    content: str
    sql_query: str = None
    created_at: datetime


class MessageListResponse(BaseModel):
    conversation_id: str
    messages: list[MessageListItem]


@router.get("/conversations")
def list_conversations(token: str = None, db: Session = Depends(get_db)):
    """Lister les conversations de l'utilisateur"""
    
    user = get_current_user(token, db)
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).all()
    
    return {"conversations": conversations}


@router.get("/chat/conversations/{conversation_id}/messages", response_model=MessageListResponse)
def get_conversation_messages(
    conversation_id: str,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Récupérer tous les messages d'une conversation"""
    
    user = get_current_user(token, db)
    
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
    
    message_list = [
        MessageListItem(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sql_query=msg.sql_query,
            created_at=msg.created_at
        )
        for msg in messages
    ]
    
    return MessageListResponse(
        conversation_id=conversation_id,
        messages=message_list
    )


# ======== HELPER FUNCTIONS ========
def get_current_user(token: str, db: Session):
    """Extraire l'utilisateur du token JWT"""
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# ======== AUTH ENDPOINTS ========
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouvel utilisateur"""
    
    # Vérifier si l'utilisateur existe déjà
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")


@router.post("/chat/message", response_model=MessageResponse)
def chat_message(
    message_data: MessageRequest,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Envoyer un message et obtenir la réponse du RAG"""
    
    user = get_current_user(token, db)
    
    # Vérifier que la conversation appartient à l'utilisateur
    conversation = db.query(Conversation).filter(
        (Conversation.id == message_data.conversation_id) &
        (Conversation.user_id == user.id)
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Appeler votre RAG pipeline
        sql_query = generate_sql(message_data.message)
        results = execute_select_query(sql_query)
        
        # Humaniser la réponse
        if isinstance(results, list) and len(results) > 0:
            columns = list(results[0].keys()) if isinstance(results[0], dict) else []
            response = humanize_results(message_data.message, sql_query, results, columns)
        else:
            response = "Aucun résultat trouvé"
        
        # Sauvegarder les messages en DB
        user_msg = Message(
            id=str(uuid4()),
            conversation_id=conversation.id,
            role="user",
            content=message_data.message
        )
        
        assistant_msg = Message(
            id=str(uuid4()),
            conversation_id=conversation.id,
            role="assistant",
            content=response,
            sql_query=sql_query
        )
        
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
        
        return {
            "user_message": message_data.message,
            "assistant_response": response,
            "sql_query": sql_query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
