#!/usr/bin/env python3
"""
Interface interactive du pipeline RAG - Version Finale
"""
from ask_database import ask, humanize_results

def display_result(result):
    """Affiche le résultat formaté"""
    if result["type"] == "text_response":
        print(f"\n📄 {result['answer']}\n")
    else:
        if result["valid"]:
            humanized = humanize_results(
                result["question"],
                result["sql"],
                result["rows"],
                result["columns"]
            )
            print(f"\n✅ {humanized}\n")
        else:
            print(f"\n❌ Erreur: {result['error']}\n")

print("\n" + "="*70)
print("🤖 ASSISTANT IA - REQUÊTES DONNÉES ÉNERGIE")
print("="*70)
print("Posez vos questions sur fuel, électricité, équipements, cuves...")
print("Tapez 'quit' pour quitter\n")

while True:
    question = input("❓ Q: ").strip()
    
    if not question:
        continue
    
    if question.lower() == "quit":
        print("\n👋 Bye!\n")
        break
    
    print("\n⏳ Traitement...")
    result = ask(question)
    display_result(result)
