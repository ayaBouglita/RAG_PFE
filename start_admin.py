#!/usr/bin/env python3
"""
Script de démarrage complet - Initialise l'application RAG avec les fonctionnalités d'administration
"""
import os
import sys
import subprocess
from pathlib import Path

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def main():
    print_header("🚀 Démarrage de RAG Intelligence avec Administration")
    
    # Déterminer le répertoire racine
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    frontend_dir = script_dir / "frontend"
    
    # Étape 1: Migrer la base de données
    print_header("Étape 1: Migration de la base de données")
    try:
        print_info("Exécution du script de migration...")
        result = subprocess.run(
            ["python", str(backend_dir / "migrate_admin.py")],
            cwd=str(backend_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print_success("Migration terminée avec succès")
        else:
            print_error("Erreur lors de la migration")
            print(result.stderr)
    except Exception as e:
        print_error(f"Impossible d'exécuter la migration: {str(e)}")
        print_warning("Continuez manuellement si nécessaire")
    
    # Étape 2: Informations de démarrage
    print_header("Étape 2: Informations de démarrage")
    
    print_info("Backend (FastAPI):")
    print(f"  {Colors.BOLD}cd backend{Colors.RESET}")
    print(f"  {Colors.BOLD}python -m uvicorn app:app --reload{Colors.RESET}")
    print(f"  URL: {Colors.BOLD}http://localhost:8000{Colors.RESET}")
    print(f"  Docs: {Colors.BOLD}http://localhost:8000/docs{Colors.RESET}")
    
    print()
    print_info("Frontend (Vue.js):")
    print(f"  {Colors.BOLD}cd frontend{Colors.RESET}")
    print(f"  {Colors.BOLD}npm run dev{Colors.RESET}")
    print(f"  URL: {Colors.BOLD}http://localhost:5173{Colors.RESET}")
    
    # Étape 3: Identifiants par défaut
    print_header("Étape 3: Identifiants par défaut")
    
    print_warning("IMPORTANT - Changez ces identifiants en production!")
    print()
    print_info("Compte Administrateur:")
    print(f"  Email:    {Colors.BOLD}admin@rag-pfe.local{Colors.RESET}")
    print(f"  Username: {Colors.BOLD}admin{Colors.RESET}")
    print(f"  Password: {Colors.BOLD}admin123{Colors.RESET}")
    print()
    print_info("Accès à l'administration:")
    print(f"  Gestion des utilisateurs: {Colors.BOLD}http://localhost:5173/admin/users{Colors.RESET}")
    print(f"  Statistiques:             {Colors.BOLD}http://localhost:5173/admin/stats{Colors.RESET}")
    
    # Étape 4: Fonctionnalités
    print_header("Étape 4: Fonctionnalités disponibles")
    
    features = [
        ("👨‍💼 Gestion des utilisateurs", "Ajouter, modifier, supprimer des comptes"),
        ("📊 Statistiques système", "Voir le total d'utilisateurs, répartition des rôles"),
        ("🔐 Système de rôles", "Admin vs Utilisateur normal"),
        ("📈 Évolution des inscriptions", "Graphique d'inscription par jour"),
        ("🔒 Protection base de données", "Confirmation avant suppression d'utilisateur"),
    ]
    
    for title, description in features:
        print(f"{title}")
        print(f"  {description}")
        print()
    
    # Étape 5: Documentation
    print_header("Étape 5: Documentation")
    
    print_info("Pour plus d'informations:")
    print(f"  • Guide d'administration: {Colors.BOLD}ADMIN_GUIDE.md{Colors.RESET}")
    print(f"  • API Documentation:     {Colors.BOLD}http://localhost:8000/docs{Colors.RESET}")
    print(f"  • Architecture:          {Colors.BOLD}ARCHITECTURE_PHASE1.md{Colors.RESET}")
    
    print_header("✅ Préparation terminée!")
    
    print_warning("Prochaines étapes:")
    print("1. Démarrez le backend: cd backend && python -m uvicorn app:app --reload")
    print("2. Démarrez le frontend: cd frontend && npm run dev")
    print("3. Accédez à http://localhost:5173")
    print("4. Connectez-vous avec admin / admin123")
    print("5. Allez à /admin/users pour gérer les utilisateurs")

if __name__ == "__main__":
    main()
