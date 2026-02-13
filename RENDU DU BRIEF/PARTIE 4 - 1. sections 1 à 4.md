# PARTIE 4 - 1. sections 1 à 4

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

## 📝 Analyse — Évolution mensuelle du chiffre d’affaires

La requête utilisant `LAG()` permet de comparer le chiffre d’affaires de chaque mois avec celui du mois précédent et de calculer un **taux de croissance mensuel (%)**.

---

### 📈 Lecture globale

* 2010 correspond à une **année partielle** (uniquement décembre).
* 2011 montre une **forte volatilité**, avec des variations importantes d’un mois à l’autre.
* 2012 présente une dynamique plus équilibrée mais avec plusieurs phases de repli.
* 2013 confirme une activité soutenue mais toujours cyclique.

### 🚀 Plus forte croissance mensuelle

La plus forte croissance observée est :

* **Août 2011 : +370,62 %**

Cette hausse exceptionnelle intervient après un mois très faible (juillet 2011), ce qui amplifie mécaniquement le pourcentage d’augmentation.

On observe également des croissances significatives :

* Janvier 2011 : +214,39 %
* Mai 2011 : +100,29 %
* Juillet 2012 : +81,01 %
* Juillet 2013 : +62,36 %

👉 Cela révèle une forte **saisonnalité** et une activité irrégulière.

### 📉 Plus forte décroissance mensuelle

La plus forte baisse est :

* **Juillet 2011 : −82,29 %**

Autres baisses notables :

* Mars 2013 : −43,62 %
* Juin 2013 : −52,65 %
* Juin 2012 : −39,71 %

👉 Les mois d’été semblent particulièrement volatils, ce qui peut traduire un effet saisonnier.

### 🔎 Observation technique importante

On remarque l’absence de certains mois en 2011 (ex : février, avril, juin).
Cela signifie qu’aucune vente n’a été enregistrée ces mois-là dans le dataset, ce qui impacte directement les calculs de croissance.

Dans un contexte réel, il serait préférable :

* soit de générer une série temporelle complète via une dimension Date,
* soit d’utiliser une table calendrier pour éviter les "trous" dans l’analyse.

### 🎯 Conclusion

L’utilisation des fonctions analytiques (`LAG()` + `OVER()`) permet :

* d’identifier les phases d’expansion et de contraction ;
* de mettre en évidence la saisonnalité ;
* de fournir des indicateurs exploitables pour la direction.

Cette analyse dépasse une simple agrégation et illustre pleinement la puissance des **window functions en SQL analytique**.

## 🧭 Étape 5 — Chiffre d’affaires cumulé par année

Objectif :
Calculer le **CA cumulé mois après mois**, en repartant à zéro chaque année.

* suivre la performance annuelle en cours,
* comparer l’année N à N-1,
* faire du pilotage budgétaire.

## 5.1 — Requête CA cumulé par année

Ajoute ceci dans ton rendu :

```sql
SELECT
  annee,
  mois,
  nom_mois,

  SUM(total_revenue) AS ca_mensuel,

  -- Cumul annuel progressif
  SUM(SUM(total_revenue))
    OVER (
      PARTITION BY annee
      ORDER BY mois
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS ca_cumule

FROM `adventureworks-dw-christian.marts.mart_sales_daily`
GROUP BY annee, mois, nom_mois
ORDER BY annee, mois;
```

## 🔎 Explication technique

* `PARTITION BY annee`
  👉 le cumul redémarre chaque année.

* `ORDER BY mois`
  👉 progression chronologique.

* `UNBOUNDED PRECEDING → CURRENT ROW`
  👉 cumul depuis le début de l’année jusqu’au mois courant.

**résultats**

