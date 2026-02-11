# PARTIE 1

## 🧭 Étape 1 — Création propre de l’environnement GCP

projet GCP : `adventureworks-dw-christian`

## 🧭 Étape 2 — Création des datasets (architecture propre)

```sql
CREATE SCHEMA IF NOT EXISTS `adventureworks-dw-christian.staging`
OPTIONS (
  location = 'EU',
  labels = [('layer', 'staging'), ('project', 'adventureworks')]
);

CREATE SCHEMA IF NOT EXISTS `adventureworks-dw-christian.dw`
OPTIONS (
  location = 'EU',
  labels = [('layer', 'dw'), ('project', 'adventureworks')]
);

CREATE SCHEMA IF NOT EXISTS `adventureworks-dw-christian.marts`
OPTIONS (
  location = 'EU',
  labels = [('layer', 'marts'), ('project', 'adventureworks')]
);

CREATE SCHEMA IF NOT EXISTS `adventureworks-dw-christian.meta`
OPTIONS (
  location = 'EU',
  labels = [('layer', 'meta'), ('project', 'adventureworks')]
);
```

## 🧭 Étape 3 — Créer le bucket Cloud Storage + dossiers + upload CSV

Dans le bucket :

créer un “folder” `landing/`

créer un “folder” `archive/`

upload dans landing/ :
* FactResellerSales.csv
* DimProduct.csv
* DimReseller.csv
* DimEmployee.csv
* DimGeography.csv

## 🧭 Étape 4 — Créer les tables staging.* (on commence par la FACT)

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_fact_reseller_sales` (
  -- Keys
  ProductKey              INT64,
  OrderDateKey            INT64,
  DueDateKey              INT64,
  ShipDateKey             INT64,
  ResellerKey             INT64,
  EmployeeKey             INT64,
  PromotionKey            INT64,
  CurrencyKey             INT64,
  SalesTerritoryKey       INT64,

  -- Sales order identifiers
  SalesOrderNumber        STRING,
  SalesOrderLineNumber    INT64,
  RevisionNumber          INT64,

  -- Measures
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

  -- Metadata
  _ingested_at            TIMESTAMP,
  _source_file            STRING
);
```

## 🧭 Étape 5 — Charger le CSV dans la table staging (LOAD DATA)

```sql
LOAD DATA OVERWRITE `adventureworks-dw-christian.staging.stg_fact_reseller_sales`
FROM FILES (
  format = 'CSV',
  uris = ['gs://adventureworks-data-christian/landing/FactResellerSales2.csv'],
  skip_leading_rows = 1
);
```

**validation**
```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`;
```

## 🧭 Étape 6 — Remplir les colonnes de métadonnées (FACT uniquement)

```sql
ALTER TABLE `adventureworks-dw-christian.staging.stg_fact_reseller_sales`
ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP;

ALTER TABLE `adventureworks-dw-christian.staging.stg_fact_reseller_sales`
ADD COLUMN IF NOT EXISTS _source_file STRING;

UPDATE `adventureworks-dw-christian.staging.stg_fact_reseller_sales`
SET
  _ingested_at = CURRENT_TIMESTAMP(),
  _source_file = 'FactResellerSales2.csv'
WHERE _ingested_at IS NULL;
```
**vérification**
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(_ingested_at IS NULL) AS null_ingested_at,
  COUNTIF(_source_file IS NULL) AS null_source_file,
  ANY_VALUE(_source_file) AS sample_source_file
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`;
```

## 🧭 Étape 7 — Staging de la dimension Produit (DimProduct2.csv)

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_dim_product` (
  ProductKey               INT64,
  ProductAlternateKey      STRING,
  ProductSubcategoryKey    INT64,
  WeightUnitMeasureCode    STRING,
  SizeUnitMeasureCode      STRING,
  EnglishProductName       STRING,
  SpanishProductName       STRING,
  FrenchProductName        STRING,
  StandardCost             FLOAT64,
  FinishedGoodsFlag        INT64,
  Color                    STRING,
  SafetyStockLevel         INT64,
  ReorderPoint             INT64,
  ListPrice                FLOAT64,
  Size                     STRING,
  SizeRange                STRING,
  Weight                   FLOAT64,
  DaysToManufacture        INT64,
  ProductLine              STRING,
  DealerPrice              FLOAT64,
  Class                    STRING,
  Style                    STRING,
  ModelName                STRING,
  EnglishDescription       STRING,
  FrenchDescription        STRING,
  ChineseDescription       STRING,
  ArabicDescription        STRING,
  HebrewDescription        STRING,
  ThaiDescription          STRING,
  GermanDescription        STRING,
  JapaneseDescription      STRING,
  TurkishDescription       STRING,
  StartDate                DATE,
  EndDate                  DATE,
  Status                   STRING,

  -- Metadata
  _ingested_at             TIMESTAMP,
  _source_file             STRING
);
```

## 🧭 Étape 8 — Charger DimProduct2.csv dans staging.stg_dim_product

```sql

```
