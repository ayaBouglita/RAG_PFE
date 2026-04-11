#!/usr/bin/env python3
"""
Script de migration pour initialiser un administrateur par défaut et mettre à jour le schéma
"""
import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, User, create_tables, engine
from auth import hash_password
from sqlalchemy import text

load_dotenv()

def migrate_add_role_column():
    """Ajouter la colonne role si elle n'existe pas et mettre à jour les valeurs NULL"""
    print("Vérification de la colonne 'role'...")
    try:
        with engine.connect() as conn:
            # Vérifier si la colonne existe
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'app_users' AND COLUMN_NAME = 'role'
            """))
            
            if not result.fetchone():
                # Ajouter la colonne si elle n'existe pas
                conn.execute(text("""
                    ALTER TABLE app_users
                    ADD role VARCHAR(20) DEFAULT 'user'
                """))
                conn.commit()
                print("✓ Colonne 'role' ajoutée avec succès")
            else:
                print("✓ Colonne 'role' existe déjà")
            
            # Mettre à jour les valeurs NULL à 'user'
            update_result = conn.execute(text("""
                UPDATE app_users 
                SET role = 'user' 
                WHERE role IS NULL OR role = ''
            """))
            conn.commit()
            
            rows_updated = update_result.rowcount
            if rows_updated > 0:
                print(f"✓ {rows_updated} utilisateur(s) mis à jour avec le rôle 'user'")
            else:
                print("✓ Aucun utilisateur nécessitant une mise à jour")
                
    except Exception as e:
        print(f"✗ Erreur lors de la migration: {str(e)}")



def create_default_admin():
    """Créer un administrateur par défaut s'il n'existe pas"""
    print("\nVérification des administrateurs...")
    db = SessionLocal()
    try:
        # Vérifier si un admin existe
        admin = db.query(User).filter(User.role == "admin").first()
        
        if admin:
            print(f"✓ Un administrateur existe déjà: {admin.username}")
            return
        
        # Créer un premier admin
        first_admin = User(
            username="admin",
            email="admin@rag-pfe.local",
            password_hash=hash_password("admin123"),
            role="admin"
        )
        
        db.add(first_admin)
        db.commit()
        print("✓ Administrateur par défaut créé")
        print(f"  - Identifiant: admin")
        print(f"  - Mot de passe: admin123")
        print(f"  - Email: admin@rag-pfe.local")
        print("\n⚠️  IMPORTANT: Changez ce mot de passe immédiatement en production!")
        
    except Exception as e:
        print(f"✗ Erreur lors de la création de l'admin: {str(e)}")
    finally:
        db.close()


def display_statistics():
    """Afficher les statistiques finales"""
    print("\n" + "="*50)
    print("📊 STATISTIQUES FINALES")
    print("="*50)
    
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        total = db.query(func.count(User.id)).scalar()
        admin_count = db.query(func.count(User.id)).filter(User.role == "admin").scalar()
        user_count = db.query(func.count(User.id)).filter(User.role == "user").scalar()
        
        print(f"\n👥 Total d'utilisateurs: {total}")
        print(f"👨‍💼 Administrateurs: {admin_count}")
        print(f"👤 Utilisateurs normaux: {user_count}")
        
        if total > 0:
            admin_pct = (admin_count / total) * 100
            user_pct = (user_count / total) * 100
            print(f"\n📈 Répartition:")
            print(f"   - Admin: {admin_pct:.1f}%")
            print(f"   - User: {user_pct:.1f}%")
        
        print("\n✓ Migration réussie!")
        
    except Exception as e:
        print(f"✗ Erreur lors de l'affichage des stats: {str(e)}")
    finally:
        db.close()


def main():
    print("=== Migration du système d'administration ===\n")
    
    # Créer les tables
    print("Création des tables...")
    create_tables()
    print("✓ Tables créées/vérifiées\n")
    
    # Ajouter la colonne role
    migrate_add_role_column()
    
    # Créer l'admin par défaut
    create_default_admin()
    
    # Afficher les statistiques
    display_statistics()
    
    print("\n=== Migration terminée ===")


if __name__ == "__main__":
    main()