| annee | mois | nom_mois  | ca_mensuel    | ca_cumule       |
|-------|------|-----------|---------------|-----------------|
| 2010  | 12   | December  | 489328,5787   | 489328,5787     |
| 2011  | 1    | January   | 1538408,312   | 1538408,312     |
| 2011  | 3    | March     | 2010618,074   | 3549026,386     |
| 2011  | 5    | May       | 4027080,34    | 7576106,727     |
| 2011  | 7    | July      | 713116,6943   | 8289223,421     |
| 2011  | 8    | August    | 3356069,344   | 11645292,76     |
| 2011  | 9    | September | 882899,9424   | 12528192,71     |
| 2011  | 10   | October   | 2269116,712   | 14797309,42     |
| 2011  | 11   | November  | 1001803,77    | 15799113,19     |
| 2011  | 12   | December  | 2393689,526   | 18192802,71     |
| 2012  | 1    | January   | 3601190,714   | 3601190,714     |
| 2012  | 2    | February  | 2885359,199   | 6486549,913     |
| 2012  | 3    | March     | 1802154,213   | 8288704,126     |
| 2012  | 4    | April     | 3053816,326   | 11342520,45     |
| 2012  | 5    | May       | 2185213,215   | 13527733,67     |
| 2012  | 6    | June      | 1317541,833   | 14845275,5      |
| 2012  | 7    | July      | 2384846,591   | 17230122,09     |
| 2012  | 8    | August    | 1563955,081   | 18794077,17     |
| 2012  | 9    | September | 1865278,434   | 20659355,61     |
| 2012  | 10   | October   | 2880752,681   | 23540108,29     |
| 2012  | 11   | November  | 1987872,707   | 25527980,99     |
| 2012  | 12   | December  | 2665650,539   | 28193631,53     |
| 2013  | 1    | January   | 4212971,51    | 4212971,51      |
| 2013  | 2    | February  | 4047574,038   | 8260545,548     |
| 2013  | 3    | March     | 2282115,877   | 10542661,42     |
| 2013  | 4    | April     | 3483161,403   | 14025822,83     |
| 2013  | 5    | May       | 3510948,732   | 17536771,56     |
| 2013  | 6    | June      | 1662547,324   | 19199318,88     |
| 2013  | 7    | July      | 2699300,793   | 21898619,68     |
| 2013  | 8    | August    | 2738653,618   | 24637273,29     |
| 2013  | 9    | September | 2206725,224   | 26843998,52     |
| 2013  | 10   | October   | 3314600,785   | 30158599,3      |
| 2013  | 11   | November  | 3416234,854   | 33574834,16     |

**commentaire**

On observe que :

* **Décembre 2011 → 18 192 802,71**
* **Décembre 2012 → 28 193 631,53**
* **Novembre 2013 → 33 574 834,16**

Ces montants correspondent exactement aux chiffres d’affaires annuels calculés précédemment.

👉 Le cumul est donc parfaitement cohérent.

### 📈 Lecture analytique

Le cumul permet de visualiser :

* la vitesse de génération du chiffre d’affaires,
* les périodes d’accélération,
* les périodes de ralentissement.

Par exemple :

* En **2013**, dès mars, le cumul dépasse 10,5M.
* En juin 2013, le cumul atteint déjà ~19,2M.
* La croissance s’accélère fortement entre septembre et novembre.

Cela montre que 2013 est une année particulièrement dynamique comparée à 2011 et 2012.

### 🎯 Intérêt métier

Le cumul annuel est un indicateur clé pour :

* le pilotage budgétaire,
* la comparaison YTD (Year-To-Date),
* l’analyse de performance progressive,
* le suivi d’objectifs annuels.

Il est largement utilisé en BI pour les tableaux de bord directionnels.

### 💡 Remarque technique

L’utilisation combinée de :

* `PARTITION BY annee`
* `ORDER BY mois`
* `UNBOUNDED PRECEDING`

permet un cumul précis, contrôlé et lisible.

Cette requête illustre parfaitement la puissance des **window functions en SQL analytique**, au-delà d’un simple `GROUP BY`.

## 🧭 Étape 6 — Création du Data Mart Produits

## 6.1 — Créer la table `marts.mart_products`

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.marts.mart_products` AS
SELECT
  p.product_key,
  p.product_name,
  p.color,

  -- KPI principaux
  SUM(f.sales_amount) AS total_revenue,
  SUM(f.quantity) AS total_quantity,
  SUM(f.margin) AS total_margin,

  -- KPI calculés
  SAFE_DIVIDE(SUM(f.margin), SUM(f.sales_amount)) * 100 AS margin_pct,
  COUNT(DISTINCT f.order_number) AS nb_orders,
  AVG(f.unit_price) AS avg_unit_price,

  -- Classement par CA
  RANK() OVER (ORDER BY SUM(f.sales_amount) DESC) AS revenue_rank,

  -- Contribution au CA total
  ROUND(
    SUM(f.sales_amount) * 100.0
    / SUM(SUM(f.sales_amount)) OVER (),
    2
  ) AS revenue_contribution_pct

FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
JOIN `adventureworks-dw-christian.dw.dim_product` p
  ON f.product_key = p.product_key
GROUP BY
  p.product_key,
  p.product_name,
  p.color;
```

