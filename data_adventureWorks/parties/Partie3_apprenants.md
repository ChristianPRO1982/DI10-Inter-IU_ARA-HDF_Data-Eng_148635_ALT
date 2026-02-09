# Brief : Construction d'un Data Warehouse et de Data Marts avec BigQuery

## Partie 0 — Veille : Concepts DW, OLAP et BigQuery

---

# Partie 3 — Transformations & Core Data Warehouse

## Objectifs

À l'issue de cette partie, vous serez capable de :

- créer des **tables de dimensions nettoyées** à partir du staging ;
- créer une **table de faits** avec clés étrangères validées ;
- appliquer des règles de **standardisation** et **dédoublonnage** ;
- optimiser les tables avec **partitionnement** et **clustering** ;
- documenter les transformations appliquées.

---

## 1. Architecture cible du Core DW

```
staging                          dw
┌──────────────────┐            ┌──────────────────┐
│ stg_dim_date     │──────────►│ dim_date          │
│ stg_dim_product  │──────────►│ dim_product       │
│ stg_dim_reseller │──────────►│ dim_reseller      │
│ stg_dim_employee │──────────►│ dim_employee      │
│ stg_dim_geography│──────────►│ dim_geography     │
│                  │            │                   │
│ stg_fact_reseller│──────────►│ fact_reseller_    │
│    _sales        │            │    sales          │
└──────────────────┘            └──────────────────┘
```

Les transformations Staging → DW doivent :
- **sélectionner** les colonnes utiles (pas tout reprendre) ;
- **renommer** les colonnes pour plus de clarté ;
- **standardiser** les formats (dates, textes, codes) ;
- **filtrer** les données invalides ;
- **dédoublonner** si nécessaire.

---

## 2. Dimensions

### 2.1 dim_date

La dimension Date est la plus simple. Sélectionnez les colonnes utiles et renommez-les :

```sql
CREATE OR REPLACE TABLE dw.dim_date AS
SELECT
    DateKey                     AS date_key,
    FullDateAlternateKey        AS date_complete,
    DayNumberOfWeek             AS num_jour_semaine,
    EnglishDayNameOfWeek        AS jour_semaine,
    DayNumberOfMonth            AS jour_du_mois,
    MonthNumberOfYear           AS num_mois,
    EnglishMonthName            AS nom_mois,
    CalendarQuarter             AS trimestre,
    CalendarYear                AS annee,
    FiscalQuarter               AS trimestre_fiscal,
    FiscalYear                  AS annee_fiscale
FROM staging.stg_dim_date;
```

- [ ] Créer `dw.dim_date`
- [ ] Vérifier : `SELECT COUNT(*) FROM dw.dim_date`

### 2.2 dim_product

Créez `dw.dim_product` en sélectionnant les colonnes pertinentes pour l'analyse.

**Colonnes à inclure :**
- `ProductKey` → `product_key`
- `ProductAlternateKey` → `product_code`
- `EnglishProductName` → `product_name`
- `Color` → `color`
- `Size` → `size`
- `StandardCost` → `standard_cost`
- `ListPrice` → `list_price`
- `ProductSubcategoryKey` → `subcategory_key`

**Transformations à appliquer :**
- Remplacer les NULLs dans `Color` par `'N/A'`
- Remplacer les NULLs dans `Size` par `'N/A'`
- Calculer une colonne `margin` = `list_price - standard_cost`
- Ne garder que les produits ayant un `ListPrice > 0` (exclure les produits non vendables)

```sql
-- À compléter
CREATE OR REPLACE TABLE dw.dim_product AS
SELECT
    ProductKey              AS product_key,
    ProductAlternateKey     AS product_code,
    EnglishProductName      AS product_name,
    -- Compléter les transformations...
FROM staging.stg_dim_product
WHERE ______;
```

- [ ] Créer `dw.dim_product`
- [ ] Vérifier les NULLs : `SELECT COUNTIF(color = 'N/A') FROM dw.dim_product`

### 2.3 dim_reseller

Créez `dw.dim_reseller` avec les colonnes utiles.

**Colonnes suggérées :**
- `ResellerKey` → `reseller_key`
- `ResellerAlternateKey` → `reseller_code`
- `ResellerName` → `reseller_name`
- `BusinessType` → `business_type`
- `GeographyKey` → `geography_key`
- `NumberEmployees` → `nb_employees`
- `AnnualSales` → `annual_sales`
- `AnnualRevenue` → `annual_revenue`
- `YearOpened` → `year_opened`

**Transformations :**
- Standardiser `BusinessType` en UPPER
- Remplacer les NULLs de `NumberEmployees` par 0

- [ ] Créer `dw.dim_reseller`

### 2.4 dim_employee

Créez `dw.dim_employee` avec les informations commerciales pertinentes.

**Colonnes suggérées :**
- `EmployeeKey` → `employee_key`
- `FirstName`, `LastName` → concaténer en `full_name`
- `Title` → `job_title`
- `HireDate` → `hire_date`
- `SalesTerritoryKey` → `sales_territory_key`
- `DepartmentName` → `department`

**Transformations :**
- Concaténer `FirstName || ' ' || LastName` en `full_name`
- Standardiser `Title` en INITCAP

- [ ] Créer `dw.dim_employee`

### 2.5 dim_geography

Créez `dw.dim_geography` avec la hiérarchie géographique.

**Colonnes suggérées :**
- `GeographyKey` → `geography_key`
- `City` → `city`
- `StateProvinceName` → `state_province`
- `CountryRegionCode` → `country_code`
- `EnglishCountryRegionName` → `country_name`
- `SalesTerritoryKey` → `sales_territory_key`

