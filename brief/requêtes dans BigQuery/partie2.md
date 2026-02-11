# PARTIE 1

projet GCP : `adventureworks-dw-christian`

## Création des datasets

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

## création des dossiers Cloud Storage

Dans le bucket :

créer un “folder” `landing/`

créer un “folder” `archive/`

upload dans landing/ :
* FactResellerSales.csv
* DimProduct.csv
* DimReseller.csv
* DimEmployee.csv
* DimGeography.csv

## création table staging

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

## Charger le CSV dans la table staging (LOAD DATA)

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