# Brief : Construction d'un Data Warehouse et de Data Marts avec BigQuery

## Partie 0 — Veille : Concepts DW, OLAP et BigQuery

---

# Partie 2 — Import des données & couche Staging

## Objectifs

À l'issue de cette partie, vous serez capable de :

- créer un projet GCP et configurer BigQuery ;
- organiser les données par **datasets** (staging, dw, marts, meta) ;
- charger des fichiers CSV dans BigQuery via Cloud Storage ;
- ajouter des **métadonnées d'ingestion** aux tables ;
- effectuer des **contrôles qualité** sur les données brutes.

---

## 1. Configuration de l'environnement GCP

### 1.1 Créer le projet

- [ ] Créer un projet GCP : `adventureworks-dw-[votre-nom]`
- [ ] Activer l'API BigQuery
- [ ] Vérifier que le Free Tier est actif (1 TB requêtes / 10 GB stockage gratuits)

### 1.2 Créer les datasets

Créez les 4 datasets suivants dans la **région EU** :

| Dataset | Rôle | Labels |
|---------|------|--------|
| `staging` | Données brutes importées | `layer=staging`, `project=adventureworks` |
| `dw` | Core Data Warehouse (dimensions + faits nettoyés) | `layer=dw`, `project=adventureworks` |
| `marts` | Data Marts métier (agrégations) | `layer=marts`, `project=adventureworks` |
| `meta` | Logs et monitoring du pipeline | `layer=meta`, `project=adventureworks` |

```sql
-- Exemple de création via SQL
CREATE SCHEMA IF NOT EXISTS staging
OPTIONS (
  location = 'EU',
  labels = [('layer', 'staging'), ('project', 'adventureworks')]
);

-- Créez les 3 autres datasets de la même manière
```

- [ ] Créer le dataset `staging`
- [ ] Créer le dataset `dw`
- [ ] Créer le dataset `marts`
- [ ] Créer le dataset `meta`

### 1.3 Créer le bucket Cloud Storage

- [ ] Créer un bucket : `adventureworks-data-[votre-nom]` (région EU)
- [ ] Créer les dossiers : `landing/`, `archive/`
- [ ] Télécharger les 6 fichiers CSV (FactResellerSales, DimProduct, DimReseller, DimEmployee, DimGeography, DimDate)
- [ ] Uploader les fichiers dans `landing/`

**Livrable :** Screenshot montrant les 4 datasets dans BigQuery et le bucket avec les fichiers.

---

## 2. Création des tables Staging

### 2.1 Stratégie de staging

Les tables staging doivent :
- refléter la **structure exacte** des fichiers sources ;
- avoir les **types corrects** (pas tout en STRING — contrairement à une approche Bronze, ici les CSV AdventureWorks sont déjà typés) ;
- inclure des **colonnes de métadonnées** pour la traçabilité.

Colonnes de métadonnées à ajouter :

```sql
_ingested_at  TIMESTAMP    -- horodatage du chargement
_source_file  STRING       -- nom du fichier source
```

### 2.2 Créer la table staging.stg_fact_reseller_sales

Analysez le fichier `FactResellerSales.csv` et créez la table staging correspondante.

```sql
-- Structure à compléter
CREATE OR REPLACE TABLE staging.stg_fact_reseller_sales (
    -- Clés
    ProductKey              INT64,
    OrderDateKey            INT64,
    DueDateKey              INT64,
    ShipDateKey             INT64,
    ResellerKey             INT64,
    EmployeeKey             INT64,
    PromotionKey            INT64,
    CurrencyKey             INT64,
    SalesTerritoryKey       INT64,

    -- Identifiants commande
    SalesOrderNumber        STRING,
    SalesOrderLineNumber    INT64,
    RevisionNumber          INT64,

    -- Mesures
    OrderQuantity           INT64,
    UnitPrice               FLOAT64,
    ExtendedAmount          FLOAT64,
    UnitPriceDiscountPct    FLOAT64,
    DiscountAmount          FLOAT64,
    ProductStandardCost     FLOAT64,
    TotalProductCost        FLOAT64,
    SalesAmount             FLOAT64,
    TaxAmt                  FLOAT64,
    Freight                 FLOAT64,

    -- Dates
    OrderDate               DATE,
    DueDate                 DATE,
    ShipDate                DATE,

    -- Métadonnées
    _ingested_at            TIMESTAMP,
    _source_file            STRING
);
```

