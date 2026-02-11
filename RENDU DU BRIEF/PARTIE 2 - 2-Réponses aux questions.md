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