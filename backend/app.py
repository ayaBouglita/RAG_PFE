from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import os
import sys
import pandas as pd
from dotenv import load_dotenv

from database import create_tables, get_db, User, Conversation, Message
from auth import hash_password, verify_password, create_access_token, verify_token

load_dotenv()

# Ajouter le pipeline RAG au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '06_pipeline'))
from ask_database import humanize_results
from generate_sql_ollama import generate_sql
from run_query import execute_select_query

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


# ======== STARTUP ========
@app.on_event("startup")
def startup():
    create_tables()
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


@app.post("/api/v1/chat/message", dependencies=[Depends(security)])
def chat_message(
    data: MessageRequest,
    user: User = Depends(get_token_user),
    db = Depends(get_db)
):
    """Envoyer un message et obtenir la réponse"""
    
    # Vérifier que la conversation appartient à l'utilisateur
    conv = db.query(Conversation).filter(
        (Conversation.id == data.conversation_id) & (Conversation.user_id == user.id)
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Appeler RAG pipeline
        sql_result = generate_sql(data.message)
        sql_query = sql_result["sql"]
        
        # Si c'est une réponse textuelle (pas SQL)
        if sql_result["is_text_response"]:
            response = sql_query
        else:
            # Exécuter la requête SQL (retourne un DataFrame)
            df_results = execute_select_query(sql_query)
            
            # Humaniser les résultats
            if not df_results.empty:
                # Convertir DataFrame en list of dicts - remplace NaN par None pour JSON serialization
                results_list = df_results.where(pd.notna(df_results), None).to_dict('records')
                columns = list(df_results.columns)
                response = humanize_results(data.message, sql_query, results_list, columns)
            else:
                response = "Aucun résultat trouvé"
        
        # Sauvegarder
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
            sql_query=sql_query
        )
        
        db.add(msg_user)
        db.add(msg_assistant)
        db.commit()
        
        return {
            "user_message": data.message,
            "assistant_response": response,
            "sql_query": sql_query
        }
        
    except Exception as e:
        import traceback
        print(f" Error in chat_message: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur pipeline: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
