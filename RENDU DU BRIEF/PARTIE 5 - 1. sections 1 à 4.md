# PARTIE 5 - 1. sections 1 à 4

## 🧭 Étape 1 — Audit & Optimisation des tables

## 1.1 — Audit du partitionnement et du clustering

```sql
WITH all_tables AS (
  SELECT
    'dw' AS dataset_name,
    table_name,
    ddl
  FROM `adventureworks-dw-christian.dw.INFORMATION_SCHEMA.TABLES`

  UNION ALL

  SELECT
    'marts' AS dataset_name,
    table_name,
    ddl
  FROM `adventureworks-dw-christian.marts.INFORMATION_SCHEMA.TABLES`
)
SELECT
  dataset_name,
  table_name,
  REGEXP_EXTRACT(ddl, r'PARTITION BY\s+([^\n]+)') AS partition_by,
  REGEXP_EXTRACT(ddl, r'CLUSTER BY\s+([^\n]+)') AS cluster_by
FROM all_tables
ORDER BY dataset_name, table_name;
```

**résultats**

| dataset_name | table_name           | partition_by | cluster_by                    |
|--------------|----------------------|--------------|-------------------------------|
| dw           | dim_date             |              |                               |
| dw           | dim_employee         |              |                               |
| dw           | dim_geography        |              |                               |
| dw           | dim_product          |              |                               |
| dw           | dim_reseller         |              |                               |
| dw           | fact_reseller_sales  | order_date   | product_key, reseller_key     |
| marts        | mart_customers       |              | business_type, country_name   |
| marts        | mart_products        |              |                               |
| marts        | mart_sales_daily     | order_date   | country_name                  |

**✅ audit OK et conforme**

## 🧭 Étape 1.2 — Analyse des coûts et impact du partitionnement

### 1.2.1 — Comparer une requête sans filtre vs avec filtre date

**Requête A — sans filtre (scanne tout)**

```sql
SELECT
  SUM(sales_amount) AS total_ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales`;
```

**Requête B — avec filtre sur la partition (scanne une partie)**

```sql
SELECT
  SUM(sales_amount) AS total_ca_2013
FROM `adventureworks-dw-christian.dw.fact_reseller_sales`
WHERE order_date BETWEEN '2013-01-01' AND '2013-12-31';
```

### 1.2.2 — 📊 Résultats observés

| Requête         | Octets traités | Octets facturés | Slot ms |
| --------------- | -------------- | --------------- | ------- |
| A (sans filtre) | 475,43 Ko      | 10 Mo           | 149 ms  |
| B (filtre 2013) | 445,94 Ko      | 10 Mo           | 58 ms   |

**🔎 Analyse des coûts et du partitionnement**

La comparaison entre une requête sans filtre et une requête filtrée sur la colonne de partition montre :

* Une légère réduction des données traitées (475 Ko → 446 Ko).
* Une amélioration du temps d’exécution (149 ms → 58 ms).
* Aucun impact sur les octets facturés (10 Mo), en raison du minimum de facturation BigQuery.

Le gain est limité ici car la table est de petite taille (~60 000 lignes).
Dans un environnement réel avec des tables de plusieurs Go ou To, le partitionnement permettrait une réduction massive des données scannées et donc des coûts.

🎯 Conclusion :

* Partitionnement correctement implémenté
* Impact visible sur la performance
* Impact financier limité ici à cause du faible volume