## 6.2 — Vérification simple

```sql
SELECT
  COUNT(*) AS nb_products,
  SUM(total_revenue) AS total_ca
FROM `adventureworks-dw-christian.marts.mart_products`;
```

**résultats**

| nb_products | total_ca     |
|-------------|--------------|
| 334         | 80450596,98  |

# ✅ Analyse rapide

✔ 334 produits actifs (cohérent avec ton filtre `ListPrice > 0`)
✔ CA total strictement égal au DW
✔ Agrégation correcte
✔ Pas de perte de données

Ton mart est sain.

# 🧭 Étape 7 — Analyse Produit avancée

## 7.1 — Top 10 produits par CA

```sql
SELECT
  product_name,
  total_revenue,
  revenue_rank,
  revenue_contribution_pct
FROM `adventureworks-dw-christian.marts.mart_products`
WHERE revenue_rank <= 10
ORDER BY revenue_rank;
```

**résultats**

| product_name               | total_revenue | revenue_rank | revenue_contribution_pct |
|----------------------------|---------------|--------------|--------------------------|
| Mountain-200 Black; 38     | 1634647,937   | 1            | 2,03                     |
| Mountain-200 Black; 38     | 1471078,722   | 2            | 1,83                     |
| Road-350-W Yellow; 48      | 1380253,877   | 3            | 1,72                     |
| Touring-1000 Blue; 60      | 1370784,224   | 4            | 1,7                      |
| Mountain-200 Black; 42     | 1360828,019   | 5            | 1,69                     |
| Mountain-200 Black; 42     | 1285524,649   | 6            | 1,6                      |
| Road-350-W Yellow; 40      | 1238754,643   | 7            | 1,54                     |
| Touring-1000 Yellow; 60    | 1184363,301   | 8            | 1,47                     |
| Mountain-200 Silver; 38    | 1181945,817   | 9            | 1,47                     |
| Mountain-200 Silver; 42    | 1175932,516   | 10           | 1,46                     |


## 7.2 — Top 10 produits par marge

```sql
SELECT
  product_name,
  total_margin,
  margin_pct
FROM `adventureworks-dw-christian.marts.mart_products`
ORDER BY total_margin DESC
LIMIT 10;
```

**résultats**

| product_name               | total_margin  | margin_pct     |
|----------------------------|---------------|----------------|
| Mountain-200 Black; 38     | 146318,3418   | 9,946329835    |
| Mountain-200 Black; 38     | 136026,3213   | 8,321444526    |
| Mountain-200 Black; 42     | 133378,9194   | 9,80130608     |
| Mountain-200 Silver; 42    | 116205,1229   | 9,88195507     |
| Mountain-200 Silver; 38    | 115895,5921   | 9,88642972     |
| Mountain-200 Silver; 46    | 114264,7275   | 9,874034728    |
| Mountain-200 Black; 42     | 108662,2271   | 8,452753292    |
| Mountain-200 Silver; 38    | 102372,3839   | 8,661343218    |
| Mountain-200 Black; 46     | 93225,7743    | 9,914721961    |
| Mountain-200 Black; 46     | 88240,992     | 8,860182875    |


## 7.3 — Analyse Pareto (80/20)

On veut identifier les produits représentant **80 % du CA total**.

Ajoute ceci :

```sql
WITH ranked_products AS (
  SELECT
    product_name,
    total_revenue,
    SUM(total_revenue)
      OVER (ORDER BY total_revenue DESC) AS cumulative_revenue,
    SUM(total_revenue)
      OVER () AS total_revenue_all
  FROM `adventureworks-dw-christian.marts.mart_products`
)

SELECT
  product_name,
  total_revenue,
  cumulative_revenue,
  ROUND(cumulative_revenue * 100 / total_revenue_all, 2) AS cumulative_pct
FROM ranked_products
WHERE cumulative_revenue * 100 / total_revenue_all <= 80
ORDER BY total_revenue DESC;
```

**résultats**

