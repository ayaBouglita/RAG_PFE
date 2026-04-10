# 🏗️ ARCHITECTURE PHASE 1 - Expliquée Simplement

## Ce qui a été créé

Une API web simple qui permet à plusieurs utilisateurs d'utiliser votre système RAG via une interface web.

---

## Avant Phase 1 (Ce que vous aviez)

```
Terminal
  ↓
ask_database.py (script)
  ↓
RAG → SQL Server
  ↓
Résultat → Terminal
```

**Problème**: UN utilisateur à la fois, pas d'historique, pas d'interface.

---

## Après Phase 1 (Maintenant)

```
Client 1 (Web)            Client 2 (Web)           Client 3 (Web)
    ↓                         ↓                        ↓
        ← JWT Token ←  FastAPI Backend  → JWT Token →
              ↑              ↓              ↑
              │        3 Tables           │
              └─→  SQL Server (DB) ←──────┘
                        ↓
                    RAG Pipeline
                   (votre code)
                        ↓
    ← Réponse + Historique ←
```

**Avantage**: Plusieurs utilisateurs simultanément, chacun avec son historique.

---

## Comment ça marche?

### Step 1️⃣: Utilisateur crée un compte

```python
# Dans app.py
@app.post("/api/v1/auth/register")
def register(data: UserCreate):
    # 1. Vérifier que l'utilisateur n'existe pas
    # 2. Hasher le password (Argon2)
    # 3. Ajouter en table SQL Server "app_users"
    # 4. Retourner succès
```

**SQL Server**:
```sql
INSERT INTO app_users (username, email, password_hash)
VALUES ('john_doe', 'john@example.com', '$argon2id$...')
```

---

### Step 2️⃣: Utilisateur se connecte

```python
# Dans app.py
@app.post("/api/v1/auth/login")
def login(data: LoginRequest):
    # 1. Chercher l'utilisateur dans DB par username
    # 2. Comparer le password fourni avec le hash en DB
    # 3. Si match: créer un JWT token
    # 4. Retourner le token (valide 30 minutes)
```

**JWT Token contient**:
```json
{
  "user_id": 1,
  "exp": 2024-01-15T11:30:00
}
```

---

### Step 3️⃣: Utilisateur crée une conversation

```python
# Dans app.py
@app.post("/api/v1/chat/conversations")
def create_conversation(data, user: User = Depends(get_token_user)):
    # 1. Vérifier le JWT token (vient de get_token_user)
    # 2. Créer une conversation liée à user.id
    # 3. Sauvegarder en table "app_conversations"
    # 4. Retourner l'ID de la conversation
```

**SQL Server**:
```sql
INSERT INTO app_conversations (id, user_id, title)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 1, 'Mon titre')
```

---

### Step 4️⃣: Utilisateur envoie un message ⭐ (Le plus important)

```python
# Dans app.py
@app.post("/api/v1/chat/message")
def chat_message(data, user: User = Depends(get_token_user)):
    # 1. Vérifier le token
    # 2. Chercher la conversation (et vérifier qu'elle appartient à l'user)
    # 3. Appeler votre RAG pipeline avec la question
    # 4. Exécuter la SQL sur SQL Server
    # 5. Humaniser la réponse
    # 6. Sauvegarder DEUX messages en DB:
    #    - Message utilisateur
    #    - Message assistant (avec SQL query)
    # 7. Retourner la réponse
```

**Étapes détaillées**:

```
1. Message reçu: "Quelle est la consommation de fuel?"

2. Appeler generate_sql() → Génère: 
   "SELECT SUM(quantity) FROM fuel WHERE year=2024"

3. Appeler execute_select_query() → Exécute sur SQL Server →
   Results: [{"sum": 5000}]

4. Appeler humanize_results() → Utilise OLLAMA pour transformer en:
   "La consommation totale de fuel était 5000 tonnes"

5. Sauvegarder dans "app_messages" (2 lignes):
   - role: "user", content: "Quelle est la consommation de fuel?"
   - role: "assistant", content: "La consommation...5000 tonnes", sql_query: "SELECT SUM..."

6. Retourner au client
```

---

## 📁 Les 3 Tables SQL Server Créées

### Table 1: app_users
```sql
CREATE TABLE app_users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),    ← Contient Argon2 hash
    created_at DATETIME DEFAULT GETUTCDATE()
)
```

**Exemple de ligne**:
```
id=1, username='john', email='john@ex.com', password_hash='$argon2id$...', created_at='2024-01-15 10:00:00'
```

---

