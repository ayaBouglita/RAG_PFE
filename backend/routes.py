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
from generate_chart import ChartDataBuilder
from detect_temporal import detect_chart_type, ChartType
import json

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
    role: str


class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    role: str = None


class UserFullResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime


class AdminStatsResponse(BaseModel):
    total_users: int
    admin_count: int
    user_count: int
    registrations_by_date: list


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
    chart_config: dict = None


class ConversationCreate(BaseModel):
    title: str


class MessageListItem(BaseModel):
    id: str
    role: str
    content: str
    sql_query: str = None
    chart_config: dict = None
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
            chart_config=json.loads(msg.chart_config) if msg.chart_config else None,
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


def get_admin_user(token: str, db: Session):
    """Extraire et vérifier que c'est un administrateur"""
    user = get_current_user(token, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
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
    
    # Créer le nouvel utilisateur avec le rôle "user" par défaut
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }


@router.post("/login", response_model=LoginResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    """Authentifier un utilisateur et retourner un token"""
    
    user = db.query(User).filter(User.username == creds.username).first()
    
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    token = create_access_token({"user_id": user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


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
        
        # Générer le chart_config
        chart_config = None
        chart_config_str = None
        if isinstance(results, list) and len(results) > 0:
            try:
                # Détecter le type de graphique approprié
                chart_type, metadata = detect_chart_type(message_data.message)
                title = metadata.get("chart_title", "Répartition des données")
                
                # Générer le graphique selon le type détecté
                if chart_type == ChartType.BAR:
                    chart_config = ChartDataBuilder.build_bar_chart(
                        data=results,
                        title=title,
                        unit="kWh"
                    )
                elif chart_type == ChartType.LINE:
                    chart_config = ChartDataBuilder.build_line_chart(
                        data=results,
                        title=title,
                        unit="kWh"
                    )
                else:  # PIE ou NONE par défaut
                    chart_config = ChartDataBuilder.build_pie_chart(
                        data=results,
                        title=title,
                        unit="kWh"
                    )
                chart_config_str = json.dumps(chart_config, ensure_ascii=False)
            except Exception as chart_err:
                print(f"⚠️  Impossible de générer le graphique: {str(chart_err)}")
        
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
            sql_query=sql_query,
            chart_config=chart_config_str
        )
        
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
        
        return {
            "user_message": message_data.message,
            "assistant_response": response,
            "sql_query": sql_query,
            "chart_config": chart_config
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ======== ADMIN ENDPOINTS ========
@router.get("/admin/users", response_model=list[UserFullResponse])
def list_users(token: str = None, db: Session = Depends(get_db)):
    """Lister tous les utilisateurs (Admin only)"""
    admin = get_admin_user(token, db)
    
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at
        }
        for u in users
    ]


@router.post("/admin/users", response_model=UserFullResponse)
def create_user_admin(
    user_data: UserCreate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Créer un utilisateur (Admin only)"""
    admin = get_admin_user(token, db)
    
    # Vérifier si l'utilisateur existe déjà
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "created_at": new_user.created_at
    }


@router.put("/admin/users/{user_id}", response_model=UserFullResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Modifier un utilisateur (Admin only)"""
    admin = get_admin_user(token, db)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.username:
        # Vérifier que le nouveau username n'existe pas
        existing = db.query(User).filter(
            (User.username == user_data.username) & (User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username déjà utilisé")
        user.username = user_data.username
    
    if user_data.email:
        # Vérifier que le nouvel email n'existe pas
        existing = db.query(User).filter(
            (User.email == user_data.email) & (User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        user.email = user_data.email
    
    if user_data.role:
        if user_data.role not in ["admin", "user"]:
            raise HTTPException(status_code=400, detail="Rôle invalide")
        user.role = user_data.role
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at
    }


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Supprimer un utilisateur (Admin only)"""
    admin = get_admin_user(token, db)
    
    # Empêcher la suppression de l'admin lui-même
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Impossible de supprimer votre propre compte")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Supprimer les conversations et messages associés
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    for conv in conversations:
        db.query(Message).filter(Message.conversation_id == conv.id).delete()
    
    db.query(Conversation).filter(Conversation.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.get("/admin/stats", response_model=AdminStatsResponse)
def get_stats(token: str = None, db: Session = Depends(get_db)):
    """Obtenir les statistiques système (Admin only)"""
    admin = get_admin_user(token, db)
    
    # Total d'utilisateurs
    total_users = db.query(User).count()
    admin_count = db.query(User).filter(User.role == "admin").count()
    user_count = db.query(User).filter(User.role == "user").count()
    
    # Inscriptions par date
    from sqlalchemy import func
    registrations = db.query(
        func.DATE(User.created_at).label("date"),
        func.count(User.id).label("count")
    ).group_by(func.DATE(User.created_at)).order_by(func.DATE(User.created_at)).all()
    
    registrations_by_date = [
        {"date": str(reg.date), "count": reg.count}
        for reg in registrations
    ]
    
    return {
        "total_users": total_users,
        "admin_count": admin_count,
        "user_count": user_count,
        "registrations_by_date": registrations_by_date
    }
