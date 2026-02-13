# 📦 AdventureWorks – Data Warehouse & Data Marts (BigQuery)

## 1️⃣ Architecture

### 🔁 Schéma global

```
staging  →  dw  →  marts
```

### 🗂 Datasets et tables

#### 📥 `staging`

Tables sources brutes (import AdventureWorks) :

* `stg_dim_date`
* `stg_dim_employee`
* `stg_dim_geography`
* `stg_dim_product`
* `stg_dim_reseller`
* `stg_fact_reseller_sales`

#### 🏗 `dw`

Modèle en étoile (tables nettoyées / transformées) :

* `dim_date`
* `dim_employee`
* `dim_geography`
* `dim_product`
* `dim_reseller`
* `fact_reseller_sales`

#### 📊 `marts`

Tables analytiques pré-agrégées :

* `mart_sales_daily`
* `mart_products`
* `mart_customers`

#### 📝 `meta`

* `pipeline_logs` (historique des exécutions)

---

## 2️⃣ Données sources

### 📘 Contexte

Le dataset provient de **AdventureWorks Data Warehouse**, base fictive Microsoft représentant une entreprise de vente de vélos et équipements sportifs.

### 📊 Volumétrie

* ~60 855 lignes dans `fact_reseller_sales`
* 395 produits
* 635 revendeurs
* 1 826 dates
* 655 géographies

Dataset de taille modérée, idéal pour :

* démonstration de partitioning/clustering
* mise en place de pipeline
* modélisation OLAP

---

## 3️⃣ Modèle de données

### ⭐ Schéma en étoile

#### 📌 Table de faits

`fact_reseller_sales`

Mesures :

* quantity
* sales_amount
* total_cost
* margin
* discount_amount
* tax_amount
* freight

Clés étrangères :

* product_key
* reseller_key
* employee_key
* order_date_key

Partitionnée par :

* `order_date`

Clusterisée par :

* `product_key`
* `reseller_key`

---

#### 📐 Dimensions

* `dim_date`
* `dim_product`
* `dim_reseller`
* `dim_geography`
* `dim_employee`

Les dimensions enrichissent les axes d’analyse :

* Temps (année, trimestre, mois)
* Produit
* Revendeur
* Géographie
* Organisation interne

---

## 4️⃣ Data Marts

### 📅 `mart_sales_daily`

Grain :
Jour × Pays × Type de revendeur

KPI :

* nb_orders
* nb_lines
* total_quantity
* total_revenue
* total_cost
* total_margin
* avg_order_value
* margin_pct

Optimisation :

* Partition par `order_date`
* Cluster par `country_name`

Usage :

* Analyse temporelle
* Reporting pays / business type
* Suivi performance commerciale

---

### 🛒 `mart_products`

Grain :
Produit

KPI :

* total_revenue
* total_quantity
* total_margin
* margin_pct
* nb_orders
* avg_unit_price
* revenue_rank
* revenue_contribution_pct (Pareto)

Usage :

* Top produits
* Analyse Pareto 80/20
* Rentabilité produit

---

### 👥 `mart_customers`

Grain :
Revendeur

KPI :

* lifetime_value
* total_margin
* nb_orders
* avg_order_value
* order_frequency_days
* days_since_last_order
* customer_status (Active / At Risk / Churned)

Usage :

* Analyse LTV
* Segmentation commerciale
* Pilotage churn

---

## 5️⃣ Pipeline

### 🔄 Exécution manuelle

#### Rafraîchir le DW :

```sql
CALL `meta.sp_refresh_dw`();
```

#### Rafraîchir les marts :

```sql
CALL `meta.sp_refresh_marts`();
```

#### Pipeline complet :

```sql
CALL `meta.sp_run_full_pipeline`();
```

---

### ⚙️ Fonctionnement

`sp_run_full_pipeline()` :

1. Refresh `dw` depuis `staging`
2. Refresh `marts` depuis `dw`
3. Log global dans `meta.pipeline_logs`

---

## 6️⃣ Optimisation

### 🧩 Partitionnement

`fact_reseller_sales` partitionnée par `order_date`

→ Permet :

* partition pruning
* réduction des scans temporels
* optimisation des coûts

`mart_sales_daily` partitionnée par `order_date`
→ cohérent avec usage analytique temps.

---

### 🔗 Clustering

Choix effectués :

| Table               | Clustering                  |
| ------------------- | --------------------------- |
| fact_reseller_sales | product_key, reseller_key   |
| mart_sales_daily    | country_name                |
| mart_products       | product_name                |
| mart_customers      | business_type, country_name |

Justification :

* Les dimensions les plus utilisées en filtres
* Optimisation des GROUP BY fréquents
* Amélioration des performances sur agrégations