- [ ] Créer `staging.stg_fact_reseller_sales`

### 2.3 Créer les tables staging des dimensions

Créez les tables staging suivantes. Pour chaque table, analysez le CSV correspondant pour identifier les colonnes et leurs types.

- [ ] `staging.stg_dim_product` — colonnes principales : ProductKey, ProductAlternateKey, EnglishProductName, StandardCost, ListPrice, Color, Size, ProductSubcategoryKey, ...
- [ ] `staging.stg_dim_reseller` — colonnes principales : ResellerKey, ResellerAlternateKey, BusinessType, ResellerName, NumberEmployees, ...
- [ ] `staging.stg_dim_employee` — colonnes principales : EmployeeKey, FirstName, LastName, Title, HireDate, SalesTerritoryKey, ...
- [ ] `staging.stg_dim_geography` — colonnes principales : GeographyKey, City, StateProvinceName, CountryRegionCode, EnglishCountryRegionName, SalesTerritoryKey, ...
- [ ] `staging.stg_dim_date` — colonnes principales : DateKey, FullDateAlternateKey, DayNumberOfWeek, EnglishDayNameOfWeek, MonthNumberOfYear, EnglishMonthName, CalendarQuarter, CalendarYear, ...

**Conseil :** Ouvrez chaque CSV pour vérifier les en-têtes et les types de données avant de créer la table.

---

## 3. Chargement des données

### 3.1 Charger les CSV depuis Cloud Storage

Pour chaque table, chargez les données depuis le bucket.

```sql
-- Exemple pour FactResellerSales
LOAD DATA OVERWRITE staging.stg_fact_reseller_sales
FROM FILES (
  format = 'CSV',
  uris = ['gs://adventureworks-data-[votre-nom]/landing/FactResellerSales.csv'],
  skip_leading_rows = 1
);
```

**Alternative via bq CLI :**

```bash
bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  staging.stg_fact_reseller_sales \
  gs://adventureworks-data-[votre-nom]/landing/FactResellerSales.csv
```

- [ ] Charger `FactResellerSales.csv` → `staging.stg_fact_reseller_sales`
- [ ] Charger `DimProduct.csv` → `staging.stg_dim_product`
- [ ] Charger `DimReseller.csv` → `staging.stg_dim_reseller`
- [ ] Charger `DimEmployee.csv` → `staging.stg_dim_employee`
- [ ] Charger `DimGeography.csv` → `staging.stg_dim_geography`
- [ ] Charger `DimDate.csv` → `staging.stg_dim_date`

### 3.2 Mettre à jour les métadonnées

Après chargement, mettez à jour les colonnes de métadonnées :

```sql
-- Exemple
UPDATE staging.stg_fact_reseller_sales
SET
  _ingested_at = CURRENT_TIMESTAMP(),
  _source_file = 'FactResellerSales.csv'
WHERE _ingested_at IS NULL;
```

- [ ] Mettre à jour les métadonnées de toutes les tables staging

---

## 4. Contrôles qualité

### 4.1 Comptage des lignes

Vérifiez que le nombre de lignes correspond aux fichiers sources :

```sql
-- Comptage par table
SELECT 'stg_fact_reseller_sales' as table_name, COUNT(*) as row_count
FROM staging.stg_fact_reseller_sales
UNION ALL
SELECT 'stg_dim_product', COUNT(*) FROM staging.stg_dim_product
UNION ALL
SELECT 'stg_dim_reseller', COUNT(*) FROM staging.stg_dim_reseller
UNION ALL
SELECT 'stg_dim_employee', COUNT(*) FROM staging.stg_dim_employee
UNION ALL
SELECT 'stg_dim_geography', COUNT(*) FROM staging.stg_dim_geography
UNION ALL
SELECT 'stg_dim_date', COUNT(*) FROM staging.stg_dim_date;
```

- [ ] Vérifier les comptages

### 4.2 Vérification des NULLs sur les clés

Les clés primaires et étrangères ne doivent pas être NULL :

