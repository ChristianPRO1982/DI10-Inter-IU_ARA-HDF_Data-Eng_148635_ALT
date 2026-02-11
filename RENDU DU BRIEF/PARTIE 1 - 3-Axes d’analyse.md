# PARTIE 1 - #3 - Axes d’analyse

## 1. Principe

Un **axe d’analyse** :

* correspond à **une dimension** ;
* possède un ou plusieurs **niveaux hiérarchiques** ;
* permet d’agréger les mesures FLOW à différents niveaux.

👉 Chaque hiérarchie doit être **logique métier** et **ordonnée du plus fin au plus agrégé**.

---

## 2. Axes d’analyse par dimension

### Dimension Produit — `DimProduct`

**Axe : Produit**

Hiérarchie :

```
Produit → Sous-catégorie → Catégorie
```

Analyses possibles :

* ventes par produit précis ;
* regroupement par familles de produits ;
* comparaison des performances entre catégories.

---

### Dimension Revendeur — `DimReseller`

**Axe : Client / Revendeur**

Hiérarchie possible :

```
Revendeur → Type de revendeur
```

Analyses possibles :

* performance individuelle des revendeurs ;
* analyse par typologie de clients (Warehouse, Specialty, VAR, etc.).

*(Selon les attributs disponibles, une hiérarchie par taille ou ancienneté peut aussi exister.)*

---

### Dimension Employé — `DimEmployee`

**Axe : Commercial**

Hiérarchie possible :

```
Employé → Département
```

Analyses possibles :

* performance par commercial ;
* performance par équipe ou département.

---

### Dimension Géographie — `DimGeography`

**Axe : Géographique**

Hiérarchie classique :

```
Ville → Région / État → Pays → Territoire de vente
```

Analyses possibles :

* ventes locales ;
* comparaisons régionales et nationales ;
* pilotage par territoires commerciaux.

---

### Dimension Temps — `DimDate`

**Axe : Temps**

Hiérarchie temporelle standard :

```
Jour → Mois → Trimestre → Année
```

Variantes possibles :

* calendrier fiscal ;
* jour → semaine → année.

Analyses possibles :

* évolution du chiffre d’affaires ;
* saisonnalité ;
* comparaisons année N / N-1.

---

## 3. Tableau récapitulatif (livrable attendu)

Tu peux intégrer directement ce tableau dans ta restitution :

| Dimension    | Axe d’analyse | Niveaux de granularité               |
| ------------ | ------------- | ------------------------------------ |
| DimProduct   | Produit       | Produit → Sous-catégorie → Catégorie |
| DimReseller  | Client        | Revendeur → Type de revendeur        |
| DimEmployee  | Commercial    | Employé → Département                |
| DimGeography | Géographie    | Ville → Région → Pays → Territoire   |
| DimDate      | Temps         | Jour → Mois → Trimestre → Année      |

---
---
---
---
---

> [SUITE DU RENDU ICI](https://github.com/ChristianPRO1982/DI10-Inter-IU_ARA-HDF_Data-Eng_148635_ALT/blob/main/RENDU%20DU%20BRIEF/PARTIE%201%20-%204-Indicateurs%20m%C3%A9tier%20(KPI).md)