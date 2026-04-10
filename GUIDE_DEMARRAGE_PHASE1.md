# 🚀 GUIDE DÉMARRAGE - PHASE 1

## Qu'avez-vous maintenant?

✅ Backend FastAPI simple avec:
- Authentification JWT
- 3 tables SQL Server (Users, Conversations, Messages)
- 5 endpoints pour chat + authentification
- Intégration RAG existante

---

## ⚡ Étapes Pour Lancer

### Étape 1: Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

**Temps estimé**: 2-3 minutes

---

### Étape 2: Vérifier la configuration

Ouvrir `backend/.env` et vérifier:

```env
SQL_SERVER=Malek           ← Votre serveur SQL
SQL_DATABASE=DW_Energie    ← Votre base de données
SECRET_KEY=...             ← À laisser comme c'est pour dev
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral
```

**Si vous devez le changer**: Éditer `.env`

---

### Étape 3: Lancer OLLAMA

Dans un terminal:
```bash
ollama serve
```

**Vérifier** qu'il dit: `Listening on 127.0.0.1:11434`

---

### Étape 4: Lancer l'API

Dans un **autre** terminal:
```bash
cd backend
python app.py
```

**Attendre** que ça dise:
```
✅ API démarrée - Tables OK
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Étape 5: Tester l'API

#### Option 1: Via Swagger (Interface graphique)

Ouvrir dans le navigateur: **http://localhost:8000/docs**

Vous verrez une interface pour tester les endpoints directement.

#### Option 2: Avec le script de test

Dans un **troisième** terminal:
```bash
cd backend
python test_api.py
```

Ça va automatiquement:
1. Créer un compte
2. Se connecter (obtenir token)
3. Créer une conversation
4. Lister les conversations
5. Envoyer un message et obtenir la réponse

---

## 📡 Les 5 Endpoints

| # | Méthode | Route | Authentification | Utilité |
|---|---------|-------|------------------|---------|
| 1 | POST | `/api/v1/auth/register` | ❌ | Créer un compte |
| 2 | POST | `/api/v1/auth/login` | ❌ | Se connecter (obtenir token) |
| 3 | POST | `/api/v1/chat/conversations` | ✅ | Créer une conversation |
| 4 | GET | `/api/v1/chat/conversations` | ✅ | Lister ses conversations |
| 5 | POST | `/api/v1/chat/message` | ✅ | Envoyer un message |

**Les endpoints avec ✅ ont besoin du token JWT!**

---

## 🔐 Comment utiliser le token JWT

### 1. Se connecter d'abord
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

Réponse:
```json
{
  "access_token": "eyJhbGc...",  ← Copier ce token
  "token_type": "bearer"
}
```

### 2. Utiliser le token pour les endpoints protégés
```bash
curl -X GET http://localhost:8000/api/v1/chat/conversations \
  -H "Authorization: Bearer eyJhbGc..."  ← Le token ici
```

---

## 🗄️ Que se passe-t-il quand vous lancez?

1️⃣ **App.py démarre** → Crée les 3 tables dans SQL Server si elles n'existent pas

2️⃣ **Utilisateur crée un compte** → Enregistré en db

3️⃣ **Utilisateur se connecte** → JWT token généré (valide 30 min)

4️⃣ **Utilisateur crée une conversation** → ID généré, sauvegardé en DB

5️⃣ **Utilisateur envoie un message** → 
   - Appelle votre RAG pipeline
   - Génère SQL avec OLLAMA
   - Exécute SQL sur SQL Server
   - Retourne la réponse humanisée
   - Sauvegarde tout en DB

---

## ✅ Checklist - Avant de passer à Phase 2

- [ ] API démarre sans erreurs
- [ ] http://localhost:8000/docs accessible
- [ ] Créer compte fonctionne
- [ ] Login retourne un token
- [ ] Créer conversation fonctionne
- [ ] Lister conversations fonctionne
- [ ] **Envoyer message retourne réponse RAG** ← Le plus important
- [ ] Messages sauvegardés en SQL Server
- [ ] `test_api.py` réussit

---

## 🐛 Troubleshooting Rapide

### L'API ne démarre pas
```
Erreur: "Connection refused to SQL Server"
```
**Solution**: Vérifier `SQL_SERVER` et `SQL_DATABASE` dans `.env`

### Erreur "No module found"
```
Erreur: "ModuleNotFoundError: No module named 'ask_database'"
```
**Solution**: Vérifier que `06_pipeline/` existe avec vos fichiers

### OLLAMA Error
```
Erreur: "Connection refused to OLLAMA"
```
**Solution**: Lancer `ollama serve` dans un autre terminal avant l'API

### Token invalide
```
Erreur: "Invalid token"
```
**Solution**: Le token a expiré (30 min). Refaire un login.

---

## 📝 Structure créée

```
backend/
├── app.py                 ← Start here: python app.py
├── database.py            ← Models SQLAlchemy + SQL Server connection
├── auth.py                ← JWT + Password hashing
├── test_api.py            ← Tests automatiques
├── requirements.txt       ← Dépendances
├── .env                   ← Configuration (à personnaliser)
├── .env.example           ← Template
└── README.md              ← Documentation complète
```

---

## 🎯 Qu'est-ce qui fonctionne maintenant?

✅ **Authentification complète** - Register/Login avec JWT tokens valides 30 min

✅ **Gestion des conversations** - Créer, lister

✅ **Chat avec RAG** - Question → SQL généré → Réponse humanisée → Sauvegardé en DB

✅ **Multi-utilisateurs** - Chaque utilisateur a ses propres conversations

✅ **Mémoire des messages** - Toutes les Q/A sauvegardées en DB

---

## ✅ Backend Opérationnel

L'API est prête pour être intégrée à tout type d'interface (web, mobile, CLI, etc.)

---

**L'API est maintenant prête à l'emploi!** 🚀
