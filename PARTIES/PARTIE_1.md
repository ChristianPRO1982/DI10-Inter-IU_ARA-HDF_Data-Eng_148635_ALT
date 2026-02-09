# 1. Analyse de la table FactResellerSales

## 1.1 Comprendre l’événement métier

> **Une ligne de la table `FactResellerSales` correspond à une ligne de commande de vente, c’est-à-dire la vente d’un produit donné à un revendeur donné, pour une commande donnée, à une date donnée.**
>
> Une même commande (`SalesOrderNumber`) peut donc être composée de plusieurs lignes (`SalesOrderLineNumber`), chacune représentant un article distinct vendu dans cette commande.

* elle explicite clairement la **granularité** ;
* elle relie **produit / revendeur / commande / temps** ;
* elle justifie naturellement la présence de `SalesOrderNumber` et `SalesOrderLineNumber` ;
* elle prépare parfaitement l’étape KPI (somme, comptage, etc.).

## 1.2 Identifier mesures, clés, types de mesures (FLOW / VPU / STOCK)

### 1. Clés de la table de faits (dimensions)

Ces colonnes définissent la **granularité du fait** et permettent les analyses multidimensionnelles.

### Clés étrangères vers les dimensions

| Colonne             | Dimension associée | Rôle              |
| ------------------- | ------------------ | ----------------- |
| `ProductKey`        | DimProduct         | Produit vendu     |
| `OrderDateKey`      | DimDate            | Date de commande  |
| `DueDateKey`        | DimDate            | Date d’échéance   |
| `ShipDateKey`       | DimDate            | Date d’expédition |
| `ResellerKey`       | DimReseller        | Revendeur         |
| `EmployeeKey`       | DimEmployee        | Commercial        |
| `SalesTerritoryKey` | DimGeography       | Zone géographique |

➡️ Ces clés **ne sont pas des mesures** et **ne s’agrègent jamais**.
Elles définissent **le grain : une ligne de commande par produit, par revendeur, par date**.

---
---

### 2. Identifiants métier (non analytiques)

Ces colonnes servent à l’identification mais **pas au calcul de KPI**.

| Colonne                 | Description             |
| ----------------------- | ----------------------- |
| `SalesOrderNumber`      | Numéro de commande      |
| `SalesOrderLineNumber`  | Numéro de ligne         |
| `RevisionNumber`        | Révision de la commande |
| `CarrierTrackingNumber` | Suivi transport         |
| `CustomerPONumber`      | Référence client        |

➡️ Utiles pour :

* compter les commandes (`COUNT(DISTINCT SalesOrderNumber)`),
* tracer / auditer,
* mais **jamais comme KPI directs**.

---
---

### 3. Mesures — classification FLOW / VPU / STOCK

***3.1 Mesures de type FLOW (additives)***

Ces mesures représentent un **flux** et sont **totalement additives**.

| Colonne            | Type | Additive | Agrégation recommandée |
| ------------------ | ---- | -------- | ---------------------- |
| `OrderQuantity`    | FLOW | ✅        | `SUM`                  |
| `ExtendedAmount`   | FLOW | ✅        | `SUM`                  |
| `DiscountAmount`   | FLOW | ✅        | `SUM`                  |
| `TotalProductCost` | FLOW | ✅        | `SUM`                  |
| `SalesAmount`      | FLOW | ✅        | `SUM`                  |
| `TaxAmt`           | FLOW | ✅        | `SUM`                  |
| `Freight`          | FLOW | ✅        | `SUM`                  |

👉 **Ce sont les bases des KPI métier**.

---

***3.2 Mesures de type VPU (non additives)***

Valeurs **par unité** ou **ratio** → **non additives**.

| Colonne                | Type | Additive | Agrégation recommandée |
| ---------------------- | ---- | -------- | ---------------------- |
| `UnitPrice`            | VPU  | ❌        | `AVG`, `MIN`, `MAX`    |
| `UnitPriceDiscountPct` | VPU  | ❌        | `AVG`                  |

⚠️ Les sommer **n’a aucun sens métier**.

---

***3.3 Mesure de type STOCK***

Valeur de référence, dépendante du produit.

| Colonne               | Type  | Additive | Remarque                 |
| --------------------- | ----- | -------- | ------------------------ |
| `ProductStandardCost` | STOCK | ❌        | Sert au calcul de marges |

➡️ On **ne somme jamais** un stock de référence.

---
---

### 4. Conclusion de l’étape

* La table `FactResellerSales` contient :

  * des **clés de dimensions**,
  * des **identifiants de commande**,
  * des **mesures FLOW (additives)** utilisables comme KPI,
  * des **mesures VPU / STOCK** réservées aux analyses ou calculs dérivés.
* Les KPI doivent **exclusivement** s’appuyer sur les mesures FLOW.
