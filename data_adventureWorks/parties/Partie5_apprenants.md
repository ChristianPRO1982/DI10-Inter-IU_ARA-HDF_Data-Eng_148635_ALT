# Brief : Construction d'un Data Warehouse et de Data Marts avec BigQuery

## Partie 0 — Veille : Concepts DW, OLAP et BigQuery

---

# Partie 5 — Optimisation, automatisation & documentation

## Objectifs

À l'issue de cette partie, vous serez capable de :

- **optimiser** les coûts et performances des tables BigQuery ;
- **automatiser** le pipeline ELT avec des Stored Procedures ;
- **planifier** les exécutions avec des Scheduled Queries ;
- créer un **monitoring** du pipeline ;
- **documenter** l'architecture complète.

---

## 1. Optimisation des tables

### 1.1 Audit du partitionnement et du clustering

Vérifiez que vos tables sont correctement optimisées :

```sql
-- Lister les tables avec leurs options de partitionnement et clustering
SELECT
    table_schema,
    table_name,
    ARRAY_TO_STRING(
        ARRAY(SELECT option_value FROM UNNEST(t.option_list)),
        ', '
    ) AS options
FROM (
    SELECT
        table_schema,
        table_name,
        ARRAY_AGG(STRUCT(option_name, option_value)) AS option_list
    FROM `INFORMATION_SCHEMA.TABLE_OPTIONS`
    WHERE table_schema IN ('dw', 'marts')
    GROUP BY 1, 2
) t
ORDER BY table_schema, table_name;
```

**Recommandations de partitionnement et clustering :**

| Table | Partitionnement | Clustering |
|-------|-----------------|------------|
| `dw.fact_reseller_sales` | `order_date` (DATE) | `product_key, reseller_key` |
| `marts.mart_sales_daily` | `order_date` (DATE) | `country_name` |
| `marts.mart_products` | Aucun (petite table) | `product_name` |
| `marts.mart_customers` | Aucun (petite table) | `business_type, country_name` |

- [ ] Vérifier le partitionnement de chaque table
- [ ] Ajouter le clustering manquant si nécessaire

### 1.2 Analyser les coûts des requêtes

```sql
-- Estimation du volume scanné par une requête (dry run via la console)
-- Dans la console BigQuery, la barre verte en haut à droite indique
-- le volume de données qui sera scanné.

-- Comparer ces deux requêtes :
-- Requête A : sans filtre date (scanne tout)
SELECT SUM(sales_amount)
FROM dw.fact_reseller_sales;

-- Requête B : avec filtre date (scanne une partition)
SELECT SUM(sales_amount)
FROM dw.fact_reseller_sales
WHERE order_date BETWEEN '2013-01-01' AND '2013-12-31';
```

- [ ] Comparer le volume scanné des deux requêtes (en MB)
- [ ] Documenter le gain de performance du partitionnement

### 1.3 Bonnes pratiques coûts BigQuery

Vérifiez que vos requêtes respectent ces règles :

- [ ] Jamais de `SELECT *` sur les tables volumineuses
- [ ] Toujours filtrer sur la colonne de partitionnement quand possible
- [ ] Utiliser `LIMIT` pour les requêtes exploratoires
- [ ] Préférer les agrégations dans les marts plutôt que sur la table de faits brute

---

## 2. Stored Procedures

### 2.1 Procédure de refresh Staging → DW

Créez une procédure qui reconstruit les tables DW depuis le staging :

