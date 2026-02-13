# PARTIE 5 - 1. sections 1 à 4

## 🧭 Étape 1 — Audit & Optimisation des tables

## 1.1 — Audit du partitionnement et du clustering

```sql
WITH all_tables AS (
  SELECT
    'dw' AS dataset_name,
    table_name,
    ddl
  FROM `adventureworks-dw-christian.dw.INFORMATION_SCHEMA.TABLES`

  UNION ALL

  SELECT
    'marts' AS dataset_name,
    table_name,
    ddl
  FROM `adventureworks-dw-christian.marts.INFORMATION_SCHEMA.TABLES`
)
SELECT
  dataset_name,
  table_name,
  REGEXP_EXTRACT(ddl, r'PARTITION BY\s+([^\n]+)') AS partition_by,
  REGEXP_EXTRACT(ddl, r'CLUSTER BY\s+([^\n]+)') AS cluster_by
FROM all_tables
ORDER BY dataset_name, table_name;
```

**résultats**

| dataset_name | table_name           | partition_by | cluster_by                    |
|--------------|----------------------|--------------|-------------------------------|
| dw           | dim_date             |              |                               |
| dw           | dim_employee         |              |                               |
| dw           | dim_geography        |              |                               |
| dw           | dim_product          |              |                               |
| dw           | dim_reseller         |              |                               |
| dw           | fact_reseller_sales  | order_date   | product_key, reseller_key     |
| marts        | mart_customers       |              | business_type, country_name   |
| marts        | mart_products        |              |                               |
| marts        | mart_sales_daily     | order_date   | country_name                  |

**✅ audit OK et conforme**

## 🧭 Étape 1.2 — Analyse des coûts et impact du partitionnement

### 1.2.1 — Comparer une requête sans filtre vs avec filtre date

**Requête A — sans filtre (scanne tout)**

```sql
SELECT
  SUM(sales_amount) AS total_ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales`;
```

**Requête B — avec filtre sur la partition (scanne une partie)**

```sql
SELECT
  SUM(sales_amount) AS total_ca_2013
