# PARTIE 4 - 2. sections 5 - KPI

## 🧭 Étape 10 — 7 KPI Direction Générale

Objectif :
Produire une synthèse exécutive basée sur les marts.

---

## 📊 KPI 1 — Chiffre d’Affaires Total

```sql
SELECT
  SUM(total_revenue) AS chiffre_affaires_total
FROM `adventureworks-dw-christian.marts.mart_sales_daily`;
```

**Résultats**

> **C.A. Total ≈** 80 450 596,98

## 💰 KPI 2 — Marge Totale & Taux de Marge Global

```sql
SELECT
  SUM(total_margin) AS marge_totale,
  ROUND(
    SAFE_DIVIDE(
      SUM(total_margin),
      SUM(total_revenue)
    ) * 100,
    2
  ) AS taux_marge_pct
FROM `adventureworks-dw-christian.marts.mart_sales_daily`;
```

**Résultats**

| marge_totale | taux_marge_pct |
|-------------:|---------------:|
| 470482,6033  | 0,58%          |

**commentaire**

*C'est un taux de marge global extrêmement faible.*

## 📈 KPI 3 — CA Année N (2013)

```sql
SELECT
  SUM(total_revenue) AS ca_2013
FROM `adventureworks-dw-christian.marts.mart_sales_daily`
WHERE annee = 2013;
```

**Résultats**

> **C.A. 2013 ≈** 33 574 834.15

## 🚀 KPI 4 — Croissance 2013 vs 2012

```sql
WITH yearly AS (
  SELECT
    annee,
    SUM(total_revenue) AS ca
  FROM `adventureworks-dw-christian.marts.mart_sales_daily`
  GROUP BY annee
)

SELECT
  ROUND(
    SAFE_DIVIDE(
      MAX(CASE WHEN annee = 2013 THEN ca END)
      -
      MAX(CASE WHEN annee = 2012 THEN ca END),
      MAX(CASE WHEN annee = 2012 THEN ca END)
    ) * 100,
    2
  ) AS croissance_2013_vs_2012_pct
FROM yearly;
```

**Résultats**

> **Croissance 2013 =** 19.09%

## 🏆 KPI 5 — Top Pays par CA

```sql
SELECT
  country_name,
  SUM(total_revenue) AS ca_total
FROM `adventureworks-dw-christian.marts.mart_sales_daily`
GROUP BY country_name
ORDER BY ca_total DESC
LIMIT 1;
```

**Résultats**

| country_name   | ca_total       |
|----------------|---------------:|
| United States  | 53607801,21    |

**commentaire**

*Dominance géographique claire mais cohérent.*

## 🛍 KPI 6 — Top Produit par CA

```sql
SELECT
  product_name,
  total_revenue
FROM `adventureworks-dw-christian.marts.mart_products`
ORDER BY total_revenue DESC
LIMIT 1;
```

**Résultats**

| product_name               | total_revenue |
|----------------------------|--------------:|
| Mountain-200 Black; 38     | 1634647,937   |

## 👥 KPI 7 — % Clients Actifs

```sql
SELECT
  ROUND(
    COUNTIF(customer_status = 'Active') * 100.0
    / COUNT(*),
    2
  ) AS pct_clients_actifs
FROM `adventureworks-dw-christian.marts.mart_customers`;
```

**Résultats**

> **Clients Actifs =** 73.39%

---
---
---
---
---

> [SUITE DU RENDU ICI](https://github.com/ChristianPRO1982/DI10-Inter-IU_ARA-HDF_Data-Eng_148635_ALT/blob/main/RENDU%20DU%20BRIEF/PARTIE%205%20-%201.%20sections%201%20%C3%A0%204.md)