- [ ] Créer `dw.dim_geography`

---

## 3. Table de faits

### 3.1 Créer fact_reseller_sales

Créez `dw.fact_reseller_sales` avec :
- les clés étrangères vers les dimensions ;
- les mesures validées ;
- un **partitionnement** par `order_date` ;
- un **clustering** par `product_key, reseller_key`.

```sql
CREATE OR REPLACE TABLE dw.fact_reseller_sales
PARTITION BY order_date
CLUSTER BY product_key, reseller_key
AS
SELECT
    -- Clés
    f.ProductKey            AS product_key,
    f.OrderDateKey          AS order_date_key,
    f.ResellerKey           AS reseller_key,
    f.EmployeeKey           AS employee_key,
    f.SalesTerritoryKey     AS sales_territory_key,

    -- Identifiants
    f.SalesOrderNumber      AS order_number,
    f.SalesOrderLineNumber  AS order_line_number,

    -- Dates
    f.OrderDate             AS order_date,
    f.ShipDate              AS ship_date,
    f.DueDate               AS due_date,

    -- Mesures FLOW (additives)
    f.OrderQuantity         AS quantity,
    f.SalesAmount           AS sales_amount,
    f.TotalProductCost      AS total_cost,
    f.DiscountAmount        AS discount_amount,
    f.TaxAmt                AS tax_amount,
    f.Freight               AS freight,

    -- Mesures VPU (non additives, conservées pour analyse)
    f.UnitPrice             AS unit_price,
    f.UnitPriceDiscountPct  AS discount_pct,

    -- Mesure calculée
    f.SalesAmount - f.TotalProductCost AS margin

FROM staging.stg_fact_reseller_sales f

-- Vérifier que les clés existent dans les dimensions
WHERE EXISTS (SELECT 1 FROM dw.dim_product p WHERE p.product_key = f.ProductKey)
  AND EXISTS (SELECT 1 FROM dw.dim_reseller r WHERE r.reseller_key = f.ResellerKey)
  AND EXISTS (SELECT 1 FROM dw.dim_employee e WHERE e.employee_key = f.EmployeeKey)
  AND EXISTS (SELECT 1 FROM dw.dim_date d WHERE d.date_key = f.OrderDateKey);
```

- [ ] Créer `dw.fact_reseller_sales`
- [ ] Comparer le comptage avec la table staging (des lignes ont-elles été filtrées ?)

### 3.2 Vérifier le partitionnement et le clustering

```sql
-- Vérifier les métadonnées de la table
SELECT
  table_name,
  partition_column,
  clustering_columns
FROM `INFORMATION_SCHEMA.TABLE_OPTIONS`
WHERE table_name = 'fact_reseller_sales';
```

---

## 4. Validation du Core DW

### 4.1 Contrôle de cohérence staging vs dw

```sql
-- Le total SalesAmount doit être identique
SELECT
  (SELECT SUM(SalesAmount) FROM staging.stg_fact_reseller_sales) AS staging_total,
  (SELECT SUM(sales_amount) FROM dw.fact_reseller_sales) AS dw_total;
-- Si différence → des lignes ont été filtrées (clés invalides)
```

- [ ] Vérifier la cohérence des totaux entre staging et dw
- [ ] Si écart, expliquer pourquoi (combien de lignes filtrées ? quelles clés manquantes ?)

### 4.2 Requêtes de validation

Exécutez ces requêtes pour vérifier que le modèle fonctionne :

```sql
-- 1. CA par année
SELECT d.annee, SUM(f.sales_amount) as ca
FROM dw.fact_reseller_sales f
JOIN dw.dim_date d ON f.order_date_key = d.date_key
GROUP BY d.annee
ORDER BY d.annee;

-- 2. Top 5 produits par CA
SELECT p.product_name, SUM(f.sales_amount) as ca
FROM dw.fact_reseller_sales f
JOIN dw.dim_product p ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY ca DESC
LIMIT 5;

-- 3. CA par pays
SELECT g.country_name, SUM(f.sales_amount) as ca
FROM dw.fact_reseller_sales f
JOIN dw.dim_reseller r ON f.reseller_key = r.reseller_key
JOIN dw.dim_geography g ON r.geography_key = g.geography_key
GROUP BY g.country_name
ORDER BY ca DESC;
```

- [ ] Exécuter les 3 requêtes de validation
- [ ] Vérifier que les résultats sont cohérents (pas de valeurs absurdes)

### 4.3 Logger les transformations

```sql
INSERT INTO meta.pipeline_logs (step_name, source_table, target_table, started_at, finished_at, rows_processed, status)
VALUES
  ('dw_transform', 'staging.stg_dim_date', 'dw.dim_date', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM dw.dim_date), 'SUCCESS'),
  ('dw_transform', 'staging.stg_dim_product', 'dw.dim_product', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(),
   (SELECT COUNT(*) FROM dw.dim_product), 'SUCCESS'),
  -- Compléter pour les autres tables...
;
```

- [ ] Logger toutes les transformations dans `meta.pipeline_logs`

---

## Livrables — Partie 3

1. **Scripts SQL** de création des 5 dimensions (`dw.dim_*`)
2. **Script SQL** de création de la table de faits (`dw.fact_reseller_sales`)
3. **Résultats des contrôles** de cohérence staging vs dw
4. **Résultats des 3 requêtes** de validation (CA par année, top produits, CA par pays)
5. **Documentation** des transformations appliquées (en commentaires SQL ou document séparé)
