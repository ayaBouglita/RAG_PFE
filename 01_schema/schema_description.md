# Schéma DW_Energie

## Table : dbo.Fact_Fuel
Rôle : table de faits contenant les mesures de consommation et de volume de fuel.

Colonnes :
- id_date
- id_cuve
- id_type_fuel
- consommation_en_tonne
- Volume_cuve_en_Tonne
## Table : dbo.DIM_DATE
Rôle : dimension temps.

Colonnes :
- id_date
- date_complete
- jour
- mois
- annee
## Table : dbo.Dim_Cuve
Rôle : dimension des cuves.

Colonnes :
- id_cuve
- numero_cuve
- nom_cuve
- capacite_max__T
- date_construction
## Grain de la table Fact_Fuel

Une ligne représente une mesure de consommation et de volume pour :
- une date
- une cuve
- un type de fuel
## Grain de la table Fact_Fuel
Une ligne représente une mesure de consommation et de volume pour une date donnée, une cuve donnée et un type de fuel donné.