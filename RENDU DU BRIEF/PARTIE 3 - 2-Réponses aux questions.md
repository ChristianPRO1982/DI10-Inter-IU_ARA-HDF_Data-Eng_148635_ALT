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

requête d'affichage :

```sql
SELECT
  g.country_name,
  SUM(f.sales_amount) AS ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
JOIN `adventureworks-dw-christian.dw.dim_reseller` r
  ON f.reseller_key = r.reseller_key
JOIN `adventureworks-dw-christian.dw.dim_geography` g
  ON r.geography_key = g.geography_key
GROUP BY g.country_name
UNION ALL
SELECT 'TOTAL' AS country_name, SUM(sales_amount) AS ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales`
ORDER BY ca ASC;
```

**résultats**

| Pays            | Chiffre d’affaires |
|-----------------|--------------------|
| Australia       | 1 594 335,38 |
| Germany         | 1 983 988,04 |
| United Kingdom  | 4 279 008,83 |
| France          | 4 607 537,94 |
| Canada          | 14 377 925,60 |
| United States   | 53 607 801,21 |
| **TOTAL**       | **80 450 596,98** |

**Analyse :**
- Les États-Unis représentent le principal marché (≈ 2/3 du CA).
- Canada et France constituent des marchés secondaires significatifs.
- La somme des CA par pays est cohérente avec le total global (contrôle d’intégrité des jointures).

## 🧭 Étape 10 — Logger les transformations dans `meta.pipeline_logs`

### SQL (création de la table META `adventureworks-dw-christian.meta.pipeline_logs`)

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.meta.pipeline_logs` (
  log_id INT64,
  step_name STRING,
  source_table STRING,
  target_table STRING,
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  rows_processed INT64,
  status STRING
);
```

### SQL (insertion des logs pour Partie 3)

```sql
INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
(log_id, step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
VALUES
  (1, 'dw_transform', 'staging.stg_dim_date', 'dw.dim_date',
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.dim_date`), 'SUCCESS'),

  (2, 'dw_transform', 'staging.stg_dim_product', 'dw.dim_product',
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.dim_product`), 'SUCCESS'),

  (3, 'dw_transform', 'staging.stg_dim_reseller', 'dw.dim_reseller',
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.dim_reseller`), 'SUCCESS'),

  (4, 'dw_transform', 'staging.stg_dim_employee', 'dw.dim_employee',
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.dim_employee`), 'SUCCESS'),

  (5, 'dw_transform', 'staging.stg_dim_geography', 'dw.dim_geography',
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.dim_geography`), 'SUCCESS'),

  (6, 'dw_transform', 'staging.stg_fact_reseller_sales', 'dw.fact_reseller_sales',
   CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.fact_reseller_sales`), 'SUCCESS');
```

### Vérification

```sql
SELECT
  log_id,
  step_name,
  source_table,
  target_table,
  rows_processed,
  status
FROM `adventureworks-dw-christian.meta.pipeline_logs`
ORDER BY log_id;
```

**résultats**

### Vérification des logs

| log_id | step_name    | source_table                     | target_table              | rows_processed | status  |
|--------|--------------|----------------------------------|---------------------------|----------------|---------|
| 1      | dw_transform | staging.stg_dim_date             | dw.dim_date               | 1826           | SUCCESS |
| 2      | dw_transform | staging.stg_dim_product          | dw.dim_product            | 395            | SUCCESS |
| 3      | dw_transform | staging.stg_dim_reseller         | dw.dim_reseller           | 701            | SUCCESS |
| 4      | dw_transform | staging.stg_dim_employee         | dw.dim_employee           | 296            | SUCCESS |
| 5      | dw_transform | staging.stg_dim_geography        | dw.dim_geography          | 655            | SUCCESS |
| 6      | dw_transform | staging.stg_fact_reseller_sales  | dw.fact_reseller_sales    | 60855          | SUCCESS |

**Remarque :**
Dans un pipeline réel orchestré (Airflow, Cloud Composer, etc.),
les colonnes `started_at` et `finished_at` seraient alimentées
par l’orchestrateur afin de mesurer précisément la durée d’exécution.
Dans ce contexte pédagogique, elles sont simulées via `CURRENT_TIMESTAMP()`.