| product_name                     | total_revenue | cumulative_revenue | cumulative_pct |
|-----------------------------------|---------------|--------------------|----------------|
| Mountain-200 Black; 38           | 1634647,937   | 1634647,937        | 2,03           |
| Mountain-200 Black; 38           | 1471078,722   | 3105726,659        | 3,86           |
| Road-350-W Yellow; 48            | 1380253,877   | 4485980,536        | 5,58           |
| Touring-1000 Blue; 60            | 1370784,224   | 5856764,761        | 7,28           |
| Mountain-200 Black; 42           | 1360828,019   | 7217592,78         | 8,97           |
| Mountain-200 Black; 42           | 1285524,649   | 8503117,429        | 10,57          |
| Road-350-W Yellow; 40            | 1238754,643   | 9741872,072        | 12,11          |
| Touring-1000 Yellow; 60          | 1184363,301   | 10926235,37        | 13,58          |
| Mountain-200 Silver; 38          | 1181945,817   | 12108181,19        | 15,05          |
| Mountain-200 Silver; 42          | 1175932,516   | 13284113,71        | 16,51          |
| Mountain-100 Black; 38           | 1174622,745   | 14458736,45        | 17,97          |
| Mountain-200 Silver; 38          | 1172269,418   | 15631005,87        | 19,43          |
| Touring-1000 Blue; 46            | 1164973,183   | 16795979,05        | 20,88          |
| Mountain-100 Black; 44           | 1163352,978   | 17959332,03        | 22,32          |
| Mountain-200 Silver; 46          | 1157224,282   | 19116556,31        | 23,76          |
| Mountain-100 Black; 42           | 1102848,183   | 20219404,5         | 25,13          |
| Road-250 Red; 44                 | 1096280,079   | 21315684,57        | 26,5           |
| Mountain-100 Silver; 38          | 1094669,281   | 22410353,86        | 27,86          |
| Mountain-100 Silver; 44          | 1050610,851   | 23460964,71        | 29,16          |
| Mountain-100 Silver; 42          | 1043695,271   | 24504659,98        | 30,46          |
| Mountain-100 Black; 48           | 1041901,601   | 25546561,58        | 31,75          |
| Touring-1000 Yellow; 46          | 1016312,829   | 26562874,41        | 33,02          |
| Mountain-200 Silver; 42          | 1005111,772   | 27567986,18        | 34,27          |
| Mountain-200 Black; 46           | 995927,4345   | 28563913,61        | 35,5           |
| Mountain-200 Silver; 46          | 975932,5614   | 29539846,17        | 36,72          |
| Road-250 Black; 44               | 975155,8224   | 30515002           | 37,93          |
| Road-250 Red; 48                 | 947659,1615   | 31462661,16        | 39,11          |
| Mountain-200 Black; 46           | 940276,2343   | 32402937,39        | 40,28          |
| Road-250 Black; 44               | 913324,23     | 33316261,62        | 41,41          |
| Mountain-100 Silver; 48          | 897257,3612   | 34213518,98        | 42,53          |
| Road-250 Black; 48               | 842197,4394   | 35055716,42        | 43,57          |
| Road-250 Black; 48               | 814252,2515   | 35869968,67        | 44,59          |
| Road-150 Red; 56                 | 792228,978    | 36662197,65        | 45,57          |
| Road-250 Red; 52                 | 741801,06     | 37403998,71        | 46,49          |
| Road-350-W Yellow; 42            | 720333,7143   | 38124332,43        | 47,39          |
| Touring-1000 Blue; 50            | 713790,558    | 38838122,98        | 48,28          |
| Road-650 Black; 52               | 679332,3031   | 39517455,29        | 49,12          |
| Road-650 Red; 60                 | 675199,3686   | 40192654,66        | 49,96          |
| Touring-2000 Blue; 54            | 665395,2123   | 40858049,87        | 50,79          |
| Road-250 Black; 52               | 662322,375    | 41520372,24        | 51,61          |
| Touring-1000 Yellow; 50          | 621193,2792   | 42141565,52        | 52,38          |
| Road-450 Red; 52                 | 621103,74     | 42762669,26        | 53,15          |
| Road-250 Black; 52               | 615724,2      | 43378393,46        | 53,92          |
| Road-650 Red; 44                 | 587454,8469   | 43965848,31        | 54,65          |
| Road-650 Red; 62                 | 575619,5616   | 44541467,87        | 55,36          |
| Road-650 Red; 48                 | 575500,782    | 45116968,65        | 56,08          |
| Road-650 Black; 58               | 573356,0941   | 45690324,75        | 56,79          |
| Road-150 Red; 62                 | 566797,968    | 46257122,72        | 57,5           |
| Touring-2000 Blue; 60            | 537320,8659   | 46794443,58        | 58,17          |
| Road-450 Red; 58                 | 507978,2959   | 47302421,88        | 58,8           |
| Mountain-300 Black; 40           | 501648,8751   | 47804070,75        | 59,42          |
| Road-550-W Yellow; 48            | 485572,4091   | 48289643,16        | 60,02          |
| Mountain-300 Black; 44           | 484051,518    | 48773694,68        | 60,63          |
| Mountain-300 Black; 48           | 479071,9001   | 49252766,58        | 61,22          |
| Road-550-W Yellow; 38            | 470145,5027   | 49722912,08        | 61,81          |
| Road-550-W Yellow; 48            | 464562,3586   | 50187474,44        | 62,38          |
| Road-550-W Yellow; 38            | 463876,0582   | 50651350,5         | 62,96          |
| Road-250 Black; 58               | 448965,5625   | 51549281,62        | 64,08          |
| Road-250 Red; 58                 | 448965,5625   | 51549281,62        | 64,08          |
| Mountain-300 Black; 38           | 442477,087    | 51991758,71        | 64,63          |
| Road-250 Black; 58               | 435404,97     | 52862568,65        | 65,71          |
| Road-250 Red; 58                 | 435404,97     | 52862568,65        | 65,71          |
| HL Mountain Frame - Silver; 38   | 412969,1998   | 53275537,85        | 66,22          |
| Road-550-W Yellow; 40            | 399174,5625   | 53674712,41        | 66,72          |
| HL Mountain Frame - Black; 42    | 395972,64     | 54070685,05        | 67,21          |
| HL Mountain Frame - Silver; 38   | 387021,804    | 54457706,86        | 67,69          |
| Road-750 Black; 48               | 382157,943    | 54839864,8         | 68,17          |
| Road-550-W Yellow; 40            | 382110,3962   | 55221975,2         | 68,64          |
| HL Mountain Frame - Black; 42    | 379114,9325   | 55601090,13        | 69,11          |
| Touring-1000 Blue; 54            | 361901,826    | 55962991,96        | 69,56          |
| Road-650 Red; 52                 | 342479,826    | 56305471,78        | 69,99          |
| Road-150 Red; 48                 | 334926,072    | 57310250           | 71,24          |
| Road-150 Red; 44                 | 334926,072    | 57310250           | 71,24          |
| Road-150 Red; 52                 | 334926,072    | 57310250           | 71,24          |
| Road-650 Black; 60               | 330932,6027   | 57641182,6         | 71,65          |
| Road-650 Black; 44               | 329968,2722   | 57971150,87        | 72,06          |
| Road-350-W Yellow; 44            | 326590,08     | 58297740,95        | 72,46          |
| HL Touring Frame - Blue; 54      | 324333,1033   | 58622074,06        | 72,87          |
| HL Touring Frame - Yellow; 54    | 323268,2559   | 58945342,31        | 73,27          |
| Touring-2000 Blue; 46            | 321027,0281   | 59266369,34        | 73,67          |
| Touring-3000 Yellow; 62          | 314430,2127   | 59580799,55        | 74,06          |
| Touring-3000 Yellow; 44          | 314323,2401   | 59895122,79        | 74,45          |
| Touring-3000 Blue; 50            | 312948,7051   | 60208071,5         | 74,84          |
| Road-750 Black; 52               | 307230,7665   | 60515302,26        | 75,22          |
| Road-450 Red; 60                 | 306177,9      | 60821480,16        | 75,6           |
| Road-550-W Yellow; 42            | 304333,0875   | 61125813,25        | 75,98          |
| Road-450 Red; 44                 | 302678,724    | 61428491,98        | 76,36          |
| Road-650 Red; 44                 | 295718,5245   | 61724210,5         | 76,72          |
| Road-650 Red; 60                 | 295056,0598   | 62019266,56        | 77,09          |
| Road-650 Black; 52               | 293841,0305   | 62313107,59        | 77,46          |
| Road-550-W Yellow; 42            | 293120,184    | 62606227,77        | 77,82          |
| Touring-1000 Yellow; 54          | 290475,0888   | 62896702,86        | 78,18          |
| ML Road Frame-W - Yellow; 44     | 255122,1328   | 63151825           | 78,5           |
| Touring-3000 Blue; 54            | 249245,8693   | 63401070,86        | 78,81          |
| Touring-3000 Yellow; 50          | 247948,6129   | 63649019,48        | 79,12          |
| Road-650 Red; 62                 | 241188,8675   | 63890208,35        | 79,42          |
| Road-650 Red; 48                 | 235316,4429   | 64125524,79        | 79,71          |
| Road-650 Black; 58               | 234896,984    | 64360421,77        | 80             |

