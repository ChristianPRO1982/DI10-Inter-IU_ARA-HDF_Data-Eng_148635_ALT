# PARTIE 1 - #2 - Analyse des **dimensions** et axes d’analyse associés

**Objectif**
Pour chaque table de dimension, expliquer **ce qu’elle décrit** et **ce qu’elle permet d’analyser** par rapport à la table de faits `FactResellerSales`.

👉 On ne parle **pas encore de KPI**, uniquement des **axes d’analyse**.

---

## 1. Dimension Produit — `DimProduct`

### Rôle

Décrit les caractéristiques des produits vendus.

### Informations clés (exemples)

* nom du produit
* catégorie / sous-catégorie
* couleur
* taille
* modèle
* coût standard
* prix catalogue

### Analyses possibles

* ventes par **produit**
* ventes par **catégorie / sous-catégorie**
* performance par **gamme de produits**
* analyse de **marge par produit**
* comparaison produits chers vs produits d’entrée de gamme

---

## 2. Dimension Revendeur — `DimReseller`

### Rôle

Décrit les entreprises clientes qui achètent les produits (revendeurs).

### Informations clés (exemples)

* nom du revendeur
* type de business (Warehouse, Specialty, VAR, etc.)
* taille de l’entreprise (nombre d’employés)
* chiffre d’affaires annuel
* date d’ouverture

### Analyses possibles

* ventes par **revendeur**
* ventes par **type de revendeur**
* performance selon la **taille du revendeur**
* analyse de **fidélité** et de **valeur client**
* segmentation des revendeurs (petits / grands comptes)

---

## 3. Dimension Employé — `DimEmployee`

### Rôle

Décrit les employés impliqués dans les ventes (commerciaux).

### Informations clés (exemples)

* nom et prénom
* poste
* département
* date d’embauche
* territoire de vente

### Analyses possibles

* ventes par **commercial**
* performance par **équipe / département**
* analyse de performance **avant / après embauche**
* comparaison des résultats entre commerciaux

---

## 4. Dimension Géographie — `DimGeography`

### Rôle

Décrit la localisation géographique des revendeurs.

### Informations clés (exemples)

* ville
* région / état
* pays
* territoire de vente

### Analyses possibles

* ventes par **pays**
* ventes par **région**
* performance par **territoire commercial**
* comparaison des marchés géographiques
* détection des zones à fort / faible potentiel

---

## 5. Dimension Temps — `DimDate`

### Rôle

Décrit les différentes représentations du temps pour l’analyse.

### Informations clés (exemples)

* date complète
* jour de la semaine
* mois
* trimestre
* année
* année fiscale

### Analyses possibles

* évolution des ventes dans le **temps**
* comparaisons **mois / trimestre / année**
* analyses saisonnières
* suivi de croissance ou de décroissance
* comparaisons année N vs N-1

---

## 6. Synthèse — Tableau récapitulatif (attendu au rendu)

Tu peux intégrer ce tableau tel quel dans ta restitution :

| Dimension    | Rôle                          | Analyses possibles                       |
| ------------ | ----------------------------- | ---------------------------------------- |
| DimProduct   | Décrit les produits           | CA, marge, volume par produit, catégorie |
| DimReseller  | Décrit les clients revendeurs | Performance client, segmentation         |
| DimEmployee  | Décrit les commerciaux        | Performance par employé                  |
| DimGeography | Décrit la localisation        | CA par pays, région, territoire          |
| DimDate      | Décrit le temps               | Évolutions temporelles, saisonnalité     |
