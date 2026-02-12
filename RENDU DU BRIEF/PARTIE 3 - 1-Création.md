# PARTIE 3 - 1-Création

## 🧭 Étape 1 — Problème stratégique avant de commencer

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_dim_date` AS
WITH date_range AS (
  SELECT
    date_day
  FROM UNNEST(GENERATE_DATE_ARRAY('2010-01-01', '2014-12-31')) AS date_day
)

SELECT
  FORMAT_DATE('%Y%m%d', date_day) AS DateKey,
  date_day AS FullDateAlternateKey,
  EXTRACT(DAYOFWEEK FROM date_day) AS DayNumberOfWeek,
  FORMAT_DATE('%A', date_day) AS EnglishDayNameOfWeek,
  EXTRACT(DAY FROM date_day) AS DayNumberOfMonth,
  EXTRACT(MONTH FROM date_day) AS MonthNumberOfYear,
  FORMAT_DATE('%B', date_day) AS EnglishMonthName,
  EXTRACT(QUARTER FROM date_day) AS CalendarQuarter,
  EXTRACT(YEAR FROM date_day) AS CalendarYear,
  EXTRACT(QUARTER FROM date_day) AS FiscalQuarter,
  EXTRACT(YEAR FROM date_day) AS FiscalYear,

  CURRENT_TIMESTAMP() AS _ingested_at,
  'generated_sql' AS _source_file

FROM date_range;
```

**vérification**
```sql
SELECT COUNT(*) FROM `adventureworks-dw-christian.staging.stg_dim_date`;
```

**résultats**

| line | COUNT(0) |
|------|----------|
|    1 |     1826 |

## 🧭 Étape 2 — Créer dw.dim_date (core DW)

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_date` AS
SELECT
  CAST(DateKey AS INT64)          AS date_key,
  FullDateAlternateKey            AS date_complete,
  DayNumberOfWeek                 AS num_jour_semaine,
  EnglishDayNameOfWeek            AS jour_semaine,
  DayNumberOfMonth                AS jour_du_mois,
  MonthNumberOfYear               AS num_mois,
  EnglishMonthName                AS nom_mois,
  CalendarQuarter                 AS trimestre,
  CalendarYear                    AS annee,
  FiscalQuarter                   AS trimestre_fiscal,
  FiscalYear                      AS annee_fiscale
FROM `adventureworks-dw-christian.staging.stg_dim_date`;
```

**vérification**
```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.dw.dim_date`;
```

**résultats**

1826 lignes > OK

## 🧭 Étape 3 — Créer dw.dim_product (transformations demandées)

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_product` AS
SELECT
  ProductKey AS product_key,
  ProductAlternateKey AS product_code,
  EnglishProductName AS product_name,
  IFNULL(Color, 'N/A') AS color,
  IFNULL(Size, 'N/A') AS size,
  StandardCost AS standard_cost,
  ListPrice AS list_price,
  ProductSubcategoryKey AS subcategory_key,
  (ListPrice - StandardCost) AS margin
FROM `adventureworks-dw-christian.staging.stg_dim_product`
WHERE ListPrice > 0;
```

**vérification 1**

Comptage

```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.dw.dim_product`;
```

**résultats**

395 lignes

**vérification 2**

Vérif N/A

```sql
SELECT
  COUNTIF(color = 'N/A') AS nb_color_na,
  COUNTIF(size = 'N/A') AS nb_size_na
FROM `adventureworks-dw-christian.dw.dim_product`;
```

**résultats**

| nb_color_na | nb_size_na |
|-------------|------------|
|           0 |         98 |

## 🧭 Étape 4 — Créer dw.dim_reseller (transformations demandées)

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_reseller` AS
SELECT
  ResellerKey AS reseller_key,
  ResellerAlternateKey AS reseller_code,
  ResellerName AS reseller_name,
  UPPER(BusinessType) AS business_type,
  IFNULL(NumberEmployees, 0) AS nb_employees,
  AnnualSales AS annual_sales,
  AnnualRevenue AS annual_revenue,
  YearOpened AS year_opened
FROM `adventureworks-dw-christian.staging.stg_dim_reseller`;
```

**vérification 1**

comptage

```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.dw.dim_reseller`;
```

**résultats**

701 > OK

**vérification 2**

Check standardisation

```sql
SELECT
  COUNTIF(business_type != UPPER(business_type)) AS not_upper_business_type,
  COUNTIF(nb_employees IS NULL) AS null_nb_employees
FROM `adventureworks-dw-christian.dw.dim_reseller`;
```

**résultats**

| not_upper_business_type | null_nb_employees |
|-------------------------|-------------------|
|                       0 |                 0 |

## 🧭 Étape 5 — Créer dw.dim_employee

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.dw.dim_employee` AS
SELECT
  EmployeeKey AS employee_key,
  CONCAT(FirstName, ' ', LastName) AS full_name,
  INITCAP(Title) AS job_title,
  HireDate AS hire_date,
  SalesTerritoryKey AS sales_territory_key,
  DepartmentName AS department
FROM `adventureworks-dw-christian.staging.stg_dim_employee`;
```

**vérification 1**

Comptage

```sql
SELECT COUNT(*) AS row_count
FROM `adventureworks-dw-christian.dw.dim_employee`;
```

**résultats**

296 > OK

**vérification 2**

Check standardisation

```sql
SELECT
  COUNTIF(full_name IS NULL OR full_name = ' ') AS invalid_full_name,
  COUNTIF(job_title IS NULL OR job_title = '') AS null_job_title
FROM `adventureworks-dw-christian.dw.dim_employee`;
```

**résultats**

| invalid_full_name | null_job_title |
|-------------------|----------------|
|                 0 |              0 |















---
---
---
---
---

> [SUITE DU RENDU ICI](https://github.com/ChristianPRO1982/DI10-Inter-IU_ARA-HDF_Data-Eng_148635_ALT/blob/main/RENDU%20DU%20BRIEF/PARTIE%203%20-%202-R%C3%A9ponses%20aux%20questions.md)