```sql
CREATE OR REPLACE PROCEDURE meta.sp_refresh_dw()
BEGIN
    DECLARE start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP();
    DECLARE rows_count INT64;

    -- 1. Refresh dim_date
    CREATE OR REPLACE TABLE dw.dim_date AS
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
    FROM staging.stg_dim_date;

    -- 2. Refresh dim_product
    -- À compléter : reprendre votre requête de la Partie 3

    -- 3. Refresh dim_reseller
    -- À compléter

    -- 4. Refresh dim_employee
    -- À compléter

    -- 5. Refresh dim_geography
    -- À compléter

    -- 6. Refresh fact_reseller_sales
    -- À compléter : reprendre votre requête de la Partie 3

    -- 7. Logger
    SET rows_count = (SELECT COUNT(*) FROM dw.fact_reseller_sales);

    INSERT INTO meta.pipeline_logs (step_name, target_table, started_at, finished_at, rows_processed, status)
    VALUES ('sp_refresh_dw', 'dw.*', start_ts, CURRENT_TIMESTAMP(), rows_count, 'SUCCESS');
END;
```

- [ ] Créer la procédure `meta.sp_refresh_dw()`
- [ ] Tester : `CALL meta.sp_refresh_dw();`
- [ ] Vérifier les logs : `SELECT * FROM meta.pipeline_logs ORDER BY finished_at DESC LIMIT 5;`

### 2.2 Procédure de refresh DW → Marts

```sql
CREATE OR REPLACE PROCEDURE meta.sp_refresh_marts()
BEGIN
    DECLARE start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP();

    -- 1. Refresh mart_sales_daily
    -- À compléter : reprendre votre requête de la Partie 4

    -- 2. Refresh mart_products
    -- À compléter

    -- 3. Refresh mart_customers
    -- À compléter

    -- 4. Logger
    INSERT INTO meta.pipeline_logs (step_name, target_table, started_at, finished_at, rows_processed, status)
    VALUES ('sp_refresh_marts', 'marts.*', start_ts, CURRENT_TIMESTAMP(),
            (SELECT COUNT(*) FROM marts.mart_sales_daily), 'SUCCESS');
END;
```

- [ ] Créer la procédure `meta.sp_refresh_marts()`
- [ ] Tester : `CALL meta.sp_refresh_marts();`

### 2.3 Procédure d'orchestration complète

```sql
CREATE OR REPLACE PROCEDURE meta.sp_run_full_pipeline()
BEGIN
    DECLARE start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP();

    -- Étape 1 : Refresh DW
    CALL meta.sp_refresh_dw();

    -- Étape 2 : Refresh Marts
    CALL meta.sp_refresh_marts();

    -- Étape 3 : Log global
    INSERT INTO meta.pipeline_logs (step_name, started_at, finished_at, status)
    VALUES ('sp_run_full_pipeline', start_ts, CURRENT_TIMESTAMP(), 'SUCCESS');
END;
```

- [ ] Créer `meta.sp_run_full_pipeline()`
- [ ] Tester le pipeline complet : `CALL meta.sp_run_full_pipeline();`
- [ ] Vérifier les logs

---

## 3. Scheduled Queries

### 3.1 Planifier le pipeline

Configurez une Scheduled Query pour exécuter le pipeline automatiquement :

1. Dans la console BigQuery, aller dans **Scheduled Queries**
2. Créer une nouvelle requête planifiée :
   - **Nom** : `daily_pipeline_refresh`
   - **Requête** : `CALL meta.sp_run_full_pipeline();`
   - **Fréquence** : Tous les jours à 06:00 UTC
   - **Région** : EU

- [ ] Créer la Scheduled Query
- [ ] Faire un screenshot de la configuration
- [ ] Exécuter manuellement pour vérifier

### 3.2 Notification en cas d'erreur

Configurez une notification email en cas d'échec :

1. Dans les paramètres de la Scheduled Query
2. Activer les **notifications par email** en cas d'erreur

- [ ] Activer les notifications d'erreur

---

## 4. Monitoring

### 4.1 Vue de monitoring du pipeline

Créez une vue qui résume l'état du pipeline :