### 🔝 Top produits par chiffre d’affaires

Les 10 premiers produits représentent chacun entre **1,46 % et 2,03 %** du chiffre d’affaires total.
Le produit le plus performant est :

**Mountain-200 Black; 38**
avec environ **2,03 % du CA global**.

On observe une forte dominance de la gamme **Mountain-200**, ce qui indique une concentration du chiffre d’affaires sur une famille produit spécifique.

### 💰 Top produits par marge

Les produits générant le plus de marge appartiennent également à la gamme **Mountain-200**.

Le taux de marge moyen des top produits se situe autour de **9 % à 10 %**, ce qui montre une rentabilité homogène sur cette gamme.

### 📊 Analyse Pareto (80/20)

Pour atteindre **80 % du chiffre d’affaires total**, il faut environ :

👉 **≈ 110 produits** (jusqu’à la ligne atteignant 80 %).

Cela signifie que :

* Le chiffre d’affaires est **relativement distribué**.
* On n’est pas dans un modèle ultra concentré (type 20 % des produits = 80 % du CA).
* Environ **un tiers du catalogue** génère l’essentiel du revenu.

### 🎯 Conclusion

* Les produits Mountain dominent en volume et en marge.
* Le portefeuille est diversifié.
* L’analyse Pareto confirme une concentration modérée du chiffre d’affaires.