```sql
-- Vérifier les clés de la table de faits
SELECT
  COUNTIF(ProductKey IS NULL) as null_product,
  COUNTIF(OrderDateKey IS NULL) as null_order_date,
  COUNTIF(ResellerKey IS NULL) as null_reseller,
  COUNTIF(EmployeeKey IS NULL) as null_employee,
  COUNTIF(SalesTerritoryKey IS NULL) as null_territory,
  COUNTIF(SalesAmount IS NULL) as null_sales_amount
FROM staging.stg_fact_reseller_sales;
```

- [ ] Vérifier les NULLs sur les clés de la table de faits
- [ ] Vérifier les NULLs sur les clés primaires des dimensions

### 4.3 Vérification des doublons

```sql
-- Doublons dans la table de faits (sur SalesOrderNumber + SalesOrderLineNumber)
SELECT
  SalesOrderNumber,
  SalesOrderLineNumber,
  COUNT(*) as nb
FROM staging.stg_fact_reseller_sales
GROUP BY 1, 2
HAVING COUNT(*) > 1;
-- Résultat attendu : 0 lignes

-- Doublons dans les dimensions (sur la clé primaire)
SELECT ProductKey, COUNT(*) as nb
FROM staging.stg_dim_product
GROUP BY 1
HAVING COUNT(*) > 1;
-- Résultat attendu : 0 lignes
```

- [ ] Vérifier l'absence de doublons dans la table de faits
- [ ] Vérifier l'absence de doublons dans chaque dimension

### 4.4 Vérification de l'intégrité référentielle

Les clés étrangères de la table de faits doivent exister dans les dimensions :

```sql
-- Produits référencés dans les faits mais absents de la dimension
SELECT DISTINCT f.ProductKey
FROM staging.stg_fact_reseller_sales f
LEFT JOIN staging.stg_dim_product p ON f.ProductKey = p.ProductKey
WHERE p.ProductKey IS NULL;
-- Résultat attendu : 0 lignes
```

- [ ] Vérifier l'intégrité référentielle pour chaque clé étrangère (ProductKey, ResellerKey, EmployeeKey, SalesTerritoryKey → GeographyKey)

### 4.5 Statistiques descriptives

```sql
-- Plages de valeurs des mesures
SELECT
  MIN(SalesAmount) as min_sales,
  MAX(SalesAmount) as max_sales,
  AVG(SalesAmount) as avg_sales,
  MIN(OrderDate) as min_date,
  MAX(OrderDate) as max_date,
  COUNT(DISTINCT SalesOrderNumber) as nb_orders
FROM staging.stg_fact_reseller_sales;
```

- [ ] Produire les statistiques descriptives de la table de faits

---

## 5. Table de logs

Créez une table pour tracer les chargements :

```sql
CREATE TABLE meta.pipeline_logs (
  log_id          STRING DEFAULT GENERATE_UUID(),
  step_name       STRING NOT NULL,
  source_table    STRING,
  target_table    STRING,
  started_at      TIMESTAMP,
  finished_at     TIMESTAMP,
  rows_processed  INT64,
  status          STRING,     -- SUCCESS, ERROR
  error_message   STRING
);

-- Insérer un log pour chaque chargement effectué
INSERT INTO meta.pipeline_logs (step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
VALUES (
  'staging_load',
  'FactResellerSales.csv',
  'staging.stg_fact_reseller_sales',
  TIMESTAMP('2025-02-10 09:00:00'),
  CURRENT_TIMESTAMP(),
  (SELECT COUNT(*) FROM staging.stg_fact_reseller_sales),
  'SUCCESS'
);
```

- [ ] Créer la table `meta.pipeline_logs`
- [ ] Insérer un log pour chaque table chargée

---

## Livrables — Partie 2

1. **Scripts SQL** de création des 6 tables staging
2. **Scripts SQL** de chargement (LOAD DATA ou bq CLI)
3. **Résultats des contrôles qualité** :
   - comptages par table
   - vérification des NULLs
   - vérification des doublons
   - intégrité référentielle
   - statistiques descriptives
4. **Table `meta.pipeline_logs`** remplie
5. **Screenshot** de la console BigQuery montrant les tables staging chargées