FROM `adventureworks-dw-christian.dw.fact_reseller_sales`
WHERE order_date BETWEEN '2013-01-01' AND '2013-12-31';
```

### 1.2.2 — 📊 Résultats observés

| Requête         | Octets traités | Octets facturés | Slot ms |
| --------------- | -------------- | --------------- | ------- |
| A (sans filtre) | 475,43 Ko      | 10 Mo           | 149 ms  |
| B (filtre 2013) | 445,94 Ko      | 10 Mo           | 58 ms   |

**🔎 Analyse des coûts et du partitionnement**

La comparaison entre une requête sans filtre et une requête filtrée sur la colonne de partition montre :

* Une légère réduction des données traitées (475 Ko → 446 Ko).
* Une amélioration du temps d’exécution (149 ms → 58 ms).
* Aucun impact sur les octets facturés (10 Mo), en raison du minimum de facturation BigQuery.

Le gain est limité ici car la table est de petite taille (~60 000 lignes).
Dans un environnement réel avec des tables de plusieurs Go ou To, le partitionnement permettrait une réduction massive des données scannées et donc des coûts.

🎯 Conclusion :

* Partitionnement correctement implémenté
* Impact visible sur la performance
* Impact financier limité ici à cause du faible volume

## 🧭 Étape 2 — Stored Procedure `meta.sp_refresh_dw()` (Staging → DW)

### 2.1 — Créer la procédure `meta.sp_refresh_dw()`

```sql
CREATE OR REPLACE PROCEDURE `adventureworks-dw-christian.meta.sp_refresh_dw`()
BEGIN
  DECLARE start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP();
  DECLARE rows_count INT64 DEFAULT 0;

  BEGIN
    -- 1) dim_date
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_date` AS
    SELECT
      DateKey AS date_key,
      FullDateAlternateKey AS date_complete,
      DayNumberOfWeek AS num_jour_semaine,
      EnglishDayNameOfWeek AS jour_semaine,
      DayNumberOfMonth AS jour_du_mois,
      MonthNumberOfYear AS num_mois,
      EnglishMonthName AS nom_mois,
      CalendarQuarter AS trimestre,
      CalendarYear AS annee,
      FiscalQuarter AS trimestre_fiscal,
      FiscalYear AS annee_fiscale
    FROM `adventureworks-dw-christian.staging.stg_dim_date`;

    -- 2) dim_product
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_product` AS
    SELECT
      ProductKey AS product_key,
      ProductAlternateKey AS product_alternate_key,
      EnglishProductName AS product_name,
      Color AS color,
      StandardCost AS standard_cost,
      ListPrice AS list_price,
      ProductSubcategoryKey AS product_subcategory_key,
      IFNULL(ModelName, 'Unknown') AS model_name,
      IFNULL(Status, 'Unknown') AS product_status
    FROM `adventureworks-dw-christian.staging.stg_dim_product`
    WHERE ListPrice > 0;

    -- 3) dim_reseller
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_reseller` AS
    SELECT
      ResellerKey AS reseller_key,
      ResellerName AS reseller_name,
      BusinessType AS business_type,
      IFNULL(BusinessType, 'Unknown') AS business_type_clean,
      GeographyKey AS geography_key
    FROM `adventureworks-dw-christian.staging.stg_dim_reseller`;

    -- 4) dim_employee
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_employee` AS
    SELECT
      EmployeeKey AS employee_key,
      FirstName AS first_name,
      LastName AS last_name,
      CONCAT(FirstName, ' ', LastName) AS full_name,
      Title AS title,
      DepartmentName AS department_name
    FROM `adventureworks-dw-christian.staging.stg_dim_employee`;

    -- 5) dim_geography
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_geography` AS
    SELECT
      GeographyKey AS geography_key,
      City AS city,
      StateProvinceName AS state_province_name,
      CountryRegionCode AS country_region_code,
      EnglishCountryRegionName AS country_name
    FROM `adventureworks-dw-christian.staging.stg_dim_geography`;

    -- 6) fact_reseller_sales (partition + cluster)
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.fact_reseller_sales`
    PARTITION BY order_date
    CLUSTER BY product_key, reseller_key
    AS
    SELECT
      SalesOrderNumber AS order_number,
      SalesOrderLineNumber AS order_line_number,

      OrderDateKey AS order_date_key,
      PARSE_DATE('%Y%m%d', CAST(OrderDateKey AS STRING)) AS order_date,

      ProductKey AS product_key,
      ResellerKey AS reseller_key,
      EmployeeKey AS employee_key,

      OrderQuantity AS quantity,
      UnitPrice AS unit_price,
      ExtendedAmount AS sales_amount,
      UnitPriceDiscountPct AS discount_pct,
      DiscountAmount AS discount_amount,
      ProductStandardCost AS standard_cost,
      TotalProductCost AS total_cost,
      TaxAmt AS tax_amount,
      Freight AS freight,

      (ExtendedAmount - TotalProductCost) AS margin
    FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`;

    -- 7) Logger
    SET rows_count = (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.fact_reseller_sales`);

    INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
      (step_name, target_table, started_at, finished_at, rows_processed, status)
    VALUES
      ('sp_refresh_dw', 'dw.*', start_ts, CURRENT_TIMESTAMP(), rows_count, 'SUCCESS');

  EXCEPTION WHEN ERROR THEN
    INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
      (step_name, target_table, started_at, finished_at, rows_processed, status)
    VALUES
      ('sp_refresh_dw', 'dw.*', start_ts, CURRENT_TIMESTAMP(), 0, 'ERROR');

    RAISE;
  END;
