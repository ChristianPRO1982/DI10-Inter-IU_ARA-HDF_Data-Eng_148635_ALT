# PARTIE 3 - 2-Réponses aux questions

## 🧭 Étape 9 — Requêtes de validation (les 3 requêtes du brief)

On exécute maintenant les 3 requêtes et tu colles les résultats (au moins les premières lignes).

### 9.1 CA par année

```sql
SELECT d.annee, SUM(f.sales_amount) AS ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
JOIN `adventureworks-dw-christian.dw.dim_date` d
  ON f.order_date_key = d.date_key
GROUP BY d.annee
ORDER BY d.annee;
```

**résultats**

| Année | Chiffre d’affaires |
|--------|-------------------|
| 2010   | 489 328,58 |
| 2011   | 18 192 802,71 |
| 2012   | 28 193 631,53 |
| 2013   | 33 574 834,16 |

**Analyse :**

- 2010 correspond à une année partielle (décembre uniquement).
- Forte croissance entre 2011 et 2013.
- Le modèle DW permet bien une agrégation temporelle fiable.

### 9.2 — Top 5 produits par CA

```sql
SELECT
  p.product_name,
  SUM(f.sales_amount) AS ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
JOIN `adventureworks-dw-christian.dw.dim_product` p
  ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY ca DESC
LIMIT 5;
```

**résultats**

| Produit                        | Chiffre d’affaires |
|--------------------------------|--------------------|
| Mountain-200 Black; 38        | 3 105 726,66 |
| Mountain-200 Black; 42        | 2 646 352,67 |
| Mountain-200 Silver; 38       | 2 354 215,24 |
| Mountain-200 Silver; 42       | 2 181 044,29 |
| Mountain-200 Silver; 46       | 2 133 156,84 |

**Analyse :**
- La gamme *Mountain-200* concentre les meilleures performances.
- Les tailles 38 et 42 sont particulièrement dominantes.
- Le modèle DW permet une agrégation produit fiable via la clé `product_key`.

### 9.3 — Chiffre d’affaires par pays

problème de création de la table `adventureworks-dw-christian.dw.dim_reseller`

> correction :

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_reseller` AS
SELECT
  ResellerKey AS reseller_key,
  ResellerAlternateKey AS reseller_code,
  ResellerName AS reseller_name,
  UPPER(BusinessType) AS business_type,
  GeographyKey AS geography_key,
  IFNULL(NumberEmployees, 0) AS nb_employees,
  AnnualSales AS annual_sales,
  AnnualRevenue AS annual_revenue,
  YearOpened AS year_opened
FROM `adventureworks-dw-christian.staging.stg_dim_reseller`;
```