---

## 7️⃣ Monitoring

### 📊 Logs pipeline

Table : `meta.pipeline_logs`

Colonnes principales :

* step_name
* source_table
* target_table
* started_at
* finished_at
* rows_processed
* status

---

### 🔎 Vérifier l’état du pipeline

```sql
SELECT *
FROM `meta.pipeline_logs`
ORDER BY finished_at DESC
LIMIT 10;
```

Permet de :

* voir les SUCCESS / ERROR
* vérifier la volumétrie traitée
* contrôler la durée d’exécution

---
---
---

## 📊 Documentation des KPI

### Tableau récapitulatif des KPI

| KPI                           | Formule SQL (logique)                               | Table source     | Résultat obtenu                | Interprétation métier           |
| ----------------------------- | --------------------------------------------------- | ---------------- | ------------------------------ | ------------------------------- |
| **CA total**                  | `SUM(total_revenue)`                                | mart_sales_daily | **80 450 596,98**              | Chiffre d’affaires global       |
| **Marge totale**              | `SUM(total_margin)`                                 | mart_sales_daily | **470 482**                | Profit brut global (négatif)    |
| **Taux de marge global**      | `SUM(margin) / SUM(revenue) * 100`                  | mart_sales_daily | **≈ 0,58 %**                  | Rentabilité globale faible      |
| **Panier moyen global**       | `SUM(total_revenue) / COUNT(DISTINCT order_number)` | mart_sales_daily | ≈ **1 322 €**                  | Valeur moyenne par commande     |
| **Nombre total de commandes** | `COUNT(DISTINCT order_number)`                      | mart_sales_daily | **60 855 lignes fact**         | Activité commerciale globale    |
| **Quantité totale vendue**    | `SUM(total_quantity)`                               | mart_sales_daily | (calculé dans mart)            | Volume physique vendu           |
| **Top pays par CA**           | `SUM(total_revenue) GROUP BY country_name`          | mart_sales_daily | **United States : 19 200 388** | Marché principal                |
| **Top produit (CA)**          | `ORDER BY total_revenue DESC`                       | mart_products    | Mountain-200 Black; 38         | Produit leader                  |
| **Contribution Top produit**  | `revenue_contribution_pct`                          | mart_products    | **2,03 %**                     | Produit individuel peu dominant |
| **Produits pour 80 % du CA**  | Pareto cumulatif                                    | mart_products    | ~80 % atteint vers 80e produit | Distribution concentrée         |
| **Nombre total produits**     | `COUNT(DISTINCT product_key)`                       | mart_products    | **334 produits**               | Large catalogue                 |
| **Nombre total revendeurs**   | `COUNT(DISTINCT reseller_key)`                      | mart_customers   | **635 revendeurs**             | Base client B2B                 |
| **LTV max**                   | `MAX(lifetime_value)`                               | mart_customers   | **877 107**                    | Meilleur client                 |
| **LTV total portefeuille**    | `SUM(lifetime_value)`                               | mart_customers   | **80 450 596,98**              | Cohérent avec CA global         |
| **Clients actifs**            | `COUNTIF(status='Active')`                          | mart_customers   | **466 (73 %)**                 | Portefeuille sain               |
| **Clients churned**           | `COUNTIF(status='Churned')`                         | mart_customers   | **142 (22 %)**                 | Attrition significative         |
| **Clients at risk**           | `COUNTIF(status='At Risk')`                         | mart_customers   | **27 (4 %)**                   | Clients à surveiller            |

### 📌 Lecture stratégique rapide

#### 💰 Rentabilité

* CA important (~80M)
* Marge globale légèrement négative
  → Problème de pricing ou structure de coûts

#### 🌍 Géographie

* USA = principal moteur de croissance
* Autres pays plus fragmentés

#### 🛒 Produits

* Aucun produit ne dépasse 3 % du CA
* Modèle très diversifié
* Pareto valide : ~20 % des produits génèrent ~80 % du CA

#### 👥 Clients

* 73 % actifs → portefeuille plutôt sain
* 22 % churned → potentiel d’amélioration CRM
* Forte concentration LTV sur top clients

### 🎯 Synthèse stratégique des KPI

Les KPI couvrent 4 axes majeurs :

1. **Performance financière globale**

   * CA
   * Marge
   * Taux de marge
   * Croissance annuelle

2. **Analyse produit**

   * Top produits
   * Contribution au CA
   * Pareto 80/20
   * Rentabilité par produit

3. **Analyse client**

   * LTV
   * Récence
   * Fréquence
   * Segmentation comportementale

4. **Analyse géographique**

   * Top pays
   * Contribution pays
