# PARTIE 4 - 1.Création

## 🧭 Étape 1 — Création du Data Mart Ventes quotidien

### 1.1 — Créer la table `marts.mart_sales_daily`

**Objectif :**
Créer une table **pré-agrégée**, partitionnée par date, clusterisée par pays, contenant les KPI quotidiens par pays et type de revendeur.

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.marts.mart_sales_daily`
PARTITION BY order_date
CLUSTER BY country_name
AS
SELECT
  f.order_date,
  d.annee,
  d.trimestre,
  d.num_mois AS mois,
  d.nom_mois,
  g.country_name,
  r.business_type,

  -- KPI volume
  COUNT(DISTINCT f.order_number) AS nb_orders,
  COUNT(*) AS nb_lines,
  SUM(f.quantity) AS total_quantity,

  -- KPI financiers
  SUM(f.sales_amount) AS total_revenue,
  SUM(f.total_cost) AS total_cost,
  SUM(f.margin) AS total_margin,
  SUM(f.discount_amount) AS total_discount,
  SUM(f.tax_amount) AS total_tax,
  SUM(f.freight) AS total_freight,

  -- KPI calculés
  SAFE_DIVIDE(SUM(f.sales_amount), COUNT(DISTINCT f.order_number)) AS avg_order_value,
  SAFE_DIVIDE(SUM(f.margin), SUM(f.sales_amount)) * 100 AS margin_pct

FROM `adventureworks-dw-christian.dw.fact_reseller_sales` AS f
JOIN `adventureworks-dw-christian.dw.dim_date` AS d
  ON f.order_date_key = d.date_key
JOIN `adventureworks-dw-christian.dw.dim_reseller` AS r
  ON f.reseller_key = r.reseller_key
JOIN `adventureworks-dw-christian.dw.dim_geography` AS g
  ON r.geography_key = g.geography_key
GROUP BY
  f.order_date,
  d.annee,
  d.trimestre,
  mois,
  d.nom_mois,
  g.country_name,
  r.business_type;
```

## 1.2 — Vérif 1 : volumétrie & plage de dates

```sql
SELECT
  COUNT(*) AS nb_rows,
  MIN(order_date) AS min_date,
  MAX(order_date) AS max_date
FROM `adventureworks-dw-christian.marts.mart_sales_daily`;
```

**résultats**

| nb_rows | min_date   | max_date   |
|---------|------------|------------|
| 427     | 29/12/2010 | 29/11/2013 |

## 1.3 — Vérif 2 : cohérence du CA

Le total du mart doit être **strictement identique** au total du DW.

```sql
SELECT
  (SELECT SUM(sales_amount)
   FROM `adventureworks-dw-christian.dw.fact_reseller_sales`) AS dw_total,

  (SELECT SUM(total_revenue)
   FROM `adventureworks-dw-christian.marts.mart_sales_daily`) AS mart_total;
```

| dw_total     | mart_total   |
|--------------|--------------|
| 80450596,98  | 80450596,98  |

## 🧭 Étape 2 — Requêtes OLAP avancées (ROLLUP)

Exploitation analytique.

### 2.1 — CA avec sous-totaux par pays et type de revendeur (ROLLUP)

```sql
SELECT
  IFNULL(country_name, '*** TOTAL ***') AS country,
  IFNULL(business_type, '** Sous-total **') AS type,
  SUM(total_revenue) AS ca,
  SUM(total_margin) AS marge
FROM `adventureworks-dw-christian.marts.mart_sales_daily`
WHERE annee = 2013
GROUP BY ROLLUP(country_name, business_type)
ORDER BY country_name NULLS LAST, business_type NULLS LAST;
```

**résultats**

| country         | type                     | ca           | marge         |
|-----------------|--------------------------|--------------|---------------|
| Australia       | SPECIALTY BIKE SHOP      | 307491,3128  | -15894,0474   |
| Australia       | VALUE ADDED RESELLER     | 771696,2789  | -49187,3675   |
| Australia       | WAREHOUSE                | 465323,0708  | -26868,1327   |
| Australia       | **Sous-total**           | 1544510,663  | -91949,5476   |
| Canada          | SPECIALTY BIKE SHOP      | 378352,5864  | 12197,4425    |
| Canada          | VALUE ADDED RESELLER     | 1868612,422  | 28616,9178    |
| Canada          | WAREHOUSE                | 2934938,386  | -64794,5452   |
| Canada          | **Sous-total**           | 5181903,395  | -23980,1849   |
| France          | SPECIALTY BIKE SHOP      | 250202,4762  | -5879,7769    |
| France          | VALUE ADDED RESELLER     | 779022,2235  | -42581,771    |
| France          | WAREHOUSE                | 2094827,452  | -42256,4854   |
| France          | **Sous-total**           | 3124052,152  | -90718,0333   |
| Germany         | SPECIALTY BIKE SHOP      | 155833,9319  | -8792,047     |
| Germany         | VALUE ADDED RESELLER     | 584745,3635  | -20381,8614   |
| Germany         | WAREHOUSE                | 1063368,171  | -39645,4689   |
| Germany         | **Sous-total**           | 1803947,467  | -68819,3773   |
| United Kingdom  | SPECIALTY BIKE SHOP      | 200057,7093  | -4565,0204    |
| United Kingdom  | VALUE ADDED RESELLER     | 1088939,314  | -1878,9933    |
| United Kingdom  | WAREHOUSE                | 1431035,354  | -56652,6314   |
| United Kingdom  | **Sous-total**           | 2720032,377  | -63096,6451   |
| United States   | SPECIALTY BIKE SHOP      | 1406878,575  | -34546,6099   |
| United States   | VALUE ADDED RESELLER     | 9337064,496  | -10301,5621   |
| United States   | WAREHOUSE                | 8456445,034  | -108458,0464  |
| United States   | **Sous-total**           | 19200388,11  | -153306,2184  |
| **TOTAL**       | **Sous-total**           | 33574834,16  | -491870,0066  |

