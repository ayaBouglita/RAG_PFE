# Règles métier - DW_Energie

## Règles de calcul

### Consommation totale
Somme de `consommation_en_tonne`.

### Volume total
Somme de `volume_en_tonne`.

### Consommation moyenne
Moyenne de `consommation_en_tonne`.

### Volume moyen
Moyenne de `volume_en_tonne`.

### Consommation minimale
Minimum de `consommation_en_tonne`.

### Consommation maximale
Maximum de `consommation_en_tonne`.

### Analyse journalière
Agrégation par `date_complete`.

### Analyse mensuelle
Agrégation par `annee, mois`.

### Analyse annuelle
Agrégation par `annee`.

### Analyse par cuve
Agrégation par `nom_cuve` ou `numero_cuve`.

### Analyse par type de fuel
Agrégation par `type_fuel` ou `nom_fuel`.

### Part relative
Calcul en pourcentage :
(valeur / total) * 100

### Taux d’évolution
Calcul :
((valeur_courante - valeur_precedente) / valeur_precedente) * 100

Toujours sécuriser la division avec `NULLIF`.

---

## Relations logiques

- Fact_Fuel.id_date = DIM_DATE.id_date
- Fact_Fuel.id_cuve = Dim_Cuve.id_cuve
- Fact_Fuel.id_type_fuel = Dim_Type_Fuel.id_type_fuel

---

## Limitations connues

Le schéma actuel permet :
- agrégations
- comparaisons
- évolutions temporelles
- classements
- ratios simples

Le schéma actuel ne permet pas directement :
- explication causale des variations
- prévisions fiables
- analyse horaire
- mouvements d’entrée/sortie détaillés
- livraisons ou approvisionnements