END;
```

## 2.2 — Test de la procédure

```sql
CALL `adventureworks-dw-christian.meta.sp_refresh_dw`();
```

## 2.3 — Vérifier les logs

```sql
SELECT *
FROM `adventureworks-dw-christian.meta.pipeline_logs`
ORDER BY finished_at DESC
LIMIT 5;
```

**résultats**

| log_id | step_name      | source_table                         | target_table                 | started_at           | finished_at          | rows_processed | status  |
|--------|---------------|--------------------------------------|-----------------------------|----------------------|----------------------|---------------|---------|
|        | sp_refresh_dw |                                      | dw.*                        | 13/02/2026 11:07:09  | 13/02/2026 11:07:27  | 60855         | SUCCESS |
| 6      | dw_transform  | staging.stg_fact_reseller_sales      | dw.fact_reseller_sales      | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 60855         | SUCCESS |
| 1      | dw_transform  | staging.stg_dim_date                 | dw.dim_date                 | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 1826          | SUCCESS |
| 2      | dw_transform  | staging.stg_dim_product              | dw.dim_product              | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 395           | SUCCESS |
| 5      | dw_transform  | staging.stg_dim_geography            | dw.dim_geography            | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 655           | SUCCESS |

> la procédure s’exécute correctement

## 🧭 Étape 3 — Stored Procedure `meta.sp_refresh_marts()` (DW → Marts)

## 3.1 — Créer la procédure `meta.sp_refresh_marts()`

```sql
CREATE OR REPLACE PROCEDURE `adventureworks-dw-christian.meta.sp_refresh_marts`()
BEGIN
  DECLARE start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP();
  DECLARE rows_sales_daily INT64 DEFAULT 0;
  DECLARE rows_products INT64 DEFAULT 0;
  DECLARE rows_customers INT64 DEFAULT 0;
  DECLARE rows_total INT64 DEFAULT 0;

  BEGIN
    -- 1) mart_sales_daily (spec inchangée, OR REPLACE OK)
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

      COUNT(DISTINCT f.order_number) AS nb_orders,
      COUNT(*) AS nb_lines,
      SUM(f.quantity) AS total_quantity,

      SUM(f.sales_amount) AS total_revenue,
      SUM(f.total_cost) AS total_cost,
      SUM(f.margin) AS total_margin,
      SUM(f.discount_amount) AS total_discount,
      SUM(f.tax_amount) AS total_tax,
      SUM(f.freight) AS total_freight,

      SAFE_DIVIDE(SUM(f.sales_amount), COUNT(DISTINCT f.order_number)) AS avg_order_value,
      SAFE_DIVIDE(SUM(f.margin), SUM(f.sales_amount)) * 100 AS margin_pct
    FROM `adventureworks-dw-christian.dw.fact_reseller_sales` AS f
    JOIN `adventureworks-dw-christian.dw.dim_date` AS d
      ON f.order_date_key = CAST(d.date_key AS INT64)
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

    -- 2) mart_products (DROP required when changing clustering spec)
    DROP TABLE IF EXISTS `adventureworks-dw-christian.marts.mart_products`;

    CREATE TABLE `adventureworks-dw-christian.marts.mart_products`
    CLUSTER BY product_name
    AS
    SELECT
      p.product_key,
      p.product_name,
      p.color,

      SUM(f.sales_amount) AS total_revenue,
      SUM(f.quantity) AS total_quantity,
      SUM(f.margin) AS total_margin,

      SAFE_DIVIDE(SUM(f.margin), SUM(f.sales_amount)) * 100 AS margin_pct,
      COUNT(DISTINCT f.order_number) AS nb_orders,
      AVG(f.unit_price) AS avg_unit_price,

      RANK() OVER (ORDER BY SUM(f.sales_amount) DESC) AS revenue_rank,

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

    -- 3) mart_customers (spec inchangée, OR REPLACE OK)
    CREATE OR REPLACE TABLE `adventureworks-dw-christian.marts.mart_customers`
    CLUSTER BY business_type, country_name
    AS
    WITH max_date AS (
      SELECT MAX(order_date) AS dataset_end_date
      FROM `adventureworks-dw-christian.dw.fact_reseller_sales`
    )
    SELECT
      r.reseller_key,
      r.reseller_name,
      r.business_type,
      g.country_name,

      MIN(f.order_date) AS first_order_date,
      MAX(f.order_date) AS last_order_date,

      COUNT(DISTINCT f.order_number) AS nb_orders,
      SUM(f.quantity) AS total_items,
      SUM(f.sales_amount) AS lifetime_value,
      SUM(f.margin) AS total_margin,

      SAFE_DIVIDE(SUM(f.sales_amount), COUNT(DISTINCT f.order_number)) AS avg_order_value,

      SAFE_DIVIDE(
        DATE_DIFF(MAX(f.order_date), MIN(f.order_date), DAY),
        GREATEST(COUNT(DISTINCT f.order_number) - 1, 1)
      ) AS order_frequency_days,

      DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) AS days_since_last_order,

      CASE
        WHEN DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) < 180 THEN 'Active'
        WHEN DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) < 365 THEN 'At Risk'
        ELSE 'Churned'
      END AS customer_status
    FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
    JOIN `adventureworks-dw-christian.dw.dim_reseller` r
      ON f.reseller_key = r.reseller_key
    JOIN `adventureworks-dw-christian.dw.dim_geography` AS g
      ON r.geography_key = g.geography_key
    CROSS JOIN max_date md
    GROUP BY
      r.reseller_key,
      r.reseller_name,
      r.business_type,
      g.country_name,
      md.dataset_end_date;

    -- 4) Row counts
    SET rows_sales_daily = (SELECT COUNT(*) FROM `adventureworks-dw-christian.marts.mart_sales_daily`);
    SET rows_products = (SELECT COUNT(*) FROM `adventureworks-dw-christian.marts.mart_products`);
    SET rows_customers = (SELECT COUNT(*) FROM `adventureworks-dw-christian.marts.mart_customers`);
    SET rows_total = rows_sales_daily + rows_products + rows_customers;

    -- 5) Logger
    INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
      (step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
    VALUES
      ('sp_refresh_marts', 'dw.*', 'marts.*', start_ts, CURRENT_TIMESTAMP(), rows_total, 'SUCCESS');

  EXCEPTION WHEN ERROR THEN
    INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
      (step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
    VALUES
      ('sp_refresh_marts', 'dw.*', 'marts.*', start_ts, CURRENT_TIMESTAMP(), 0, 'ERROR');
    RAISE;
  END;
END;
```

## 3.2 — Test

```sql
CALL `adventureworks-dw-christian.meta.sp_refresh_marts`();
```

## 3.3 — Logs

```sql
SELECT *
FROM `adventureworks-dw-christian.meta.pipeline_logs`
ORDER BY finished_at DESC
LIMIT 5;
```

| log_id | step_name        | source_table              | target_table     | started_at           | finished_at          | rows_processed | status  |
|--------|------------------|---------------------------|------------------|----------------------|----------------------|---------------|---------|
|        | sp_refresh_marts | dw.*                      | marts.*          | 13/02/2026 11:20:04  | 13/02/2026 11:20:19  | 1396          | SUCCESS |
|        | sp_refresh_marts | dw.*                      | marts.*          | 13/02/2026 11:18:07  | 13/02/2026 11:18:13  | 0             | ERROR   |
|        | sp_refresh_marts |                           | marts.*          | 13/02/2026 11:12:48  | 13/02/2026 11:12:54  | 0             | ERROR   |
|        | sp_refresh_dw    |                           | dw.*             | 13/02/2026 11:07:09  | 13/02/2026 11:07:27  | 60855         | SUCCESS |
| 5      | dw_transform     | staging.stg_dim_geography | dw.dim_geography | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 655           | SUCCESS |

> **validé :** `sp_refresh_marts` passe en SUCCESS et ton logging est propre.

# 🧭 Étape 4 — Procédure “pipeline complet” `meta.sp_run_full_pipeline()`

## 4.1 — Créer la procédure `meta.sp_run_full_pipeline()`

```sql
CREATE OR REPLACE PROCEDURE `adventureworks-dw-christian.meta.sp_run_full_pipeline`()
BEGIN
  DECLARE start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP();
  DECLARE rows_fact INT64 DEFAULT 0;
  DECLARE rows_marts INT64 DEFAULT 0;

  BEGIN
    -- Run DW
    CALL `adventureworks-dw-christian.meta.sp_refresh_dw`();

    -- Run Marts
    CALL `adventureworks-dw-christian.meta.sp_refresh_marts`();

    -- Metrics (simple but useful)
    SET rows_fact = (SELECT COUNT(*) FROM `adventureworks-dw-christian.dw.fact_reseller_sales`);
    SET rows_marts =
      (SELECT COUNT(*) FROM `adventureworks-dw-christian.marts.mart_sales_daily`)
      + (SELECT COUNT(*) FROM `adventureworks-dw-christian.marts.mart_products`)
      + (SELECT COUNT(*) FROM `adventureworks-dw-christian.marts.mart_customers`);

    -- Global log
    INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
      (step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
    VALUES
      ('sp_run_full_pipeline', 'staging.*', 'dw.* + marts.*', start_ts, CURRENT_TIMESTAMP(),
       rows_fact + rows_marts, 'SUCCESS');

  EXCEPTION WHEN ERROR THEN
    INSERT INTO `adventureworks-dw-christian.meta.pipeline_logs`
      (step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
    VALUES
      ('sp_run_full_pipeline', 'staging.*', 'dw.* + marts.*', start_ts, CURRENT_TIMESTAMP(),
       0, 'ERROR');

    RAISE;
  END;
END;
```

## 4.2 — Test

```sql
CALL `adventureworks-dw-christian.meta.sp_run_full_pipeline`();
```

## 4.3 — Vérifier les logs

```sql
SELECT *
FROM `adventureworks-dw-christian.meta.pipeline_logs`
ORDER BY finished_at DESC
LIMIT 10;
```

**résultats**

| log_id | step_name            | source_table                         | target_table               | started_at           | finished_at          | rows_processed | status  |
|--------|----------------------|--------------------------------------|----------------------------|----------------------|----------------------|----------------|---------|
|        | sp_run_full_pipeline | staging.*                            | dw.* + marts.*             | 13/02/2026 12:09:02  | 13/02/2026 12:09:38  | 62251          | SUCCESS |
|        | sp_refresh_marts     | dw.*                                 | marts.*                    | 13/02/2026 12:09:21  | 13/02/2026 12:09:35  | 1396           | SUCCESS |
|        | sp_refresh_dw        |                                      | dw.*                       | 13/02/2026 12:09:02  | 13/02/2026 12:09:19  | 60855          | SUCCESS |
|        | sp_refresh_marts     | dw.*                                 | marts.*                    | 13/02/2026 11:20:04  | 13/02/2026 11:20:19  | 1396           | SUCCESS |
|        | sp_refresh_marts     | dw.*                                 | marts.*                    | 13/02/2026 11:18:07  | 13/02/2026 11:18:13  | 0              | ERROR   |
|        | sp_refresh_marts     |                                      | marts.*                    | 13/02/2026 11:12:48  | 13/02/2026 11:12:54  | 0              | ERROR   |
|        | sp_refresh_dw        |                                      | dw.*                       | 13/02/2026 11:07:09  | 13/02/2026 11:07:27  | 60855          | SUCCESS |
| 4      | dw_transform         | staging.stg_dim_employee             | dw.dim_employee            | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 296            | SUCCESS |
| 2      | dw_transform         | staging.stg_dim_product              | dw.dim_product             | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 395            | SUCCESS |
| 6      | dw_transform         | staging.stg_fact_reseller_sales      | dw.fact_reseller_sales     | 12/02/2026 14:55:09  | 12/02/2026 14:55:09  | 60855          | SUCCESS |

1) Exécution globale

* `sp_run_full_pipeline` = **SUCCESS** ✅
* Durée : ~36s (12:09:02 → 12:09:38) ✅

 2) Sous-procédures bien chaînées

* `sp_refresh_dw` ✅ (60855 lignes)
* `sp_refresh_marts` ✅ (1396 lignes)

Donc la chaîne **staging → dw → marts** est opérationnelle.

3) Cohérence des volumes

* `rows_processed` global = **62251**
  = 60855 (fact DW) + 1396 (3 marts)
  ✅ cohérent au chiffre près.

### 📝 Commentaire - Partie 5 sections 1–4

Les tables principales du DW et des marts sont correctement optimisées via partitionnement et clustering.
Les tests de coût montrent un gain limité sur ce dataset (faible volumétrie + minimum de facturation BigQuery), mais la logique de partition pruning est validée.

Deux procédures ont été mises en place :

* `meta.sp_refresh_dw()` : reconstruction du dataset `dw` depuis `staging`
* `meta.sp_refresh_marts()` : reconstruction du dataset `marts` depuis `dw`

Une procédure de pipeline complet `meta.sp_run_full_pipeline()` orchestre les deux étapes.
Les logs stockés dans `meta.pipeline_logs` assurent la traçabilité, et les volumes traités sont cohérents (60855 lignes DW + 1396 lignes marts = 62251).
