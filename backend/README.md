# 🚀 RAG Intelligence API - Phase 1

API FastAPI simple pour votre système RAG avec authentification et gestion des conversations.

---

## ⚡ Démarrage Rapide

### 1. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuration

Copier `.env.example` en `.env` et vérifier:
```
SQL_SERVER=Malek
SQL_DATABASE=DW_Energie
SECRET_KEY=dev-secret-key-change-this-in-production
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral
```

### 3. S'assurer que OLLAMA est lancé

```bash
ollama serve
# Dans un autre terminal:
ollama run mistral
```

### 4. Lancer l'API

```bash
python app.py
```

Ou:
```bash
uvicorn app:app --reload
```

L'API est accessible sur: **http://localhost:8000**

Documentation interactive: **http://localhost:8000/docs**

---

## 📡 Endpoints

### 1️⃣ Créer un compte

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "MyPassword123"
}
```

Réponse:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "message": "Utilisateur créé"
}
```

---

### 2️⃣ Se connecter

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "MyPassword123"
}
```

Réponse:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

**Garder le token `access_token` pour les prochains appels!**

---

### 3️⃣ Créer une conversation

```http
POST /api/v1/chat/conversations
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "title": "Consommation de Fuel 2024"
}
```

Réponse:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Consommation de Fuel 2024",
  "created_at": "2024-01-15T10:30:00"
}
```

**Garder le `id` pour l'endpoint suivant!**

---

### 4️⃣ Lister ses conversations

```http
GET /api/v1/chat/conversations
Authorization: Bearer YOUR_TOKEN_HERE
```

Réponse:
```json
{
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Consommation de Fuel 2024",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

### 5️⃣ Envoyer un message (Endpoint Principal)

```http
POST /api/v1/chat/message
Authorization: Bearer YOUR_TOKEN_HERE
Content-Type: application/json

{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Quelle est la consommation totale de fuel en 2024?"
}
```

Réponse:
```json
{
  "user_message": "Quelle est la consommation totale de fuel en 2024?",
  "assistant_response": "La consommation totale de fuel en 2024 est de 5000 tonnes.",
  "sql_query": "SELECT SUM(quantity) FROM fuel_consumption WHERE year = 2024;"
}
```

---

## 🧪 Tester avec curl

### Créer un compte
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"pass123"}'
```

### Se connecter
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123"}'
```

### Créer conversation
```bash
curl -X POST http://localhost:8000/api/v1/chat/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
```

### Envoyer un message
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"YOUR_CONV_ID","message":"Test question?"}'
```

---

## 📁 Structure des fichiers

```
backend/
├── app.py             # Application FastAPI principale
├── database.py        # Models SQLAlchemy + SQLServer connection
├── auth.py            # JWT + Password hashing
├── requirements.txt   # Dépendances Python
├── .env.example       # Template des variables d'environnement
└── .env               # Variables d'environnement réelles (à créer)
```

---

## 🗄️ Base de données

3 tables créées automatiquement:
- `app_users` - Utilisateurs
- `app_conversations` - Conversations
- `app_messages` - Messages de conversations

---

## 🔐 Authentification

JWT Token valide pendant 30 minutes. Pour chaque appel protégé, ajouter le header:

```
Authorization: Bearer YOUR_TOKEN
```

---

## ✅ Checklist - Validation Phase 1

- [ ] API démarre sans erreurs
- [ ] Swagger accessible sur `/docs`
- [ ] Créer un compte fonctionne
- [ ] Login retourne un token
- [ ] Créer une conversation fonctionne
- [ ] Envoyer un message retourne la réponse RAG
- [ ] Messages sauvegardés en SQL Server

---

## 🐛 Troubleshooting

### Erreur: "Connection refused"
- Vérifier que SQL Server est accessible
- Vérifier `SQL_SERVER` et `SQL_DATABASE` dans `.env`

### Erreur: "No module named 'ask_database'"
- Vérifier que le pipeline RAG est dans `06_pipeline/`
- Vérifier les imports dans `app.py`

### Erreur: "Token invalid"
- Le token a peut-être expiré (30 min)
- Refaire un login

### Erreur OLLAMA
- Vérifier qu'OLLAMA est lancé: `ollama serve`
- Vérifier l'URL dans `.env`

---

## 📝 Notes

- Cette version est SIMPLE, pas optimisée
- Pas de gestion d'erreurs avancée
- Pas de rate limiting
- À enrichir dans les prochaines phases