Cette étape illustre parfaitement l’utilisation combinée de :

* `RANK()`
* `SUM() OVER`
* cumul progressif

dans une logique BI décisionnelle.















Parfait 👌
On attaque la partie la plus stratégique : **Customer 360**.

Ici on passe du reporting produit à la **vision client décisionnelle** : LTV, churn, fréquence, statut.

---

# 🧭 Étape 8 — Création du Data Mart Revendeurs (`mart_customers`)

Objectif :
Construire une vue **Customer 360** avec :

* Lifetime Value
* Récence
* Fréquence
* Statut (Active / At Risk / Churned)

---

## 8.1 — Création de la table `marts.mart_customers`

Ajoute ceci dans ton rendu :

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.marts.mart_customers` AS

WITH max_date AS (
  SELECT MAX(order_date) AS dataset_end_date
  FROM `adventureworks-dw-christian.dw.fact_reseller_sales`
)

SELECT
  r.reseller_key,
  r.reseller_name,
  r.business_type,
  g.country_name,

  -- Temporal metrics
  MIN(f.order_date) AS first_order_date,
  MAX(f.order_date) AS last_order_date,

  -- Volume
  COUNT(DISTINCT f.order_number) AS nb_orders,
  SUM(f.quantity) AS total_items,
  SUM(f.sales_amount) AS lifetime_value,
  SUM(f.margin) AS total_margin,

  -- Average order value
  SAFE_DIVIDE(
    SUM(f.sales_amount),
    COUNT(DISTINCT f.order_number)
  ) AS avg_order_value,

  -- Order frequency (days between orders)
  SAFE_DIVIDE(
    DATE_DIFF(MAX(f.order_date), MIN(f.order_date), DAY),
    GREATEST(COUNT(DISTINCT f.order_number) - 1, 1)
  ) AS order_frequency_days,

  -- Recency
  DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) AS days_since_last_order,

  -- Customer status
  CASE
    WHEN DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) < 180 THEN 'Active'
    WHEN DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) < 365 THEN 'At Risk'
    ELSE 'Churned'
  END AS customer_status

FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
JOIN `adventureworks-dw-christian.dw.dim_reseller` r
  ON f.reseller_key = r.reseller_key
JOIN `adventureworks-dw-christian.dw.dim_geography` g
  ON r.geography_key = g.geography_key
CROSS JOIN max_date md

GROUP BY
  r.reseller_key,
  r.reseller_name,
  r.business_type,
  g.country_name,
  md.dataset_end_date;
```

---

## 8.2 — Vérification simple

```sql
SELECT
  COUNT(*) AS nb_resellers,
  SUM(lifetime_value) AS total_ltv
FROM `adventureworks-dw-christian.marts.mart_customers`;
```