**Commentaire**

> 👉 Les marges sont négatives partout en 2013.

Ce n’est pas une erreur technique.
C’est lié au modèle AdventureWorks (StandardCost vs SalesAmount).

## 🧭 Étape 3 — `CUBE`

```sql
SELECT
  IFNULL(country_name, '*** TOTAL PAYS ***') AS country,
  IFNULL(CAST(trimestre AS STRING), '*** TOTAL TRIMESTRE ***') AS trimestre,
  SUM(total_revenue) AS ca,
  SUM(total_margin) AS marge
FROM `adventureworks-dw-christian.marts.mart_sales_daily`
WHERE annee = 2013
GROUP BY CUBE(country_name, trimestre)
ORDER BY country_name NULLS LAST, trimestre NULLS LAST;
```

**résultats**

| country             | trimestre | ca            | marge          |
|---------------------|-----------|---------------|----------------|
| Australia           | 1         | 456401,1532   | -80418,1127    |
| Australia           | 2         | 404584,7226   | -2575,8655     |
| Australia           | 3         | 335914,317    | -5731,4897     |
| Australia           | 4         | 347610,4697   | -3224,0797     |
| Australia           |           | 1544510,663   | -91949,5476    |
| Canada              | 1         | 1646105,51    | -67311,4846    |
| Canada              | 2         | 1382250,633   | 18665,0399     |
| Canada              | 3         | 1172938,193   | 18850,4835     |
| Canada              | 4         | 980609,0588   | 5815,7763      |
| Canada              |           | 5181903,395   | -23980,1849    |
| France              | 1         | 955866,1782   | -77310,1053    |
| France              | 2         | 832389,8454   | -5880,752      |
| France              | 3         | 611155,7639   | -496,4578      |
| France              | 4         | 724640,3642   | -7030,7182     |
| France              |           | 3124052,152   | -90718,0333    |
| Germany             | 1         | 572323,5934   | -55442,2981    |
| Germany             | 2         | 459141,345    | -4023,4065     |
| Germany             | 3         | 442696,0142   | -6834,9722     |
| Germany             | 4         | 329786,514    | -2518,7005     |
| Germany             |           | 1803947,467   | -68819,3773    |
| United Kingdom      | 1         | 825836,2375   | -59146,01      |
| United Kingdom      | 2         | 697665,2251   | 2692,2074      |
| United Kingdom      | 3         | 571903,7298   | 1158,8742      |
| United Kingdom      | 4         | 624627,1843   | -7801,7167     |
| United Kingdom      |           | 2720032,377   | -63096,6451    |
| United States       | 1         | 6086128,752   | -192349,1573   |
| United States       | 2         | 4880625,688   | 49103,8429     |
| United States       | 3         | 4510071,618   | 16294,9293     |
| United States       | 4         | 3723562,048   | -26355,8333    |
| United States       |           | 19200388,11   | -153306,2184   |
| **TOTAL PAYS**      | 1         | 10542661,42   | -531977,168    |
| **TOTAL PAYS**      | 2         | 8656657,459   | 57981,0662     |
| **TOTAL PAYS**      | 3         | 7644679,635   | 23241,3673     |
| **TOTAL PAYS**      | 4         | 6730835,639   | -41115,2721    |
| **TOTAL PAYS**      |           | 33574834,16   | -491870,0066   |

**Commentaire**

### 📝 Analyse — Résultat de `CUBE(country_name, trimestre)`

La requête utilisant `CUBE(country_name, trimestre)` génère **toutes les combinaisons possibles d’agrégation** entre les deux dimensions :

1. **Détail complet :**
   `country + trimestre`
   → CA trimestriel par pays.

2. **Sous-total par pays :**
   `country + NULL`
   → CA annuel par pays (équivalent au sous-total obtenu avec `ROLLUP`).

3. **Sous-total par trimestre :**
   `NULL + trimestre`
   → CA global de chaque trimestre tous pays confondus.

4. **Total général :**
   `NULL + NULL`
   → CA total 2013.

### 🔎 Différence fondamentale entre `ROLLUP` et `CUBE`

