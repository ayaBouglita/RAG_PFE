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
    
    # Créer l'utilisateur avec le rôle "user" par défaut
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="user"  # Explicitement "user" et pas NULL
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role if user.role else "user",  # Fallback si NULL
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
            "email": user.email,
            "role": user.role if user.role else "user"  # Afficher "user" si NULL
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


# ======== ADMIN ROUTES ========
def get_current_user_from_token(authorization: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Extraire l'utilisateur du token JWT"""
    try:
        token = authorization.credentials
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except AttributeError:
        raise HTTPException(status_code=401, detail="No authorization header provided")


def verify_admin(user: User = Depends(get_current_user_from_token)):
    """Vérifier que l'utilisateur est admin"""
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.get("/api/admin/users")
def list_users(user: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Lister tous les utilisateurs (Admin only)"""
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role if u.role else "user",  # Afficher "user" si NULL
            "created_at": u.created_at
        }
        for u in users
    ]


@app.post("/api/admin/users")
def create_user_admin(
    data: UserCreate,
    user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Créer un utilisateur (Admin only)"""
    # Vérifier si l'utilisateur existe déjà
    existing = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")
    
    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
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


class UserUpdate(BaseModel):
    username: str = None
    email: str = None
    role: str = None


@app.put("/api/admin/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Modifier un utilisateur (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.username:
        # Vérifier que le nouveau username n'existe pas
        existing = db.query(User).filter(
            (User.username == data.username) & (User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username déjà utilisé")
        user.username = data.username
    
    if data.email:
        # Vérifier que le nouvel email n'existe pas
        existing = db.query(User).filter(
            (User.email == data.email) & (User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        user.email = data.email
    
    if data.role:
        if data.role not in ["admin", "user"]:
            raise HTTPException(status_code=400, detail="Rôle invalide")
        user.role = data.role
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role if user.role else "user",  # Afficher "user" si NULL
        "created_at": user.created_at
    }


@app.delete("/api/admin/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Supprimer un utilisateur (Admin only)"""
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


@app.get("/api/admin/stats")
def get_stats(admin: User = Depends(verify_admin), db: Session = Depends(get_db)):
    """Obtenir les statistiques système (Admin only)"""
    try:
        from sqlalchemy import func
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Getting admin stats...")
        
        # Total d'utilisateurs
        total_users = db.query(User).count()
        admin_count = db.query(User).filter(User.role == "admin").count()
        
        # Compter "user" ET les valeurs NULL (qui sont des utilisateurs normaux)
        user_count = db.query(User).filter(
            (User.role == "user") | (User.role.is_(None))
        ).count()
        
        logger.info(f"Stats: total={total_users}, admins={admin_count}, users={user_count}")
        
        # Inscriptions par date - simple version
        try:
            registrations = db.query(
                func.CAST(func.DATE(User.created_at), String).label("date"),
                func.count(User.id).label("count")
            ).group_by(func.CAST(func.DATE(User.created_at), String)).order_by(func.CAST(func.DATE(User.created_at), String)).all()
            
            registrations_by_date = [
                {"date": str(reg.date), "count": reg.count}
                for reg in registrations
            ]
            logger.info(f"Registrations by date: {registrations_by_date}")
        except Exception as e:
            logger.error(f"Error getting registrations by date: {e}")
            # Si l'erreur DATE pose problème, essayer une approche alternative
            try:
                all_users = db.query(User).all()
                registrations_by_date = []
                # Group by date manually
                from collections import defaultdict
                from datetime import date
                
                dates_dict = defaultdict(int)
                for user in all_users:
                    if user.created_at:
                        user_date = user.created_at.date() if hasattr(user.created_at, 'date') else user.created_at
                        dates_dict[str(user_date)] += 1
                
                registrations_by_date = [
                    {"date": date_str, "count": count}
                    for date_str, count in sorted(dates_dict.items())
                ]
            except Exception as e2:
                logger.error(f"Error in fallback registrations: {e2}")
                registrations_by_date = []
        
        return {
            "total_users": total_users,
            "admin_count": admin_count,
            "user_count": user_count,
            "registrations_by_date": registrations_by_date
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
