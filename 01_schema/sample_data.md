# Exemples de données

## Dim_Type_Fuel
- 1 = Fioul lourd = HFO 380
- 2 = Fioul leger = MGO DMA

## Dim_Cuve
- 1 = C-001 = Cuve A = capacité 60
- 2 = C-002 = Cuve B = capacité 45
- 3 = C-003 = Cuve C = capacité 35

## Fact_Fuel
Exemples :
- 20250101, cuve 1, fuel 1, consommation 0.494, volume 13.385
- 20250101, cuve 2, fuel 1, consommation 0.2964, volume 8.031
- 20250101, cuve 3, fuel 2, consommation 0.1976, volume 5.354
# Exemples de données - DW_Energie

Ce document contient des exemples réels issus des tables pour aider à comprendre les valeurs manipulées par le système.

---

## 🔷 Types de fuel (Dim_Type_Fuel)

| id_type_fuel | type_fuel   | nom_fuel |
|--------------|------------|----------|
| 1            | Fioul lourd | HFO 380  |
| 2            | Fioul leger | MGO DMA  |

👉 Interprétation :
- HFO 380 = fioul lourd
- MGO DMA = fioul léger

---

## 🔷 Cuves (Dim_Cuve)

| id_cuve | numero_cuve | nom_cuve | capacite_max |
|--------|-------------|----------|--------------|
| 1      | C-001       | Cuve A   | 60           |
| 2      | C-002       | Cuve B   | 45           |
| 3      | C-003       | Cuve C   | 35           |

👉 Interprétation :
- Chaque cuve a une capacité maximale (en tonne)
- Les cuves sont identifiées par un numéro et un nom

---

## 🔷 Dates disponibles (DIM_DATE)

### Années disponibles :
- 2025
- 2026

### Mois disponibles :

| annee | mois |
|------|------|
| 2025 | 1 à 12 |
| 2026 | 1 |

👉 Interprétation :
- Les données couvrent toute l’année 2025
- Et le début de 2026

---

## 🔷 Exemple de données Fact_Fuel

| id_date  | id_cuve | id_type_fuel | consommation_en_tonne | volume_en_tonne |
|----------|--------|--------------|------------------------|-----------------|
| 20250101 | 1      | 1            | 0.494                  | 13.385          |
| 20250101 | 2      | 1            | 0.2964                 | 8.031           |
| 20250101 | 3      | 2            | 0.1976                 | 5.354           |
| 20250102 | 1      | 1            | 1.6075                 | 12.891          |
| 20250102 | 2      | 1            | 0.9645                 | 7.7346          |
| 20250102 | 3      | 2            | 0.643                  | 5.1564          |

👉 Interprétation :
- Chaque ligne correspond à :
  - une date
  - une cuve
  - un type de fuel
- consommation_en_tonne = quantité consommée
- volume_en_tonne = volume associé (à confirmer métier)

---

## 🔷 Correspondances utiles (pour le futur assistant)

- Cuve A = C-001 = id_cuve 1
- Cuve B = C-002 = id_cuve 2
- Cuve C = C-003 = id_cuve 3

- Fioul lourd = HFO 380 = id_type_fuel 1
- Fioul léger = MGO DMA = id_type_fuel 2

---

## 🔷 Exemple de jointure logique

```sql
SELECT *
FROM dbo.Fact_Fuel f
JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
JOIN dbo.Dim_Cuve c ON f.id_cuve = c.id_cuve
JOIN dbo.Dim_Type_Fuel t ON f.id_type_fuel = t.id_type_fuel;