**résultats**

| nb_resellers | total_ltv     |
|--------------|--------------:|
| 635          | 80450596,98   |

Parfait 👌
On termine fort.

---

# ✅ Vérification Customer 360

| nb_resellers |   total_ltv |
| ------------ | ----------: |
| 635          | 80450596,98 |

✔ 635 revendeurs
✔ LTV total = CA global
✔ Aucune perte d’information
✔ Agrégation correcte

`mart_customers` est sain.

# 🧭 Étape 9 — Analyse stratégique Revendeurs

Exploitation du mart pour une direction commerciale.

## 9.1 — Répartition des statuts

```sql
SELECT
  customer_status,
  COUNT(*) AS nb_resellers,
  SUM(lifetime_value) AS total_ltv,
  ROUND(AVG(lifetime_value), 2) AS avg_ltv
FROM `adventureworks-dw-christian.marts.mart_customers`
GROUP BY customer_status
ORDER BY total_ltv DESC;
```

**résultats**

| customer_status | nb_resellers | total_ltv     | avg_ltv    |
|-----------------|-------------:|--------------:|-----------:|
| Active          | 466          | 67389743,62   | 144613,18  |
| Churned         | 142          | 12383653,83   | 87208,83   |
| At Risk         | 27           | 677199,5325   | 25081,46   |

## 9.2 — Top 10 revendeurs par Lifetime Value

```sql
SELECT
  reseller_name,
  country_name,
  lifetime_value,
  total_margin,
  customer_status
FROM `adventureworks-dw-christian.marts.mart_customers`
ORDER BY lifetime_value DESC
LIMIT 10;
```

**résultats**

| reseller_name                         | country_name   | lifetime_value | total_margin   | customer_status |
|---------------------------------------|---------------|---------------:|---------------:|-----------------|
| Brakes and Gears                     | United States | 877107,1923    | 62737,6359     | Active          |
| Excellent Riding Supplies            | United States | 853849,1795    | -19428,9804    | Active          |
| Vigorous Exercise Company            | Canada        | 841908,7708    | 2130,2508      | Active          |
| Totes & Baskets Company              | United States | 816755,5763    | -18639,5225    | Active          |
| Retail Mall                          | Canada        | 799277,8953    | -22993,418     | Active          |
| Corner Bicycle Supply                | Canada        | 787773,0436    | -13782,5107    | Active          |
| Outdoor Equipment Store              | United States | 746317,5293    | -27918,4705    | Active          |
| Thorough Parts and Repair Services   | United States | 740985,8338    | -24512,8724    | Active          |
| Health Spa; Limited                  | Canada        | 730798,7139    | -26332,8171    | Active          |
| Fitness Toy Store                    | United States | 727272,6494    | -26986,3683    | Active          |

## 9.3 — Segmentation par quartiles (NTILE)

On segmente les revendeurs en 4 groupes selon leur LTV.

```sql
SELECT
  reseller_name,
  lifetime_value,
  NTILE(4) OVER (ORDER BY lifetime_value DESC) AS ltv_quartile
FROM `adventureworks-dw-christian.marts.mart_customers`
ORDER BY lifetime_value DESC;
```

**résultats**

*Résultats partiels car beaucoup de lignes. Il y a que les 5 premières et 5 dernières lignes pour les 3 premiers quartiles*

