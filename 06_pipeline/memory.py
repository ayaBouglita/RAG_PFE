import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from config import ARTIFACTS_DIR

# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE 1 : MÉMOIRE DE SESSION (Conversation)
# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT : Historique TEMPORAIRE de la conversation actuelle
# Exemple : Les 10 dernières questions/réponses de CETTE session
# Stockage : En RAM (effacé au redémarrage)
# Utilité : Donner du contexte à l'IA pour bien comprendre la conversation
# ═══════════════════════════════════════════════════════════════════════════════

class ConversationMemory:
    """
    Gère l'historique de la conversation actuelle (session en cours)
    
    Cette classe stocke temporairement les Q&A de la session.
    Elle aide l'IA à comprendre le contexte en relisant les interactions précédentes.
    
    Exemple de flux :
        1. Utilisateur: "Quelle est la consommation de fuel?"
        2. IA généré une réponse SQL
        3. ConversationMemory.add_interaction() sauvegarde cette interaction
        4. Utilisateur posant la Q2: L'IA peut voir la Q1 et adapter sa réponse
    """
    
    def __init__(self, max_turns: int = 10):
        """
        Initialise la mémoire de conversation
        
        PARAMÈTRES :
            max_turns (int) : Nombre MAXIMUM de questions/réponses à garder
                             Au-delà, les plus anciennes sont supprimées
                             
        EXEMPLE :
            max_turns = 10 signifie : on garde les 10 dernières interactions
            Si 11e interaction arrive → La 1ère est supprimée (FIFO)
        """
        self.max_turns = max_turns  # Limite de la mémoire (ex: 10 dernières questions)
        self.history = []  # Liste qui stocks les Q/R : [{'question': '...', 'answer': '...'}, ...]
    
    def add_interaction(self, question: str, answer: str, answer_type: str):
        """
        Ajoute une interaction Question/Réponse à l'historique
        
        PARAMÈTRES :
            question (str) : La question posée par l'utilisateur
                            Ex: "Quelle est la consommation totale?"
            
            answer (str) : La réponse fournie par l'IA ou la base de données
                          Ex: "5000 tonnes"
            
            answer_type (str) : Type de réponse
                               - "sql_query" : Réponse d'une requête SQL
                               - "text_response" : Réponse textuelle générée
        
        LOGIQUE :
            1. Créer un dictionnaire avec Q/R + timestamp
            2. L'ajouter à la liste d'historique
            3. Si on dépasse le max, supprimer les plus anciennes (garder les dernières)
        
        EXEMPLE D'UTILISATION :
            mem.add_interaction(
                question="Quelle est la consommation de fuel?",
                answer="5000 tonnes",
                answer_type="sql_query"
            )
        """
        # Créer une entrée avec timestamp pour tracer QUAND la question a été posée
        self.history.append({
            "timestamp": datetime.now().isoformat(),  # format ISO : 2024-01-15T10:30:45.123456
            "question": question,  # La question telle que posée
            "answer": answer,  # La réponse complète
            "type": answer_type  # Type de réponse (sql_query ou text_response)
        })
        
        # GESTION DE LA MÉMOIRE : Garder seulement les N DERNIÈRES interactions
        # Si on a plus de max_turns interactions, supprimer les plus anciennes
        if len(self.history) > self.max_turns:
            # Garder uniquement les N dernières (ex: les 10 dernières si max_turns=10)
            # [-10:] prend les 10 derniers éléments d'une liste
            self.history = self.history[-self.max_turns:]
    
    def get_context(self) -> str:
        """
        Récupère l'historique formaté pour utiliser dans le prompt de l'IA
        
        BUT : Transformer la liste brute en texte lisible que l'IA peut utiliser
        
        RETOUR (str) : 
            - String vide si pas d'historique
            - Sinon, texte formaté avec header + les 5 dernières interactions
        
        EXEMPLE DE RETOUR :
            \"\"\"
            === HISTORIQUE DE LA CONVERSATION ===
            
            Q: Quelle est la consommation de fuel en 2024?
            R: La consommation totale de fuel est 5000 tonnes...
            
            Q: Et pour l'électricité?
            R: La consommation d'électricité est 3000 MWh...
            \"\"\"
        
        DÉTAILS :
            - On utilise les 5 DERNIÈRE interactions (pas les 10) pour le contexte
              Raison : Garder le contexte pertinent sans surcharger le prompt
            - On prend les 200 premiers caractères de la réponse
              Raison : Résumé court pour ne pas faire explose le contexte
        """
        # Si pas d'historique, retourner une string vide
        # (Pas besoin de contexte vide)
        if not self.history:
            return ""
        
        # Créer le header du contexte
        context = "=== HISTORIQUE DE LA CONVERSATION ===\n\n"
        
        # Parcourir les 5 DERNIÈRES interactions
        for item in self.history[-5:]:  # [-5:] = les 5 derniers éléments
            # Ajouter la question
            context += f"Q: {item['question']}\n"
            # Ajouter les 200 premiers caractères de la réponse (résumé)
            context += f"R: {item['answer'][:200]}...\n\n"  # [:200] = prendre les 200 premiers chars
        
        # Retourner le contexte formaté (prêt pour le prompt)
        return context
    
    def clear(self):
        """
        Efface complètement l'historique de conversation
        
        BUT : Réinitialiser la conversation pour une nouvelle session
        
        QUAND L'UTILISER :
            - Avec reset_conversation() du MemoryManager
            - Après une déconnexion/reconnexion de l'utilisateur
            - Pour "oublier" la conversation précédente
        
        NOTE : Ceci N'efface PAS la mémoire persistante (JSON)
               Juste l'historique en RAM
        """
        self.history = []  # Réinitialiser la liste à vide


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE 2 : MÉMOIRE PERSISTANTE (Faits, Préférences, Analytics)
# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT : Mémoire PERMANENTE entre les sessions
# Exemple : "L'utilisateur travaille sur DW_Energie" - mémorisé pour toujours
# Stockage : Fichier JSON sur disque (artifacts/persistent_memory.json)
# Utilité : Apprentissage machine sur les préférences et faits utilisateur
# Structure : {
#   "facts": [...],                    # Faits appris
#   "user_preferences": {...},         # Préférences (devise, année défaut, etc)
#   "frequent_topics": {...},          # Compteur de popularité des topics
#   "last_updated": "2024-01-15T..."   # Quand a été mise à jour
# }
# ═══════════════════════════════════════════════════════════════════════════════

