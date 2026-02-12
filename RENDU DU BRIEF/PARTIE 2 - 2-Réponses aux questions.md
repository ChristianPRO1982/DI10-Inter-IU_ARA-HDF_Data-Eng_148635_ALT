# PARTIE 2 - 2-Réponses aux questions

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

## 🧭 Étape 21 — Vérification des doublons (grain technique)

```sql
SELECT
  SalesOrderNumber,
  SalesOrderLineNumber,
  COUNT(*) AS nb
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`
GROUP BY 1, 2
HAVING COUNT(*) > 1;
```

**résultats :**

Pas de résultat > OK

## 🧭 Étape 22 — Intégrité référentielle (FACT → dimensions)

```sql
SELECT DISTINCT f.ProductKey
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales` AS f
LEFT JOIN `adventureworks-dw-christian.staging.stg_dim_product` AS p
  ON f.ProductKey = p.ProductKey
WHERE p.ProductKey IS NULL;
```

**résultats :**

Pas de résultat > OK

## 🧭 Étape 23 — Intégrité référentielle : ResellerKey → stg_dim_reseller

```sql
SELECT DISTINCT f.ResellerKey
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales` AS f
LEFT JOIN `adventureworks-dw-christian.staging.stg_dim_reseller` AS r
  ON f.ResellerKey = r.ResellerKey
WHERE r.ResellerKey IS NULL;
```

**résultats :**

Pas de résultat > OK

## 🧭 Étape 24 — Intégrité référentielle : EmployeeKey → stg_dim_employee

```sql
SELECT DISTINCT f.EmployeeKey
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales` AS f
LEFT JOIN `adventureworks-dw-christian.staging.stg_dim_employee` AS e
  ON f.EmployeeKey = e.EmployeeKey
WHERE e.EmployeeKey IS NULL;
```

**résultats :**

Pas de résultat > OK

## 🧭 Étape 25 — Intégrité référentielle : SalesTerritoryKey (FACT) → SalesTerritoryKey (DimGeography)

```sql
SELECT DISTINCT f.SalesTerritoryKey
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales` AS f
LEFT JOIN `adventureworks-dw-christian.staging.stg_dim_geography` AS g
  ON f.SalesTerritoryKey = g.SalesTerritoryKey
WHERE g.SalesTerritoryKey IS NULL;
```

**résultats :**

Pas de résultat > OK

## 🧭 Étape 26 — Statistiques descriptives (FACT)

```sql
SELECT
  MIN(SalesAmount) AS min_sales,
  MAX(SalesAmount) AS max_sales,
  AVG(SalesAmount) AS avg_sales,
  MIN(OrderDate) AS min_order_date,
  MAX(OrderDate) AS max_order_date,
  COUNT(DISTINCT SalesOrderNumber) AS nb_orders
FROM `adventureworks-dw-christian.staging.stg_fact_reseller_sales`;
```

**résultats :**

min_sales	max_sales	avg_sales	min_order_date	max_order_date	nb_orders
1,374	27893,619	1322,004716	29/12/2010 00:00:00	29/11/2013 00:00:00	3796