| reseller_name | lifetime_value | ltv_quartile |
| ------------- | -------------- | ------------ |
| Brakes and Gears | 877107,1923 | 1 |
| Excellent Riding Supplies | 853849,1795 | 1 |
| Vigorous Exercise Company | 841908,7708 | 1 |
| Totes & Baskets Company | 816755,5763 | 1 |
| Retail Mall | 799277,8953 | 1 |
| [...] | [...] | [...] |
| Bicycle Outfitters | 182730,2472 | 1 |
| Extreme Riding Supplies | 182025,0622 | 1 |
| Immense Manufacturing Company | 181062,7128 | 1 |
| Elite Bikes | 179831,3507 | 1 |
| Stock Parts and Supplies | 178066,6502 | 1 |
| Journey Sporting Goods | 175502,1574 | 2 |
| Convenient Sales and Service | 173228,2944 | 2 |
| Finer Parts Shop | 172227,7313 | 2 |
| Petroleum Products Distributors | 169212,2208 | 2 |
| Unified Sports Company | 165815,3344 | 2 |
| [...] | [...] | [...] |
| Sharp Bikes | 48761,856 | 2 |
| Wonderful Bikes Inc. | 47318,0679 | 2 |
| Machines & Cycles Store | 46616,6681 | 2 |
| Scratch-Resistant Finishes Company | 45769,5797 | 2 |
| Famous Bike Shop | 45502,9712 | 2 |
| Sports Products Store | 45287,6826 | 3 |
| Number One Bike Co. | 44990,0055 | 3 |
| Sports Commodities | 44945,4676 | 3 |
| This Area Sporting Goods | 44568,8113 | 3 |
| Genuine Bike Shop | 43911,1524 | 3 |
| [...] | [...] | [...] |
| More Bikes! | 7719,6876 | 3 |
| Nearby Sporting Goods | 7695,7047 | 3 |
| Racing Bike Outlet | 7643,9962 | 3 |
| All Seasons Sports Supply | 7436,268 | 3 |
| Twin Cycles | 7337,598 | 3 |
| Acclaimed Bicycle Company | 7300,8288 | 4 |
| Vigorous Sports Store | 7183,5787 | 4 |
| Leisure Clearing House | 7047,5964 | 4 |
| Commendable Bikes | 6962,3778 | 4 |
| Countryside Company | 6947,535 | 4 |
| Ideal Components | 6678,108 | 4 |
| Bicycle Accessories and Kits | 6587,3763 | 4 |
| Fleet Bikes | 6417,1108 | 4 |
| Local Sales and Rental | 6407,892 | 4 |
| Fast Services | 6369 | 4 |
| Cycle Merchants | 6287,7839 | 4 |
| Sports Store | 6278,4211 | 4 |
| Economy Bikes Company | 6221,0526 | 4 |
| Mountain Emporium | 6214,259 | 4 |
| Mechanical Sports Center | 6016,3075 | 4 |
| Finish and Sealant Products | 5925,7862 | 4 |
| Futuristic Bikes | 5776,9527 | 4 |
| Retread Tire Company | 5751,6151 | 4 |
| New Bikes Company | 5670,2261 | 4 |
| Top Bike Market | 5641,2108 | 4 |
| Extended Tours | 5615,5794 | 4 |
| City Manufacturing | 5575,2477 | 4 |
| Bicycle Warehouse Inc. | 5426,7938 | 4 |

**📝 Analyse — Customer 360 & Segmentation Revendeurs**

### 📊 Répartition des statuts

| Statut  | Nb  | % approx | Part du CA |
| ------- | --- | -------- | ---------- |
| Active  | 466 | ~73 %    | ~83,8 %    |
| Churned | 142 | ~22 %    | ~15,4 %    |
| At Risk | 27  | ~4 %     | ~0,8 %     |

### 🔎 Lecture stratégique

* La majorité des revendeurs sont **actifs (73 %)**
* Ils génèrent **près de 84 % du chiffre d’affaires total**
* Les clients churned représentent 22 % du portefeuille mais seulement 15 % du CA

👉 Le risque principal n’est pas massif, mais le portefeuille churned reste significatif.

Le segment **At Risk** est faible en volume et en CA → opportunité de réactivation ciblée.

### 🏆 Top revendeurs

Le premier revendeur :

**Brakes and Gears (US)**
LTV ≈ 877K

Les 10 premiers revendeurs :

* Majoritairement US / Canada
* Tous sont actuellement **Active**
* Certains ont une marge négative malgré un fort CA

👉 Cela peut indiquer :

* pression concurrentielle
* structure de coûts élevée
* remises importantes

### 📈 Segmentation par quartiles (NTILE)

* Quartile 1 = top 25 % des revendeurs
* Quartile 4 = bottom 25 %

Avec 635 revendeurs :

👉 Chaque quartile contient environ **159 revendeurs**

### Lecture :

* Le quartile 1 concentre la majorité du chiffre d’affaires.
* Le quartile 4 regroupe des revendeurs à très faible contribution (< 7K LTV).
* L’écart entre le top et le bas de portefeuille est très important.

👉 Cela confirme une distribution **asymétrique**, typique d’un portefeuille B2B.

### 🎯 Conclusion stratégique

* Le chiffre d’affaires repose principalement sur les revendeurs actifs.
* Une minorité de revendeurs génère l’essentiel du CA.
* La gestion du churn et la montée en gamme du quartile 2 pourraient améliorer la performance globale.
