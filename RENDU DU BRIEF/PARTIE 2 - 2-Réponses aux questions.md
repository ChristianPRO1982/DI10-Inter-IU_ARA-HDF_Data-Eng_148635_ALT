# PARTIE 2 - 2-Réponses aux questions

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
LOAD DATA OVERWRITE `adventureworks-dw-christian.staging.stg_dim_product`
FROM FILES (
  format = 'CSV',
  uris = ['gs://adventureworks-data-christian/landing/DimProduct2.csv'],
  skip_leading_rows = 1
);
```

**vérification**
```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.staging.stg_dim_product`;
```

## 🧭 Étape 9 — Ajouter les métadonnées à stg_dim_product

```sql
ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_product`
ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP;

ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_product`
ADD COLUMN IF NOT EXISTS _source_file STRING;

UPDATE `adventureworks-dw-christian.staging.stg_dim_product`
SET
  _ingested_at = CURRENT_TIMESTAMP(),
  _source_file = 'DimProduct2.csv'
WHERE _ingested_at IS NULL;
```

**vérification**
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(_ingested_at IS NULL) AS null_ingested_at,
  COUNTIF(_source_file IS NULL) AS null_source_file,
  ANY_VALUE(_source_file) AS sample_source_file
FROM `adventureworks-dw-christian.staging.stg_dim_product`;
```

## 🧭 Étape 10 — Dimension Revendeur : créer staging.stg_dim_reseller

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_dim_reseller` (
  ResellerKey              INT64,
  ResellerAlternateKey     STRING,
  Phone                    STRING,
  BusinessType             STRING,
  ResellerName             STRING,
  NumberEmployees          INT64,
  OrderFrequency           STRING,
  OrderMonth               INT64,
  FirstOrderYear           INT64,
  LastOrderYear            INT64,
  ProductLine              STRING,
  AddressLine1             STRING,
  AddressLine2             STRING,
  AnnualSales              FLOAT64,
  BankName                 STRING,
  MinPaymentType           INT64,
  MinPaymentAmount         FLOAT64,
  AnnualRevenue            FLOAT64,
  YearOpened               INT64,

  -- Metadata
  _ingested_at             TIMESTAMP,
  _source_file             STRING
);
```

## 🧭 Étape 11 — Charger DimReseller2.csv dans staging.stg_dim_reseller

```sql
LOAD DATA OVERWRITE `adventureworks-dw-christian.staging.stg_dim_reseller`
FROM FILES (
  format = 'CSV',
  uris = ['gs://adventureworks-data-christian/landing/DimReseller2.csv'],
  skip_leading_rows = 1
);
```

**vérification**
```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.staging.stg_dim_reseller`;
```

## 🧭 Étape 12 — Métadonnées pour stg_dim_reseller (pattern safe)

```sql
ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_reseller`
ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP;

ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_reseller`
ADD COLUMN IF NOT EXISTS _source_file STRING;

UPDATE `adventureworks-dw-christian.staging.stg_dim_reseller`
SET
  _ingested_at = CURRENT_TIMESTAMP(),
  _source_file = 'DimReseller2.csv'
WHERE _ingested_at IS NULL;
```

**vérification**
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(_ingested_at IS NULL) AS null_ingested_at,
  COUNTIF(_source_file IS NULL) AS null_source_file,
  ANY_VALUE(_source_file) AS sample_source_file
FROM `adventureworks-dw-christian.staging.stg_dim_reseller`;
```

## 🧭 Étape 13 — Dimension Employé : créer

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_dim_employee` (
  EmployeeKey                INT64,
  ParentEmployeeKey          INT64,
  EmployeeNationalIDAlternateKey STRING,
  ParentEmployeeNationalIDAlternateKey STRING,
  SalesTerritoryKey          INT64,
  FirstName                  STRING,
  LastName                   STRING,
  MiddleName                 STRING,
  NameStyle                  BOOL,
  Title                      STRING,
  HireDate                   DATE,
  BirthDate                  DATE,
  LoginID                    STRING,
  EmailAddress               STRING,
  Phone                      STRING,
  MaritalStatus              STRING,
  EmergencyContactName       STRING,
  EmergencyContactPhone      STRING,
  SalariedFlag               BOOL,
  Gender                     STRING,
  PayFrequency               INT64,
  BaseRate                   FLOAT64,
  VacationHours              INT64,
  SickLeaveHours             INT64,
  CurrentFlag                BOOL,
  SalesPersonFlag            BOOL,
  DepartmentName             STRING,
  StartDate                  DATE,
  EndDate                    DATE,
  Status                     STRING,

  -- Metadata
  _ingested_at               TIMESTAMP,
  _source_file               STRING
);
```

## 🧭 Étape 14 — Charger DimEmployee2.csv dans staging.stg_dim_employee

```sql
LOAD DATA OVERWRITE `adventureworks-dw-christian.staging.stg_dim_employee`
FROM FILES (
  format = 'CSV',
  uris = ['gs://adventureworks-data-christian/landing/DimEmployee2.csv'],
  skip_leading_rows = 1
);
```

**vérification**
```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.staging.stg_dim_employee`;
```