### Table 2: app_conversations
```sql
CREATE TABLE app_conversations (
    id VARCHAR(36) PRIMARY KEY,    ← UUID
    user_id INT FOREIGN KEY → app_users(id),
    title VARCHAR(255),
    created_at DATETIME DEFAULT GETUTCDATE()
)
```

**Exemple de ligne**:
```
id='550e8400-e29b-41d4-a716-446655440000'
user_id=1
title='Consommation de Fuel'
created_at='2024-01-15 10:05:00'
```

---

### Table 3: app_messages
```sql
CREATE TABLE app_messages (
    id VARCHAR(36) PRIMARY KEY,    ← UUID
    conversation_id VARCHAR(36) FOREIGN KEY → app_conversations(id),
    role VARCHAR(20),              ← 'user' ou 'assistant'
    content TEXT,                  ← Le message complet
    sql_query TEXT,                ← La SQL générée (NULL si role='user')
    created_at DATETIME DEFAULT GETUTCDATE()
)
```

**Exemple de lignes**:
```
# Message 1 (utilisateur)
id='550e8400-...-001'
conversation_id='550e8400-...-000'
role='user'
content='Quelle est la consommation de fuel?'
sql_query=NULL
created_at='2024-01-15 10:10:00'

# Message 2 (assistant)
id='550e8400-...-002'
conversation_id='550e8400-...-000'
role='assistant'
content='La consommation totale de fuel en 2024 est de 5000 tonnes.'
sql_query='SELECT SUM(quantity) FROM fuel WHERE year = 2024;'
created_at='2024-01-15 10:10:02'
```

---

## 🔐 Authentification JWT - Comment ça marche?

### 1️⃣ Utilisateur envoie credentials

```
POST /login
{
  "username": "john",
  "password": "MyPass123"
}
```

### 2️⃣ Server génère un token

```python
# Dans auth.py
token = jwt.encode(
    {"user_id": 1, "exp": datetime.utcnow() + timedelta(minutes=30)},
    SECRET_KEY,
    algorithm="HS256"
)
# Résultat: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3️⃣ Client reçoit le token

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4️⃣ Client l'utilise pour les requêtes protégées

```
GET /chat/conversations
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5️⃣ Server vérifie le token

```python
# Dans auth.py
payload = jwt.decode(token, SECRET_KEY, algorithm="HS256")
# Récupère: {"user_id": 1, "exp": ...}
user_id = payload["user_id"]
# Cherche l'utilisateur dans DB
```

### 6️⃣ Retourne les données de cet utilisateur

---

## 🛡️ Sécurité minimale

### Passwords
- Hashés avec **Argon2** (très sécurisé)
- JAMAIS stockés en plain text
- Vérification: comparer l'hash du password fourni avec l'hash en DB

### Tokens
- Valides seulement **30 minutes**
- Contiennent user_id + expiration (exp)
- Signés avec SECRET_KEY
- Si SECRET_KEY change → tous les tokens invalides

### Authentification sur chaque endpoint protégé
- Header `Authorization: Bearer TOKEN` obligatoire
- Token vérifié avant de retourner les données
- Utilisateur peut seulement accéder à SES conversations

---

## 📊 Flow Complet: Un Utilisateur Envoie un Message

```
1. Client envoie:
   POST /chat/message
   Authorization: Bearer TOKEN
   {"conversation_id": "...", "message": "Question?"}

2. Server:
   a) Vérifie le JWT token
   b) Récupère user_id du token
   c) Cherche la conversation (et vérifie qu'elle appartient à user_id)
   d) Appelle generate_sql("Question?") → "SELECT ..."
   e) Appelle execute_select_query("SELECT ...") → [Results]
   f) Appelle humanize_results(...) → "Réponse..."
   g) Sauvegarde 2 messages en DB
   h) Retourne {"user_message": "Question?", "assistant_response": "Réponse...", "sql_query": "SELECT ..."}

3. Client affiche la réponse

4. Prochaine fois, l'utilisateur peut relire son historique
   GET /chat/conversations/ID/messages → Retourne tous les messages
```

---

## ✨ Résumé simple

**Phase 1 = Une API qui dit "NON" aux utilisateurs non-authentifiés et "OUI" à ceux qui sont loggés**

- Chaque utilisateur a son espace privé
- Chaque conversation est liée à un utilisateur
- Chaque message est horodaté et sauvegardé
- Votre RAG pipeline reste exactement pareil, juste appelé via l'API

---

## ✅ Architecture terminée

Le système backend est complet et fonctionnel.
- Se connecte à cette API
- Affiche les conversations
- Permet de chatter en direct
- Affiche l'historique

Mais d'abord: **Testez Phase 1!**
