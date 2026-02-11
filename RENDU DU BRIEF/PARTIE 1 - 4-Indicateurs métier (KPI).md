# PARTIE 1 - #4 - Indicateurs métier (KPI)

## 1. Mesures utilisables pour les KPI

Rappel — seules les **mesures FLOW additives** sont utilisées :

* `SalesAmount`
* `OrderQuantity`
* `TotalProductCost`
* `DiscountAmount`
* `TaxAmt`
* `Freight`

---

## 2. KPI principaux proposés

### KPI 1 — Chiffre d’affaires

* **Mesure** : `SalesAmount`
* **Agrégation** : `SUM`
* **Axe d’analyse** : Temps

**Définition**

> **Chiffre d’affaires par période = SUM(SalesAmount) par jour / mois / année**

---

### KPI 2 — Volume de ventes

* **Mesure** : `OrderQuantity`
* **Agrégation** : `SUM`
* **Axe d’analyse** : Produit

**Définition**

> **Volume vendu = SUM(OrderQuantity) par produit / catégorie**

---

### KPI 3 — Coût total des ventes

* **Mesure** : `TotalProductCost`
* **Agrégation** : `SUM`
* **Axe d’analyse** : Temps ou Produit

**Définition**

> **Coût total = SUM(TotalProductCost) par période ou par produit**

---

### KPI 4 — Marge brute

* **Mesures** : `SalesAmount`, `TotalProductCost`
* **Calcul** : `SalesAmount - TotalProductCost`
* **Agrégation** : `SUM`
* **Axe d’analyse** : Produit / Revendeur / Temps

**Définition**

> **Marge brute = SUM(SalesAmount) - SUM(TotalProductCost)**

---

### KPI 5 — Montant total des remises

* **Mesure** : `DiscountAmount`
* **Agrégation** : `SUM`
* **Axe d’analyse** : Produit / Revendeur

**Définition**

> **Montant des remises = SUM(DiscountAmount)**

---

### KPI 6 — Nombre de commandes

* **Mesure dérivée** : `SalesOrderNumber`
* **Agrégation** : `COUNT(DISTINCT SalesOrderNumber)`
* **Axe d’analyse** : Temps / Revendeur

**Définition**

> **Nombre de commandes = COUNT(DISTINCT SalesOrderNumber)**

---

### KPI 7 — Panier moyen

* **Mesures** : `SalesAmount`
* **Calcul** : `SUM(SalesAmount) / COUNT(DISTINCT SalesOrderNumber)`
* **Axe d’analyse** : Temps / Revendeur

**Définition**

> **Panier moyen = CA total / nombre de commandes**

---

## 3. Tableau récapitulatif des KPI (livrable attendu)

À intégrer tel quel dans ton rendu :

| KPI                 | Formule                                               | Axe d’analyse    |
| ------------------- | ----------------------------------------------------- | ---------------- |
| Chiffre d’affaires  | `SUM(SalesAmount)`                                    | Temps            |
| Volume de ventes    | `SUM(OrderQuantity)`                                  | Produit          |
| Coût total          | `SUM(TotalProductCost)`                               | Produit / Temps  |
| Marge brute         | `SUM(SalesAmount) - SUM(TotalProductCost)`            | Produit / Client |
| Remises             | `SUM(DiscountAmount)`                                 | Produit / Client |
| Nombre de commandes | `COUNT(DISTINCT SalesOrderNumber)`                    | Temps / Client   |
| Panier moyen        | `SUM(SalesAmount) / COUNT(DISTINCT SalesOrderNumber)` | Temps / Client   |

---
---
---
---
---

> [SUITE DU RENDU ICI](https://github.com/ChristianPRO1982/DI10-Inter-IU_ARA-HDF_Data-Eng_148635_ALT/blob/main/RENDU%20DU%20BRIEF/PARTIE%202.md)