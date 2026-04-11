# 🛡️ Guide de l'Interface Administrateur

## Vue d'ensemble

L'interface administrateur fournit des outils pour gérer les utilisateurs et consulter les statistiques système de l'application RAG Intelligence.

### Fonctionnalités

- **Gestion des utilisateurs**: Ajouter, modifier, supprimer des comptes avec confirmation
- **Système de rôles**: Distinction entre administrateurs et utilisateurs normaux
- **Statistiques système**: Visualisation des données utilisateur et des tendances d'inscription

---

## 🔧 Configuration Initiale

### 1. Migration de la base de données

Avant de démarrer l'application, exécutez le script de migration pour ajouter le système de rôles :

```bash
cd backend
python migrate_admin.py
```

Ce script :
- ✓ Ajoute la colonne `role` à la table `app_users` (si elle n'existe pas)
- ✓ Crée un administrateur par défaut avec les identifiants :
  - **Identifiant**: `admin`
  - **Mot de passe**: `admin123`
  - **Email**: `admin@rag-pfe.local`

### 2. Changement du mot de passe par défaut

⚠️ **En production**, changez immédiatement le mot de passe administrateur :

1. Connectez-vous avec `admin / admin123`
2. Accédez à `/admin/users`
3. Cliquez sur "Modifier" à côté du compte admin
4. Changez le mot de passe

---

## 👨‍💼 Interface de Gestion des Utilisateurs

### Accès
- URL: `/admin/users`
- Nécessite un compte administrateur

### Fonctionnalités

#### 📋 Tableau des utilisateurs
Affiche la liste complète des utilisateurs avec :
- **ID**: Identifiant unique
- **Username**: Nom d'utilisateur
- **Email**: Adresse email
- **Rôle**: Admin ou Utilisateur (badge coloré)
- **Date d'inscription**: Date de création du compte
- **Actions**: Modifier ou Supprimer

#### ➕ Ajouter un utilisateur
1. Cliquez sur **"Ajouter un utilisateur"**
2. Remplissez le formulaire :
   - Nom d'utilisateur
   - Email
   - Mot de passe
   - Rôle (Admin ou Utilisateur)
3. Cliquez sur **"Créer"**

#### ✏️ Modifier un utilisateur
1. Cliquez sur **"Modifier"** dans la ligne de l'utilisateur
2. Modifiez les informations :
   - Nom d'utilisateur
   - Email
   - Rôle
3. Cliquez sur **"Mettre à jour"**

#### 🗑️ Supprimer un utilisateur
1. Cliquez sur **"Supprimer"** dans la ligne de l'utilisateur
2. Une confirmation s'affiche
3. Confirmez la suppression

⚠️ **Notes importantes** :
- La suppression est irréversible
- Tous les conversations et messages de l'utilisateur seront supprimés
- Impossible de supprimer votre propre compte

---

## 📊 Interface des Statistiques

### Accès
- URL: `/admin/stats`
- Nécessite un compte administrateur

### Affichages

#### 1️⃣ Cartes de synthèse (3 colonnes)
- **Total d'utilisateurs**: Nombre total de comptes
- **Administrateurs**: Nombre de comptes admin
- **Utilisateurs normaux**: Nombre d'utilisateurs réguliers

#### 2️⃣ Répartition des rôles
Visualisation graphique avec barres de progression montrant :
- Pourcentage d'administrateurs
- Pourcentage d'utilisateurs normaux
- Nombre pour chaque rôle

#### 3️⃣ Résumé statistique
Tableau de synthèse incluant :
- Total d'utilisateurs
- Nombre d'administrateurs
- Nombre d'utilisateurs normaux
- Ratio Admin/Utilisateur

#### 4️⃣ Évolution des inscriptions
Graphique horizontal montrant :
- Nombre d'inscriptions par jour
- Tendances d'activité
- Date et nombre d'utilisateurs inscrits

---

## 🔐 Système de Rôles

### Admin (👨‍💼)
- Accès à `/admin/users` et `/admin/stats`
- Peut gérer tous les utilisateurs
- Peut consulter les statistiques système
- Badge violet "Admin"

### Utilisateur (👤)
- Accès au chat RAG
- Impossible d'accéder aux pages administrateur
- Badge vert "Utilisateur"

---

## 🚀 Déploiement

### Backend (Flask/FastAPI)

**Routes API**:
```
GET    /api/admin/users           - Lister tous les utilisateurs
POST   /api/admin/users           - Créer un utilisateur
PUT    /api/admin/users/{id}      - Modifier un utilisateur
DELETE /api/admin/users/{id}      - Supprimer un utilisateur
GET    /api/admin/stats           - Obtenir les statistiques
```

**Authentification**: 
- Inclure le token JWT dans l'header `Authorization: Bearer <token>`

### Frontend (Vue.js)

**Composants**:
- `AdminPanel.vue`: Gestion des utilisateurs
- `AdminStats.vue`: Affichage des statistiques

**Navigation**:
- Menu en haut à droite avec lien vers Admin
- Accès automatique aux pages admin si l'utilisateur est admin

---

## 🐛 Dépannage

### Problème: Impossible d'accéder aux pages admin

**Solution**:
1. Vérifiez que vous êtes connecté en tant qu'admin
2. Vérifiez que le rôle dans la base de données est `"admin"`
3. Utilisez l'outil d'administration ou modifiez la base de données directement

### Problème: Migration échoue

**Solution**:
1. Vérifiez la connexion SQL Server
2. Vérifiez que le user dispose des droits ALTER TABLE
3. Consultez les logs d'erreur pour plus de détails

### Problème: Actions d'admin échouent

**Solution**:
1. Vérifiez le token JWT dans les les outils de développement (Network tab)
2. Vérifiez que le token n'est pas expiré
3. Reconnectez-vous si nécessaire

---

## 📝 API de base de données

### Table `app_users`
```sql
CREATE TABLE app_users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT GETUTCDATE()
);
```

### Valeurs de `role`
- `"admin"`: Administrateur
- `"user"`: Utilisateur normal

---

## 📚 Références

- [API Routes](#-déploiement)
- [Système de Rôles](#-système-de-rôles)
- [Guide de Gestion Utilisateurs](#-interface-de-gestion-des-utilisateurs)
- [Guide des Statistiques](#-interface-des-statistiques)
