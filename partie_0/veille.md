# Partie 0 — Veille : Concepts DW, OLAP et BigQuery

Cette phase de veille vise à poser les bases conceptuelles nécessaires à la conception et à l’implémentation d’une architecture décisionnelle moderne dans BigQuery. Elle couvre les notions de Data Warehouse, d’OLAP et les spécificités du moteur BigQuery.

---

## 1. Data Warehouse

Un **Data Warehouse (DW)** est une base de données orientée **aide à la décision**, conçue pour analyser l’activité d’une entreprise sur le long terme.

Ses principales caractéristiques sont :
- **Intégré** : les données proviennent de plusieurs systèmes sources et sont harmonisées ;
- **Historisé** : les données sont conservées dans le temps afin d’analyser les évolutions ;
- **Non volatil** : les données ne sont pas modifiées transactionnellement ;
- **Orienté analyse** : optimisé pour les lectures, agrégations et calculs de KPI.

La modélisation décisionnelle repose généralement sur :
- des **tables de faits**, qui portent les mesures quantitatives (ventes, montants, volumes) ;
- des **tables de dimensions**, qui décrivent les axes d’analyse (temps, produit, client, géographie).

Le modèle le plus courant est le **schéma en étoile**, favorisant la lisibilité et la performance des requêtes analytiques.

---

## 2. OLAP (Online Analytical Processing)

L’**OLAP** regroupe les techniques permettant l’analyse multidimensionnelle des données stockées dans un Data Warehouse.

On distingue plusieurs approches :
- **ROLAP** : exploitation d’un DW relationnel via SQL ;
- **MOLAP** : cubes multidimensionnels pré-agrégés ;
- **HOLAP** : combinaison des deux.

Les opérations OLAP principales sont :
- **Slice** : filtrage sur une valeur d’une dimension ;
- **Dice** : filtrage sur plusieurs dimensions ;
- **Roll-up** : agrégation vers un niveau supérieur (jour → mois → année) ;
- **Drill-down** : descente vers un niveau plus détaillé ;
- **Pivot** : changement d’axe d’analyse.

Dans un contexte SQL, l’OLAP s’appuie sur :
- des jointures entre tables de faits et dimensions ;
- des fonctions d’agrégation (`SUM`, `COUNT`, `AVG`) ;
- des regroupements et analyses temporelles.

---

## 3. BigQuery

**BigQuery** est le Data Warehouse cloud de Google Cloud Platform. Il s’agit d’un moteur analytique **serverless**, massivement parallèle, permettant d’exécuter des requêtes SQL sur de très grands volumes de données.

Ses caractéristiques principales sont :
- séparation du **stockage** et du **calcul** ;
- scalabilité automatique ;
- facturation à l’usage (stockage et données scannées).

BigQuery s’inscrit naturellement dans une approche **ELT** :
- les données sont d’abord chargées telles quelles ;
- les transformations sont réalisées directement dans le moteur SQL.

Bonnes pratiques essentielles :
- structurer les données par **datasets** (staging, core DW, data marts, meta) ;
- utiliser le **partitionnement** (souvent sur les dates) pour réduire les volumes scannés ;
- utiliser le **clustering** sur les colonnes fréquemment filtrées ;
- éviter les `SELECT *` sur les tables volumineuses.

---

## Conclusion

Les concepts de Data Warehouse et d’OLAP constituent le socle de l’analyse décisionnelle.  
BigQuery fournit une implémentation cloud moderne de ces principes, permettant de construire une architecture analytique performante, scalable et adaptée au pilotage de l’activité métier.