## 🧭 Étape 15 — Métadonnées pour stg_dim_employee

```sql
ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_employee`
ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP;

ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_employee`
ADD COLUMN IF NOT EXISTS _source_file STRING;

UPDATE `adventureworks-dw-christian.staging.stg_dim_employee`
SET
  _ingested_at = CURRENT_TIMESTAMP(),
  _source_file = 'DimEmployee2.csv'
WHERE _ingested_at IS NULL;
```

**vérification**
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(_ingested_at IS NULL) AS null_ingested_at,
  COUNTIF(_source_file IS NULL) AS null_source_file,
  ANY_VALUE(_source_file) AS sample_source_file
FROM `adventureworks-dw-christian.staging.stg_dim_employee`;
```

## 🧭 Étape 16 — Dimension Géographie : créer staging.stg_dim_geography

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_dim_geography` (
  GeographyKey             INT64,
  City                     STRING,
  StateProvinceCode        STRING,
  StateProvinceName        STRING,
  CountryRegionCode        STRING,
  EnglishCountryRegionName STRING,
  PostalCode               STRING,
  SalesTerritoryKey        INT64,
  IpAddressLocator         STRING,

  -- Metadata
  _ingested_at             TIMESTAMP,
  _source_file             STRING
);
```

## 🧭 Étape 17 — Charger DimGeography2.csv dans staging.stg_dim_geography

```sql
LOAD DATA OVERWRITE `adventureworks-dw-christian.staging.stg_dim_geography`
FROM FILES (
  format = 'CSV',
  uris = ['gs://adventureworks-data-christian/landing/DimGeography2.csv'],
  skip_leading_rows = 1
);
```

**vérification**
```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.staging.stg_dim_geography`;
```

## 🧭 Étape 18 — Métadonnées pour stg_dim_geography

```sql
ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_geography`
ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP;

ALTER TABLE `adventureworks-dw-christian.staging.stg_dim_geography`
ADD COLUMN IF NOT EXISTS _source_file STRING;

UPDATE `adventureworks-dw-christian.staging.stg_dim_geography`
SET
  _ingested_at = CURRENT_TIMESTAMP(),
  _source_file = 'DimGeography2.csv'
WHERE _ingested_at IS NULL;
```

**vérification**
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNTIF(_ingested_at IS NULL) AS null_ingested_at,
  COUNTIF(_source_file IS NULL) AS null_source_file,
  ANY_VALUE(_source_file) AS sample_source_file
FROM `adventureworks-dw-christian.staging.stg_dim_geography`;
```

## 🧭 Étape 19 — Contrôle qualité global (comptages)

```sql
SELECT 'stg_fact_reseller_sales' AS table_name, COUNT(*) AS row_count
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`
UNION ALL
SELECT 'stg_dim_product', COUNT(*)
FROM `adventureworks-dw-christian.staging.stg_dim_product`
UNION ALL
SELECT 'stg_dim_reseller', COUNT(*)
FROM `adventureworks-dw-christian.staging.stg_dim_reseller`
UNION ALL
SELECT 'stg_dim_employee', COUNT(*)
FROM `adventureworks-dw-christian.staging.stg_dim_employee`
UNION ALL
SELECT 'stg_dim_geography', COUNT(*)
FROM `adventureworks-dw-christian.staging.stg_dim_geography`;
```

**résultats :**

1	stg_fact_reseller_sales	60855
2	stg_dim_product	606
3	stg_dim_employee	296
4	stg_dim_reseller	701
5	stg_dim_geography	655

## 🧭 Étape 20 — Contrôle qualité : NULL checks sur les clés de la FACT

```sql
SELECT
  COUNTIF(ProductKey IS NULL) AS null_product,
  COUNTIF(OrderDateKey IS NULL) AS null_order_date,
  COUNTIF(DueDateKey IS NULL) AS null_due_date,
  COUNTIF(ShipDateKey IS NULL) AS null_ship_date,
  COUNTIF(ResellerKey IS NULL) AS null_reseller,
  COUNTIF(EmployeeKey IS NULL) AS null_employee,
  COUNTIF(SalesTerritoryKey IS NULL) AS null_territory,
  COUNTIF(SalesAmount IS NULL) AS null_sales_amount
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`;
```

**résultats :**

1	0	0	0	0	0	0	0	0