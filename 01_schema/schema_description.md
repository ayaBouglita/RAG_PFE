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

## Table : dbo.Fact_Electricite
Rôle : table de faits contenant les mesures de consommation électrique des équipements.

Colonnes :
- id_date
- id_equipement
- id_etat
- id_equipe
- Consommation_kWh

## Table : dbo.DIM_ETAT
Rôle : dimension des états des équipements.

Colonnes :
- id_etat
- etat

Valeurs :
- 1 = marche
- 2 = arrêt
- 3 = panne

## Table : dbo.Dim_equipement
Rôle : dimension des équipements.

Colonnes :
- id_equipement
- nom_equipement

Exemples : Administration, Armoire générale 1, Atelier lavage, Compresseur GA 110, Chiller laser

## Table : dbo.Dim_Equipe
Rôle : dimension des équipes.

Colonnes :
- id_equipe
- nom_equipe

Exemples : Équipe Support, Équipe Énergie, Équipe Gravure, Équipe Production Brongo

## Grain de la table Fact_Electricite
Une ligne représente une mesure de consommation électrique pour :
- une date
- un équipement
- un état (marche / arrêt / panne)
- une équipe

## Relations Fact_Electricite
- Fact_Electricite.id_date = DIM_DATE.id_date
- Fact_Electricite.id_equipement = Dim_equipement.id_equipement
- Fact_Electricite.id_etat = DIM_ETAT.id_etat
- Fact_Electricite.id_equipe = Dim_Equipe.id_equipe