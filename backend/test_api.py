"""
Script simple pour tester l'API
Usage: python test_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Couleurs
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
END = "\033[0m"


def test_register():
    """Test: Créer un compte"""
    print(f"\n{BLUE}1️⃣ Test REGISTER{END}")
    
    data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    
    if response.status_code == 200:
        print(f"{GREEN}✅ Créé:{END} {response.json()}")
        return data
    else:
        print(f"{RED}❌ Erreur:{END} {response.text}")
        return None


def test_login(creds):
    """Test: Se connecter"""
    print(f"\n{BLUE}2️⃣ Test LOGIN{END}")
    
    data = {
        "username": creds["username"],
        "password": creds["password"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✅ Token obtenu{END}")
        print(f"   Token: {result['access_token'][:50]}...")
        return result["access_token"]
    else:
        print(f"{RED}❌ Erreur:{END} {response.text}")
        return None


def test_create_conversation(token):
    """Test: Créer une conversation"""
    print(f"\n{BLUE}3️⃣ Test CREATE CONVERSATION{END}")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": "Test Conversation"}
    
    response = requests.post(
        f"{BASE_URL}/chat/conversations",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✅ Conversation créée:{END}")
        print(f"   ID: {result['id']}")
        return result["id"]
    else:
        print(f"{RED}❌ Erreur:{END} {response.text}")
        return None


def test_list_conversations(token):
    """Test: Lister les conversations"""
    print(f"\n{BLUE}4️⃣ Test LIST CONVERSATIONS{END}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/chat/conversations",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✅ Conversations listées:{END} {len(result['conversations'])} trouvées")
        return result["conversations"]
    else:
        print(f"{RED}❌ Erreur:{END} {response.text}")
        return None


def test_send_message(token, conversation_id):
    """Test: Envoyer un message"""
    print(f"\n{BLUE}5️⃣ Test SEND MESSAGE{END}")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "conversation_id": conversation_id,
        "message": "Quelle est la consommation totale de fuel?"
    }
    
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"{GREEN}✅ Réponse reçue:{END}")
        print(f"   Question: {result['user_message']}")
        print(f"   Réponse: {result['assistant_response'][:100]}...")
        print(f"   SQL: {result['sql_query'][:80]}...")
        return True
    else:
        print(f"{RED}❌ Erreur:{END} {response.text}")
        return False


def main():
    print(f"{BLUE}{'='*50}")
    print(f"   TEST API - RAG Intelligence")
    print(f"{'='*50}{END}")
    
    # Test 1: Register
    creds = test_register()
    if not creds:
        print(f"{RED}Arrêt: Impossible de créer un compte{END}")
        return
    
    # Test 2: Login
    token = test_login(creds)
    if not token:
        print(f"{RED}Arrêt: Impossible de se connecter{END}")
        return
    
    # Test 3: Create conversation
    conv_id = test_create_conversation(token)
    if not conv_id:
        print(f"{RED}Arrêt: Impossible de créer une conversation{END}")
        return
    
    # Test 4: List conversations
    test_list_conversations(token)
    
    # Test 5: Send message
    test_send_message(token, conv_id)
    
    print(f"\n{BLUE}{'='*50}")
    print(f"{GREEN}✅ TOUS LES TESTS PASSÉS!{END}")
    print(f"{BLUE}{'='*50}{END}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{RED}Erreur: {e}{END}")