class PersistentMemory:
    """
    Gère la mémoire persistante - faits appris entre les sessions
    
    C'est comme un journal que l'IA remplit au fil du temps :
    - Points importants sur l'utilisateur (préférences)
    - Faits contextuels (environnement, métier)
    - Analytics (topics populaires)
    
    Cette mémoire SURVIT aux redémarrages car elle est dans un fichier JSON.
    """
    
    def __init__(self):
        """
        Initialise la mémoire persistante
        
        ÉTAPES :
            1. Vérifier si le fichier persistent_memory.json existe
            2. Si oui : le charger
            3. Si non : créer une structure par défaut
        """
        # Chemin complet du fichier persisten : artifacts/persistent_memory.json
        self.memory_file = ARTIFACTS_DIR / "persistent_memory.json"
        
        # Charger le contenu du fichier (ou créer une structure vide)
        self.memory_data = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """
        Charge la mémoire depuis le fichier JSON
        
        LOGIQUE :
            1. Vérifier si le fichier existe
            2. Si oui : lire et parser le JSON
            3. Si erreur (fichier corrompu) : créer une structure par défaut
            4. Si non : créer une structure par défaut
        
        RETOUR :
            Dict contenant la structure de mémoire
        
        FORMAT DU FICHIER :
            {
                "facts": [
                    {"fact": "...", "category": "...", "timestamp": "..."},
                    ...
                ],
                "user_preferences": {
                    "clé1": {"value": ..., "timestamp": "..."},
                    ...
                },
                "frequent_topics": {"topic1": 5, "topic2": 3, ...},
                "last_updated": "2024-01-15T..."
            }
        """
        # Vérifier si le fichier existe
        if self.memory_file.exists():
            try:
                # Ouvrir et lire le fichier JSON
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # Si erreur (fichier corrompu), créer une structure par défaut
                # Ceci évite de planter si le fichier est cassé
                return self._default_memory()
        
        # Si le fichier n'existe pas, créer une structure vide
        return self._default_memory()
    
    def _default_memory(self) -> Dict[str, Any]:
        """
        Crée une structure de mémoire par défaut (template vide)
        
        RETOUR :
            Dict avec la structure initiale vide
        
        STRUCTURE :
            - facts: liste vide (aucun fait appris)
            - user_preferences: dict vide (aucune préférence)
            - frequent_topics: dict vide (aucun topic trackké)
            - last_updated: timestamp du moment
        """
        return {
            "facts": [],  # [{fact: str, category: str, timestamp: str}, ...]
            "user_preferences": {},  # {key: {value: Any, timestamp: str}, ...}
            "frequent_topics": {},  # {topic: count, ...}
            "last_updated": datetime.now().isoformat()
        }
    
    def save(self):
        """
        Sauvegarde la mémoire dans le fichier JSON
        
        BUT : Persister les changements sur disque
        
        ÉTAPES :
            1. Mettre à jour le timestamp "last_updated"
            2. Écrire le contenu en JSON dans le fichier
            3. Utiliser indent=2 pour lisibilité humaine
            4. Utiliser ensure_ascii=False pour supporter les caractères (é, à, etc)
        
        NOTE : Cette fonction est appelée après chaque modification
               (add_fact, add_preference, track_topic)
        """
        # Mettre à jour la date de dernière modification
        self.memory_data["last_updated"] = datetime.now().isoformat()
        
        # Ouvrir le fichier en mode écriture
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            # Sérialiser le dictionnaire en JSON avec indentation
            # ensure_ascii=False permet d'écrire des caractères spéciaux (accents)
            # indent=2 formate le JSON avec indentation (lisible pour l'humain)
            json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
    
    def add_fact(self, fact: str, category: str = "general"):
        """
        Ajoute un fait mémorisé à la mémoire persistante
        
        UTILITÉ : Sauvegarder des éléments contextuels importants
                 que l'IA doit savoir sur l'utilisateur/son environnement
        
        PARAMÈTRES :
            fact (str) : Le fait à mémoriser
                        Ex: "L'utilisateur travaille sur DW_Energie"
                        Ex: "La consommation de fuel se mesure en tonnes"
            
            category (str) : Catégorie du fait pour organisation
                            Valeurs courantes :
                            - "general" : Information générale (défaut)
                            - "user_context" : Infos sur l'utilisateur
                            - "domain_knowledge" : Connaissance du domaine
                            - "schema" : Infos sur la structure DB
        
        EXEMPLE D'UTILISATION :
            mem.persistent.add_fact(
                "La cuve C2 a une capacité de 1000L",
                category="equipment"
            )
        
        RÉSULTAT :
            - Le fait est ajouté à memory_data["facts"]
            - Un timestamp est enregistré
            - Le fichier JSON est mis à jour sur disque
        """
        # Ajouter le fait à la liste avec metadata
        self.memory_data["facts"].append({
            "fact": fact,  # Le contenu du fait
            "category": category,  # Catégorie pour recherche/filtrage
            "timestamp": datetime.now().isoformat()  # Quand a été ajouté
        })
        
        # Sauvegarder immédiatement sur disque
        self.save()
    
    def add_preference(self, key: str, value: Any):
        """
        Ajoute une préférence utilisateur
        
        UTILITÉ : Mémoriser les paramètres et préférences de l'utilisateur
                 L'IA/App va adapter leurs réponses en fonction
        
        PARAMÈTRES :
            key (str) : Clé de la préférence
                       Ex: "year_default", "currency", "language"
            
            value (Any) : Valeur de la préférence
                         Ex: 2025, "EUR", "FR"
        
        EXEMPLE D'UTILISATION :
            # Préférence 1 : Année par défaut
            mem.persistent.add_preference("year_default", 2025)
            
            # Préférence 2 : Devise
            mem.persistent.add_preference("currency", "EUR")
            
            # Préférence 3 : Langue
            mem.persistent.add_preference("language", "FR")
        
        RÉSULTAT :
            - La préférence est mémorisée dans memory_data["user_preferences"]
            - Accès ultérieur : get_preferences()["year_default"] → 2025
            - Le fichier JSON est mis à jour
        """
        # Ajouter la préférence avec timestamp
        # Format : {clé: {value: valeur, timestamp: quand}}
        self.memory_data["user_preferences"][key] = {
            "value": value,  # La valeur de la préférence
            "timestamp": datetime.now().isoformat()  # Quand a été définie
        }
        
        # Sauvegarder immédiatement sur disque
        self.save()
    
    def track_topic(self, topic: str):
        """
        Suivi des topics fréquemment demandés (analytics)
        
        UTILITÉ : Comprendre les intérêts de l'utilisateur
                 Chaque fois qu'il demande sur un topic, on incrémente le compteur
        
        PARAMÈTRES :
            topic (str) : Le topic demandé
                         Ex: "fuel", "électricité", "consommation"
        
        EXEMPLE D'UTILISATION :
            # L'utilisateur pose une question sur fuel
            mem.persistent.track_topic("fuel")
            # fuel count = 1
            
            # Pose une autre question sur fuel
            mem.persistent.track_topic("fuel")
            # fuel count = 2
            
            # Pose une question sur électricité
            mem.persistent.track_topic("électricité")
            # électricité count = 1
        
        RÉSULTAT :
            frequent_topics = {"fuel": 2, "électricité": 1}
            → On sait que l'utilisateur s'intéresse surtout à "fuel"
        
        UTILITÉ :
            - Analytics : Voir les intérêts de l'utilisateur
            - Priorisation : Focus sur les topics populaires
            - Recommandations : Suggérer des reports sur les topics populaires
        """
        # Si le topic n'existe pas encore, créer un compteur à 0
        if topic not in self.memory_data["frequent_topics"]:
            self.memory_data["frequent_topics"][topic] = 0
        
        # Incrémenter le nombre de fois que ce topic a été demandé
        self.memory_data["frequent_topics"][topic] += 1
        
        # Sauvegarder les changements sur disque
        self.save()
    
    def get_facts(self, category: str = None) -> List[str]:
        """
        Récupère les faits mémorisés (optionnellement filtrés par catégorie)
        
        PARAMÈTRES :
            category (str, optional) : Si on veut filtrer par catégorie
                                      Si None : retourner TOUS les faits
        
        RETOUR :
            List de strings : Les faits eux-mêmes (pas les métadatas)
        
        EXEMPLE D'UTILISATION :
            # Récupérer TOUS les faits
            all_facts = mem.persistent.get_facts()
            # Résultat: ["Fait 1", "Fait 2", ...]
            
            # Récupérer les faits d'une catégorie
            domain_facts = mem.persistent.get_facts(category="domain_knowledge")
            # Résultat: ["Fait A", "Fait B", ...]
        
        DÉTAILS :
            - On retourne seulement les 10 faits les plus RÉCENTS
              Raison : Garder l'information pertinente sans surcharge
            - On retourne juste le texte du fait (pas le JSON)
              Raison : Plus simple à utiliser dans le prompt
        """
        # Obtenir la liste des faits
        facts = self.memory_data["facts"]
        
        # Si on spécifie une catégorie, filtrer par elle
        if category:
            # Garder juste les faits de cette catégorie
            facts = [f for f in facts if f.get("category") == category]
        
        # Retourner juste les 10 DERNIERS faits (les plus récents)
        # Et extraire juste le texte (pas la metadata)
        return [f["fact"] for f in facts[-10:]]
    
    def get_preferences(self) -> Dict[str, Any]:
        """
        Récupère les préférences de l'utilisateur
        
        RETOUR :
            Dict : {clé: valeur, clé: valeur, ...}
        
        EXEMPLE DE RETOUR :
            {
                "year_default": 2025,
                "currency": "EUR",
                "language": "FR"
            }
        
        UTILITÉ :
            - Récupérer toutes les préférences en 1 call
            - Format simplifié : juste {clé: valeur}
            - Pas besoin de timestamp pour l'utilisation
        
        DÉTAILS :
            - On simplifie la structure JSON
            - structure JSON a  : {clé: {value: ..., timestamp: ...}}
            - on retourne juste : {clé: value}
        """
        # Boucler sur toutes les préférences
        # Extraire juste la "value" (pas le timestamp)
        return {
            k: v["value"]  # Pour chaque préférence, prendre juste la valeur
            for k, v in self.memory_data["user_preferences"].items()
        }
    
    def get_context(self) -> str:
        """
        Retourne la mémoire persistante formatée pour le prompt de l'IA
        
        BUT : Transformer la structure JSON en texte lisible pour l'IA
        
        RETOUR (str) :
            String vide si aucune mémoire
            Sinon : texte formaté avec préférences + faits
        
        EXEMPLE DE RETOUR :
            \"\"\"
            === PRÉFÉRENCES UTILISATEUR ===
            - year_default: 2025
            - currency: EUR
            
            === FAITS MÉMORISÉS ===
            - L'utilisateur travaille sur DW_Energie
            - La consommation de fuel se mesure en tonnes
            \"\"\"
        
        UTILITÉ :
            - Formater la mémoire pour le prompt LLM
            - Inclure contexte utilisateur dans chaque réponse
            - Améliorer la qualité des réponses
        """
        # String pour accumuler le contexte
        context = ""
        
        # SECTION 1 : PRÉFÉRENCES UTILISATEUR
        prefs = self.get_preferences()
        if prefs:  # Si il y a au moins une préférence
            context += "=== PRÉFÉRENCES UTILISATEUR ===\n"
            for k, v in prefs.items():
                context += f"- {k}: {v}\n"
            context += "\n"
        
        # SECTION 2 : FAITS MÉMORISÉS
        facts = self.get_facts()
        if facts:  # Si il y a au moins un fait
            context += "=== FAITS MÉMORISÉS ===\n"
            for fact in facts:
                context += f"- {fact}\n"
            context += "\n"
        
        # Retourner le contexte formaté (ou vide si rien à retourner)
        return context
    
    def clear(self):
        """
        Efface toute la mémoire persistente
        
        ⚠️ ATTENTION : Action IRRÉVERSIBLE!
        
        UTILITÉ : Reset complet de la mémoire (très rare)
        
        QUAND L'UTILISER :
            - Reset manuel demandé par l'utilisateur
            - Test/debug du système
        
        RÉSULTAT :
            - Tous les facts supprimés
            - Toutes les preferences supprimées
            - Tous les topic counts reset
            - Le fichier JSON est réinitialisé
        """
        # Réinitialiser la structure vide
        self.memory_data = self._default_memory()
        # Sauvegarder immédiatement (delete irréversible)
        self.save()



# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE 3 : GESTIONNAIRE UNIFIÉ DE MÉMOIRE
# ═══════════════════════════════════════════════════════════════════════════════
# CONCEPT : Interface unique pour gérer les deux mémoires en coordination
# Rôle : Chef d'orchestre qui coordonne Conversation + Persistent Memory
# Utilité : Simplifier l'utilisation (1 classe au lieu de 2)
# Pattern : Facade pattern (masquer la complexité derrière une interface simple)
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryManager:
    """
    Gestionnaire unifié pour la mémoire conversation + persistente
    
    Cette classe COMBINE les deux mémoires :
    - ConversationMemory : Historique de SESSION (temporaire)
    - PersistentMemory : Historique PERMANENT (fichier)
    
    ANALOGUE HUMAIN :
    - Conversation Memory = Souvenirs à court terme (tu te souviens de ce qu'on vient de dire)
    - Persistent Memory = Souvenirs à long terme (tu te souviens des traits de la personne)
    
    INTERFACE :
    - .conversation : Accès direct à la mémoire de conversation
    - .persistent : Accès direct à la mémoire persistante
    
    EXEMPLE D'UTILISATION :
        mem = MemoryManager()
        mem.add_interaction(question, answer, type)  # Ajoute partout
        context = mem.get_full_context()  # Récupère TOUT formaté
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de mémoire
        
        ÉTAPES :
            1. Créer une instance de ConversationMemory (vide)
            2. Créer une instance de PersistentMemory (fichier disque)
            3. Prêt à être utilisé
        """
        # Instancier la mémoire de conversation
        # Cette mémoire commence toujours vide (nouvelle session)
        self.conversation = ConversationMemory()
        
        # Instancier la mémoire persistante
        # Celle-ci est chargée depuis le fichier JSON (s'il existe)
        self.persistent = PersistentMemory()
    
    def add_interaction(self, question: str, answer: str, answer_type: str):
        """
        Ajoute une interaction et met à jour la mémoire persistante
        
        BUT : Single point of entry pour ajouter une interaction
              Gère automatiquement :
              - Historique de conversation
              - Tracking de topics
              - Autres analytics futures
        
        PARAMÈTRES :
            question (str) : La question posée
                            Ex: "Quelle est la consommation totale de fuel?"
            
            answer (str) : La réponse fournie
                          Ex: "5000 tonnes"
            
            answer_type (str) : Type de réponse
                               - "sql_query" : Réponse d'une requête SQL générée
                               - "text_response" : Réponse textuelle
        
        LOGIQUE :
            1. Ajouter à ConversationMemory (historique RAM)
            2. Si answer_type == "sql_query":
                - Extraire un topic de la question
                - Tracker ce topic dans la mémoire persistante
        
        EXEMPLE :
            mem.add_interaction(
                question="Quelle est la consommation de fuel en 2024?",
                answer="5000 tonnes",
                answer_type="sql_query"
            )
            
            → Historique conversation mémorisé ✅
            → Topic "fuel" tracké (compteur +1) ✅
            → Persistence sauvegardée sur disque ✅
        """
        # Ajouter aux DEUX mémoires
        # 1. Historique de conversation (RAM)
        self.conversation.add_interaction(question, answer, answer_type)
        
        # 2. Analytics (persistant) - seulement si réponse SQL
        # Raison : Les requêtes SQL = requêtes importantes à tracker
        if answer_type == "sql_query":
            # Extraire un topic de la question
            topic = self._extract_topic(question)
            if topic:
                # Tracker/incrémenter ce topic dans la mémoire persistante
                self.persistent.track_topic(topic)
    
    def _extract_topic(self, question: str) -> str:
        """
        Extrait un topic de la question pour les analytics
        
        BUT : Identifier les sujets importants qu'on doit tracker
        
        PARAMÈTRES :
            question (str) : La question posée
                            Ex: "Quelle est la consommation de fuel?"
        
        RETOUR :
            str : Le topic identifié, ou None si aucun match
                  Ex: "fuel", "électricité", "consommation", etc.
        
        LOGIQUE :
            1. Définir la liste des topics connus
            2. Boucler sur chaque topic
            3. Vérifier si le mot est dans la question
            4. Retourner le premier match trouvé
        
        EXEMPLE :
            _extract_topic("Consommation de FUEL?") → "fuel"
            _extract_topic("Quel est le KPI d'électricité?") → "électricité"
            _extract_topic("Bonjour") → None (pas de topic)
        
        NOTE :
            - Case-insensitive (convertir en minuscules)
            - Simple substring matching
            - Retourne le PREMIER match
        """
        # Liste des topics qu'on veut tracker
        # À adapter selon votre domaine
        topics = ["consommation", "fuel", "électricité", "équipement", 
                  "cuve", "équipe", "date", "kpi"]
        
        # Convertir la question en minuscules pour comparaison case-insensitive
        q_lower = question.lower()
        
        # Boucler sur each topic
        for topic in topics:
            if topic in q_lower:  # Vérifier si le topic est dans la question
                return topic  # Retourner le premier match
        
        # Pas de topic trouvé
        return None
    
    def get_full_context(self) -> str:
        """
        Retourne le contexte COMPLET (conversation + persistance) pour le prompt
        
        BUT : Fournir TOUTE l'information pertinente à l'IA en un seul call
        
        RETOUR (str) :
            String formatée prête pour le prompt LLM
            Contient :
            - Préférences utilisateur
            - Faits mémorisés
            - Historique de conversation
        
        EXEMPLE DE RETOUR :
            \"\"\"
            === PRÉFÉRENCES UTILISATEUR ===
            - year_default: 2025
            
            === FAITS MÉMORISÉS ===
            - L'utilisateur travaille sur DW_Energie
            
            === HISTORIQUE DE LA CONVERSATION ===
            Q: Consommation totale?
            R: 5000 tonnes...
            \"\"\"
        
        DÉTAILS :
            - Persistent memory en premier (contexte général)
            - Conversation memory après (contexte spécifique)
            - Chaque section include un header
            - Sections vides sont exclues
        
        UTILITÉ :
            - Injecter dans le prompt du LLM
            - Améliorer la qualité des réponses
            - Fournir du contexte pertinent automatiquement
        """
        # Accumulateur pour le contexte final
        context = ""
        
        # SECTION 1 : MÉMOIRE PERSISTANTE
        # (Contexte général : préférences + faits)
        persistent_context = self.persistent.get_context()
        if persistent_context:  # Si il y a quelque chose à ajouter
            context += persistent_context
        
        # SECTION 2 : HISTORIQUE DE CONVERSATION
        # (Contexte spécifique : les 5 dernières Q/R)
        conversation_context = self.conversation.get_context()
        if conversation_context:  # Si il y a quelque chose à ajouter
            context += conversation_context
        
        # Retourner le contexte formaté (ou string vide si rien)
        return context
    
    def reset_conversation(self):
        """
        Réinitialise la conversation (garde la mémoire persistante)
        
        BUT : Effacer l'historique de la conversation actuelle
              SANS perdre la mémoire persistante (faits + préférences)
        
        QUAND L'UTILISER :
            - Nouvelle conversation avec l'utilisateur
            - After une déconnexion/reconnexion
            - Reset manuel demandé par l'utilisateur
        
        RÉSULTAT :
            - Historique de conversation : ✅ EFFACÉ (vide)
            - Mémoire persistante : ✅ GARDÉE (faits + prefs)
            - Topics tracker : ✅ GARDÉ (analytics)
        
        EXEMPLE :
            # Avant
            mem.conversation.history = [Q1, Q2, Q3]
            mem.persistent.memory_data["facts"] = [Fait1, Fait2]
            
            # Appel
            mem.reset_conversation()
            
            # Après
            mem.conversation.history = []  # ✅ Vide
            mem.persistent.memory_data["facts"] = [Fait1, Fait2]  # ✅ Intact
        """
        # Effacer l'historique de conversation
        self.conversation.clear()
        # Note : Pas d'appel à clear() sur persistent!
        #        On garde intentionnellement la mémoire permanente



if __name__ == "__main__":
    # Test du système de mémoire
    manager = MemoryManager()
    
    # Simulation d'une interaction
    manager.add_interaction(
        "Quelle est la consommation de fuel en janvier ?",
        "SELECT TOP 10 ... (résultat SQL)",
        "sql_query"
    )
    
    manager.persistent.add_preference("departement", "Énergie")
    manager.persistent.add_fact("L'utilisateur s'intéresse au fuel", "user_profile")
    
    print(manager.get_full_context())
