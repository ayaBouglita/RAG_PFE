# Dictionnaire métier - DW_Energie

## Mesures principales

### consommation_en_tonne
Quantité consommée de fuel exprimée en tonne.
Cette mesure est utilisée pour calculer :
- la consommation totale
- la consommation moyenne
- la consommation minimale
- la consommation maximale
- les évolutions temporelles
- les comparaisons entre cuves
- les comparaisons entre types de fuel

### volume_en_tonne
Volume exprimé en tonne associé à la mesure.
Cette mesure peut être utilisée pour :
- calculer le volume total
- calculer le volume moyen
- suivre l’évolution du volume
- comparer les volumes par cuve ou par fuel

Attention : l’interprétation métier exacte de `volume_en_tonne` doit être confirmée.

---

## Dimensions principales

### date_complete
Date réelle de la mesure.

### jour
Jour du mois.

### mois
Mois de la mesure.

### annee
Année de la mesure.

### nom_cuve
Nom métier de la cuve.

### numero_cuve
Code technique ou identifiant visible de la cuve.

### capacite_max
Capacité maximale théorique de la cuve.

### type_fuel
Catégorie métier du carburant.

### nom_fuel
Nom précis du fuel.

---

## Entités métier

### Cuve
Réservoir de stockage identifié par :
- id_cuve
- numero_cuve
- nom_cuve

### Fuel
Type de carburant identifié par :
- id_type_fuel
- type_fuel
- nom_fuel

### Temps
Dimension temporelle identifiée par :
- id_date
- date_complete
- jour
- mois
- annee