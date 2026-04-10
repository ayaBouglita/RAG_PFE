# Frontend RAG Assistant - Vue 3 Application

## Overview
Frontend web moderne pour l'Assistant IA basé sur RAG (Retrieval-Augmented Generation) utilisant Mistral via Ollama.

## Features
✅ **Authentification**
- Inscription (Register)
- Connexion (Login)  
- Gestion JWT Token
- Stockage local du token

✅ **Chat Interface**
- Créer/gérer des conversations
- Envoyer des messages à l'assistant IA
- Affichage dynamique des réponses
- Historique SQL généré

✅ **Design**
- Responsive (desktop/mobile)
- Couleurs du logo société (#006EC3, #12239E, #7FBF2A, #4C9CDA, #8BAFCE)
- Tailwind CSS
- Mode sombre/light ready

## Tech Stack
- **Vue 3** - Framework UI
- **Vite** - Build tool
- **Vue Router** - Navigation
- **Pinia** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Styling

## Installation

### 1. Prérequis
- Node.js 16+
- npm ou yarn
- Backend FastAPI en cours d'exécution (localhost:8000)

### 2. Installation des dépendances
```bash
cd frontend
npm install
```

### 3. Configuration
Créer/modifier `.env` :
```env
VITE_API_URL=http://localhost:8000
VITE_API_PREFIX=/api/v1
```

### 4. Lancer en développement
```bash
npm run dev
```
L'application sera disponible à: **http://localhost:5173**

### 5. Build pour production
```bash
npm run build
npm run preview
```

## Structure du Projet

```
frontend/
├── public/              # Assets statiques
├── src/
│   ├── assets/         # CSS, images
│   │   └── main.css    # Tailwind styles
│   ├── components/     # Composants Vue réutilisables
│   │   ├── ChatMessage.vue   # Affichage d'un message
│   │   ├── Sidebar.vue       # Barre latérale conversations
│   │   └── Header.vue        # En-tête du chat
│   ├── pages/          # Pages principales
│   │   ├── LoginPage.vue     # Page connexion
│   │   ├── RegisterPage.vue  # Page inscription
│   │   └── ChatPage.vue      # Page chat principale
│   ├── services/       # Services API
│   │   └── api.js      # Client HTTP + endpoints
│   ├── stores/         # Pinia stores (état global)
│   │   ├── auth.js     # État authentification
│   │   └── chat.js     # État chat
│   ├── App.vue         # Root component
│   ├── main.js         # Entry point
│   └── router.js       # Configuration Vue Router
├── index.html          # HTML principal
├── .env               # Variables d'environnement
├── tailwind.config.js # Config Tailwind
├── vite.config.js     # Config Vite
└── package.json       # Dépendances
```

## API Endpoints Utilisés

### Authentication
- `POST /api/v1/auth/register` - Créer un compte
- `POST /api/v1/auth/login` - Se connecter (retourne JWT token)

### Chat
- `POST /api/v1/chat/conversations` - Créer une conversation
- `GET /api/v1/chat/conversations` - Lister les conversations
- `POST /api/v1/chat/message` - Envoyer un message

## Flow d'Authentification

1. Utilisateur s'inscrit/se connecte
2. Backend retourne `access_token` (JWT)
3. Frontend stocke le token dans `localStorage`
4. À chaque requête, le token est envoyé dans le header `Authorization: Bearer <token>`
5. Si token expiré → redirection vers login

## Couleurs de la Marque
```
Primary 600: #12239E (Bleu foncé)
Primary 500: #006EC3 (Bleu principal)
Primary 400: #4C9CDA (Bleu clair)
Accent 500: #7FBF2A (Vert clair)
Accent 400: #8BAFCE (Bleu gris)
```

## Gestion de l'État

### Auth Store
```javascript
{
  user: { id, username, email },
  token: string,
  isAuthenticated: boolean
}
```

### Chat Store
```javascript
{
  conversations: [],
  currentConversation: object,
  messages: [],
  loading: boolean
}
```

## Dépannage

### Issues Courants

❌ **Erreur CORS**
→ Vérifier que le backend a CORS activé
→ Vérifier `VITE_API_URL` dans `.env`

❌ **Token expiré**
→ Réquête retourne 401
→ Frontend redirige vers `/login`

❌ **Conversations n'apparaissent pas**
→ Vérifier que l'utilisateur est connecté
→ Vérifier le token dans localStorage

## Performance

- Lazy loading des components
- Virtual scrolling pour les longs historiques (future feature)
- Compression des assets
- Cache du service worker (future feature)

## Prochaines Améliorations

- [ ] Dark mode
- [ ] Édition des messages
- [ ] Suppression de conversations
- [ ] Upload de fichiers
- [ ] Exportation du chat
- [ ] Intégration WebSocket pour temps réel
- [ ] Recherche dans les conversations
- [ ] Avatar utilisateur personnalisé

## Support

Pour des problèmes ou suggestions:
1. Vérifier les logs du navigateur (F12)
2. Vérifier les logs du backend (`backend/logs`)
3. Vérifier la connexion backend (http://localhost:8000/health)

## License
© 2024 Assistant IA. Tous droits réservés.
