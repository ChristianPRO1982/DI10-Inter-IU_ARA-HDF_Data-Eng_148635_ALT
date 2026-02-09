# Brief : Construction d’un Data Warehouse et de Data Marts avec BigQuery

---

## Partie 0 — Veille : Concepts DW, OLAP et BigQuery

Cette phase de veille pose les bases conceptuelles nécessaires à la conception et à l’implémentation du Data Warehouse AdventureWorks dans BigQuery.

---

## 1. Concepts du Data Warehouse

- **Informatique décisionnelle**  
  Analyse des données pour l’aide à la décision.

- **Entrepôt de données (DW)**  
  Base orientée analyse, intégrée, historisée et non volatile.

- **Modélisation décisionnelle**
  - tables de faits (mesures) ;
  - tables de dimensions (axes d’analyse) ;
  - schémas en **étoile** ou en **flocon**.

**TD associé**  
Conception conceptuelle d’un Data Warehouse  
(identification des faits, dimensions et mesures).

---

## 2. OLAP et implantation des Data Warehouses

### Approches d’implantation

- **ROLAP** : basé sur des bases relationnelles et SQL ;
- **MOLAP** : basé sur des cubes multidimensionnels ;
- **HOLAP** : approche hybride.

### Opérations OLAP principales

- **Slice** : sélection sur une dimension ;
- **Dice** : sélection multidimensionnelle ;
- **Roll-up** : agrégation (jour → mois → année) ;
- **Drill-down** : descente dans le détail ;
- **Pivot** : changement d’axe d’analyse.

### Requêtes OLAP SQL

- jointures faits / dimensions ;
- agrégations (`SUM`, `COUNT`, `AVG`) ;
- analyses temporelles.

---

## 3. Introduction à BigQuery

- **BigQuery** : Data Warehouse cloud **serverless** (GCP) ;
- moteur SQL analytique massivement parallèle ;
- séparation stockage / calcul ;
- scalabilité automatique.

### Bonnes pratiques clés

- organisation des données par **datasets** ;
- tables volumineuses optimisées par :
  - **partitionnement** (souvent temporel) ;
  - **clustering** (colonnes fréquemment filtrées) ;
- approche **ELT** privilégiée en environnement Cloud.

**TP associé**  
Modélisation et conception logique ROLAP d’un entrepôt de données,  
avec quelques requêtes OLAP SQL.