```sql
CREATE OR REPLACE VIEW meta.vw_pipeline_status AS
SELECT
    step_name,
    MAX(finished_at) AS last_run,
    (SELECT status FROM meta.pipeline_logs l2
     WHERE l2.step_name = l.step_name
     ORDER BY finished_at DESC LIMIT 1) AS last_status,
    (SELECT rows_processed FROM meta.pipeline_logs l2
     WHERE l2.step_name = l.step_name
     ORDER BY finished_at DESC LIMIT 1) AS last_rows_processed,
    TIMESTAMP_DIFF(
        (SELECT MAX(finished_at) FROM meta.pipeline_logs l2 WHERE l2.step_name = l.step_name),
        (SELECT MAX(started_at) FROM meta.pipeline_logs l2 WHERE l2.step_name = l.step_name),
        SECOND
    ) AS last_duration_seconds,
    COUNT(*) AS total_runs,
    COUNTIF(status = 'SUCCESS') AS success_count,
    COUNTIF(status = 'ERROR') AS error_count
FROM meta.pipeline_logs l
GROUP BY step_name;
```

- [ ] Créer `meta.vw_pipeline_status`
- [ ] Vérifier : `SELECT * FROM meta.vw_pipeline_status`

### 4.2 Vue de comptage des tables

```sql
CREATE OR REPLACE VIEW meta.vw_table_counts AS
SELECT 'staging.stg_fact_reseller_sales' AS table_name, COUNT(*) AS row_count FROM staging.stg_fact_reseller_sales
UNION ALL SELECT 'dw.fact_reseller_sales', COUNT(*) FROM dw.fact_reseller_sales
UNION ALL SELECT 'dw.dim_date', COUNT(*) FROM dw.dim_date
UNION ALL SELECT 'dw.dim_product', COUNT(*) FROM dw.dim_product
UNION ALL SELECT 'dw.dim_reseller', COUNT(*) FROM dw.dim_reseller
UNION ALL SELECT 'dw.dim_employee', COUNT(*) FROM dw.dim_employee
UNION ALL SELECT 'dw.dim_geography', COUNT(*) FROM dw.dim_geography
UNION ALL SELECT 'marts.mart_sales_daily', COUNT(*) FROM marts.mart_sales_daily
UNION ALL SELECT 'marts.mart_products', COUNT(*) FROM marts.mart_products
UNION ALL SELECT 'marts.mart_customers', COUNT(*) FROM marts.mart_customers;
```

- [ ] Créer `meta.vw_table_counts`

---

## 5. Documentation

### 5.1 README du projet

Créez un fichier `README.md` documentant :

1. **Architecture** : schéma staging → dw → marts avec les tables
2. **Données sources** : description d'AdventureWorks DW, volumétrie
3. **Modèle de données** : schéma en étoile avec les dimensions et faits
4. **Data Marts** : description de chaque mart et ses KPI
5. **Pipeline** : comment exécuter le refresh (manuel et automatique)
6. **Optimisation** : choix de partitionnement/clustering justifiés
7. **Monitoring** : comment vérifier l'état du pipeline

- [ ] Créer le README.md

### 5.2 Documentation des KPI

Créez un tableau récapitulatif des KPI :

| KPI | Formule | Table source | Interprétation |
|-----|---------|--------------|----------------|
| CA total | `SUM(sales_amount)` | `mart_sales_daily` | Revenue brut |
| Marge | `SUM(margin)` | `mart_sales_daily` | Profit avant frais |
| Taux de marge | `SUM(margin) / SUM(revenue) * 100` | `mart_sales_daily` | Rentabilité |
| Panier moyen | `revenue / nb_orders` | `mart_sales_daily` | Valeur moyenne par commande |
| LTV | `SUM(sales_amount) par client` | `mart_customers` | Valeur vie client |
| ... | ... | ... | ... |

- [ ] Compléter le tableau avec tous les KPI implémentés

---

## Livrables — Partie 5

1. **Audit d'optimisation** : tableau montrant le partitionnement/clustering de chaque table
2. **3 Stored Procedures** fonctionnelles (sp_refresh_dw, sp_refresh_marts, sp_run_full_pipeline)
3. **Scheduled Query** configurée (screenshot)
4. **Vues de monitoring** (vw_pipeline_status, vw_table_counts)
5. **README.md** complet
6. **Tableau des KPI** documentés