* `ROLLUP` suit **une hiérarchie logique** (ex : pays → type → total).
  Il produit uniquement les sous-totaux “ascendants”.

* `CUBE` produit **toutes les combinaisons possibles**, sans notion de hiérarchie.
  Il est plus complet mais génère davantage de lignes.

👉 Formellement :

* `ROLLUP(n)` → n+1 niveaux
* `CUBE(n)` → 2ⁿ combinaisons

Ici, avec 2 dimensions :
`2² = 4 niveaux d’agrégation`.

### 📊 Lecture métier intéressante

On observe que :

* Le **T1 2013** est le trimestre le plus performant (10,54M).
* Le **T4 2013** est le moins performant.
* Les États-Unis dominent tous les trimestres.
* La marge est fortement négative au T1 mais positive au T2 et T3 (effet saisonnier ou structure produit).

## 🧭 Étape 4 — Évolution mensuelle & croissance (Window Functions)

Analyse de l’évolution du chiffre d’affaires mois par mois, avec :

* CA mensuel
* CA du mois précédent
* Taux de croissance %

## 4.1 — CA mensuel avec delta vs mois précédent

```sql
SELECT
  annee,
  mois,
  nom_mois,

  SUM(total_revenue) AS ca_mensuel,

  LAG(SUM(total_revenue))
    OVER (ORDER BY annee, mois) AS ca_mois_precedent,

  ROUND(
    SAFE_DIVIDE(
      SUM(total_revenue)
      - LAG(SUM(total_revenue)) OVER (ORDER BY annee, mois),
      LAG(SUM(total_revenue)) OVER (ORDER BY annee, mois)
    ) * 100,
    2
  ) AS croissance_pct

FROM `adventureworks-dw-christian.marts.mart_sales_daily`
GROUP BY annee, mois, nom_mois
ORDER BY annee, mois;
```

**résultats**

| annee | mois | nom_mois  | ca_mensuel    | ca_mois_precedent | croissance_pct |
|-------|------|-----------|---------------|-------------------|----------------|
| 2010  | 12   | December  | 489328,5787   |                   |                |
| 2011  | 1    | January   | 1538408,312   | 489328,5787       | 214,39         |
| 2011  | 3    | March     | 2010618,074   | 1538408,312       | 30,69          |
| 2011  | 5    | May       | 4027080,34    | 2010618,074       | 100,29         |
| 2011  | 7    | July      | 713116,6943   | 4027080,34        | -82,29         |
| 2011  | 8    | August    | 3356069,344   | 713116,6943       | 370,62         |
| 2011  | 9    | September | 882899,9424   | 3356069,344       | -73,69         |
| 2011  | 10   | October   | 2269116,712   | 882899,9424       | 157,01         |
| 2011  | 11   | November  | 1001803,77    | 2269116,712       | -55,85         |
| 2011  | 12   | December  | 2393689,526   | 1001803,77        | 138,94         |
| 2012  | 1    | January   | 3601190,714   | 2393689,526       | 50,45          |
| 2012  | 2    | February  | 2885359,199   | 3601190,714       | -19,88         |
| 2012  | 3    | March     | 1802154,213   | 2885359,199       | -37,54         |
| 2012  | 4    | April     | 3053816,326   | 1802154,213       | 69,45          |
| 2012  | 5    | May       | 2185213,215   | 3053816,326       | -28,44         |
| 2012  | 6    | June      | 1317541,833   | 2185213,215       | -39,71         |
| 2012  | 7    | July      | 2384846,591   | 1317541,833       | 81,01          |
| 2012  | 8    | August    | 1563955,081   | 2384846,591       | -34,42         |
| 2012  | 9    | September | 1865278,434   | 1563955,081       | 19,27          |
| 2012  | 10   | October   | 2880752,681   | 1865278,434       | 54,44          |
| 2012  | 11   | November  | 1987872,707   | 2880752,681       | -30,99         |
| 2012  | 12   | December  | 2665650,539   | 1987872,707       | 34,1           |
| 2013  | 1    | January   | 4212971,51    | 2665650,539       | 58,05          |
| 2013  | 2    | February  | 4047574,038   | 4212971,51        | -3,93          |
| 2013  | 3    | March     | 2282115,877   | 4047574,038       | -43,62         |
| 2013  | 4    | April     | 3483161,403   | 2282115,877       | 52,63          |
| 2013  | 5    | May       | 3510948,732   | 3483161,403       | 0,8            |
| 2013  | 6    | June      | 1662547,324   | 3510948,732       | -52,65         |
| 2013  | 7    | July      | 2699300,793   | 1662547,324       | 62,36          |
| 2013  | 8    | August    | 2738653,618   | 2699300,793       | 1,46           |
| 2013  | 9    | September | 2206725,224   | 2738653,618       | -19,42         |
| 2013  | 10   | October   | 3314600,785   | 2206725,224       | 50,2           |
| 2013  | 11   | November  | 3416234,854   | 3314600,785       | 3,07           |

**commentaire**

