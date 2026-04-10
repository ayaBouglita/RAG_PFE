# 🚀 GUIDE DE DÉMARRAGE - APPLICATION RAG COMPLÈTE

## 📌 Vue d'ensemble

Application complète d'un Assistant IA avec:
- ✅ Backend FastAPI + RAG Pipeline
- ✅ Frontend Vue 3
- ✅ Authentification JWT
- ✅ Mistral via Ollama (local)
- ✅ Database SQL Server

---

## 🛠️ Prérequis Systèmes

- Node.js 16+ (pour le frontend)
- Python 3.9+ (pour le backend)
- SQL Server (running)
- Ollama + Mistral 7B (running sur localhost:11434)

---

## 📋 Étape 1: Préparer l'Environnement Backend

### 1.1 Créer l'environnement virtuel (optionnel, déjà fait)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
```

### 1.2 Variables d'environnement
Créer/vérifier `.env` dans `/backend`:
```env
SQL_SERVER=Malek
SQL_DATABASE=DW_Energie
SECRET_KEY=votre-clé-secrète-prod
```

### 1.3 Démarrer le backend
```bash
cd backend
python app.py
```

✅ **Backend prêt** quand vous voyez:
```
📊 Connecting to SQL Server: Malek/DW_Energie
 API démarrée - Tables OK
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 📋 Étape 2: Préparer l'Environnement Frontend

### 2.1 Installation (déjà fait)
```bash
cd frontend
npm install
```

### 2.2 Vérifier les variables d'environnement
Fichier `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_API_PREFIX=/api/v1
```

### 2.3 Démarrer le frontend
```bash
cd frontend
npm run dev
```

✅ **Frontend prêt** quand vous voyez:
```
VITE v5.4.21 ready in 1234 ms
➜  Local:   http://localhost:5173/
```

---

## 🚀 Lancer l'Application Complète

### Terminal 1: Backend
```bash
cd c:\Users\malek\RAG_PFE\backend
python app.py
```

### Terminal 2: Frontend  
```bash
cd c:\Users\malek\RAG_PFE\frontend
npm run dev
```

### Vérifier Ollama
```bash
curl http://localhost:11434/api/tags
```
Doit retourner le modèle Mistral disponible.

---

## 🌐 URLs d'Accès

| Service | URL | Notes |
|---------|-----|-------|
| **Frontend** | http://localhost:5173 | Application web |
| **Backend API** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Ollama** | http://localhost:11434 | Modèle local |

---

## 📝 Premiers Tests

### Test 1: Accéder au Frontend
1. Ouvrir http://localhost:5173
2. Devrais voir l'écran de login

### Test 2: S'inscrire
1. Cliquer sur "Créer un compte"
2. Remplir:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test1234!`
3. Cliquer "Créer mon compte"
4. Devrais être redirigé vers login après 2 secondes

### Test 3: Se Connecter
1. Remplir credentials du test précédent
2. Cliquer "Se connecter"
3. Devrais arriver sur page Chat

### Test 4: Utiliser le Chat
1. Cliquer sur "+ Nouvelle" conversation
2. Nommer la conversation: "Test RAG"
3. Envoyer un message: `Quel est le volume total de fuel?`
4. Attendre la réponse RAG
5. Devrais voir: `"Le volume total de fuel est de 11 036 tonnes."`

---

## 🔍 Dépannage

### ❌ Erreur: "Cannot connect to backend"

**Cause:** Backend non lancé
**Solution:**
```bash
cd backend
python app.py
```

### ❌ Erreur: "CORS policy"

**Cause:** Backend CORS pas configuré
**Solution:** Vérifier `app.py` lignes 24-30

### ❌ Erreur: "Invalid credentials"

**Cause:** RAS utilisateur/mot de passe
**Solution:** S'inscrire d'abord si nouveau compte

### ❌ Erreur: "SQL Server connection failed"

**Cause:** SQL Server pas lancé
**Solution:** Lancer SQL Server ou vérifier `.env`

### ❌ Erreur: "Ollama connection timeout"

**Cause:** Ollama pas lancé
**Solution:**
```bash
ollama serve mistral
```

### Vérifier les Logs

**Backend:**
```bash
# Logs dans console lors du démarrage
# Erreurs HTTP
```

**Frontend:**
```bash
# Ouvrir Developer Tools: F12
# Onglet Console
# Onglet Network
```

---

## 🎯 Architecture Vérifiée

```
FRONTEND (Vue 3)
    ↓ HTTP + JWT
BACKEND (FastAPI)
    ↓ SQL
DATABASE (DW_Energie)
    ↓
RAG PIPELINE
    ↓ query
OLLAMA (Mistral)
    ↓
RESPONSE
```

---

## 📊 Test API Directement

### Enregistrement
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testapi",
    "email": "api@test.com",
    "password": "Test1234!"
  }'
```

### Connexion
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testapi",
    "password": "Test1234!"
  }'
```

Retourne:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testapi",
    "email": "api@test.com"
  }
}
```

---

## 🎓 Fichiers Importants

| Fichier | Utilité |
|---------|---------|
| `backend/app.py` | Application FastAPI principale |
| `backend/database.py` | Modèles SQLAlchemy + connection |
| `backend/auth.py` | JWT + Password hashing |
| `backend/routes.py` | Endpoints API |
| `06_pipeline/ask_database.py` | Orchestration RAG |
| `frontend/src/main.js` | Entry point Vue |
| `frontend/src/router.js` | Navigation routes |
| `frontend/src/services/api.js` | Client HTTP |
| `frontend/src/stores/auth.js` | État authentification |
| `frontend/src/stores/chat.js` | État chat |

---

## 📈 Progression

- ✅ Phase 1: Backend RAG fonctionnel
- ✅ Phase 2: Frontend Vue 3 complète
- ⏭️ Phase 3: Déploiement (optionnel)

---

## 🚨 Checklist de Démarrage

- [ ] Backend: `python backend/app.py` lancé
- [ ] Frontend: `npm run dev` lancé
- [ ] Ollama: `ollama serve` lancé
- [ ] SQL Server: fonctionnel
- [ ] Terminal 1 backend: pas d'erreurs
- [ ] Terminal 2 frontend: pas d'erreurs
- [ ] http://localhost:5173 accessible
- [ ] http://localhost:8000/health retourne `{"status": "ok"}`

---

## 💡 Tips & Tricks

**Développement rapide:**
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && npm run dev

# Modifier les fichiers = reload automatique
```

**Debug mode:**
```javascript
// Dans src/main.js
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err, info)
}
```

**Voir les requêtes API:**
- Firefox/Chrome: F12 → Network tab
- Backend logs: console du terminal Python

---

## 📞 Support

Si problème pendant le démarrage:
1. Vérifier tous les prérequis
2. Vérifier les logs (console)
3. Vérifier les .env files
4. Vérifier les ports (8000, 5173, 11434)
5. Redémarrer les services

---

**Status: ✅ Ready to Launch!**
