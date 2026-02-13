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

| KPI                        | Formule SQL (logique)                               | Table source     | Interprétation métier                    |
| -------------------------- | --------------------------------------------------- | ---------------- | ---------------------------------------- |
| **CA total**               | `SUM(total_revenue)`                                | mart_sales_daily | Chiffre d’affaires global sur la période |
| **Marge totale**           | `SUM(total_margin)`                                 | mart_sales_daily | Profit brut généré                       |
| **Taux de marge global**   | `SUM(total_margin) / SUM(total_revenue) * 100`      | mart_sales_daily | Rentabilité globale                      |
| **CA Année N**             | `SUM(total_revenue) WHERE annee = N`                | mart_sales_daily | Performance annuelle                     |
| **Croissance annuelle**    | `(CA N - CA N-1) / CA N-1 * 100`                    | mart_sales_daily | Dynamique de croissance                  |
| **Top pays par CA**        | `SUM(total_revenue) GROUP BY country_name`          | mart_sales_daily | Marché le plus contributeur              |
| **Panier moyen**           | `SUM(total_revenue) / COUNT(DISTINCT order_number)` | mart_sales_daily | Valeur moyenne par commande              |
| **Nombre de commandes**    | `COUNT(DISTINCT order_number)`                      | mart_sales_daily | Volume d’activité                        |
| **Quantité totale vendue** | `SUM(total_quantity)`                               | mart_sales_daily | Volume physique vendu                    |
| **Top produit par CA**     | `ORDER BY total_revenue DESC LIMIT 1`               | mart_products    | Produit le plus générateur de CA         |
| **Taux de marge produit**  | `SUM(margin) / SUM(total_revenue) * 100`            | mart_products    | Rentabilité par produit                  |
| **Contribution au CA (%)** | `total_revenue / SUM(total_revenue) OVER () * 100`  | mart_products    | Part de CA d’un produit                  |
| **Revenue Rank**           | `RANK() OVER (ORDER BY total_revenue DESC)`         | mart_products    | Classement des produits                  |
| **LTV (Lifetime Value)**   | `SUM(total_revenue) par reseller`                   | mart_customers   | Valeur vie client                        |
| **Marge client totale**    | `SUM(total_margin)`                                 | mart_customers   | Profit généré par client                 |
| **Fréquence de commande**  | `DATE_DIFF(max_date, min_date) / (nb_orders - 1)`   | mart_customers   | Intervalle moyen entre commandes         |
| **Days since last order**  | `DATE_DIFF(max_dataset_date, last_order_date)`      | mart_customers   | Récence client                           |
| **Statut client**          | CASE basé sur récence                               | mart_customers   | Segmentation Active / At Risk / Churned  |
| **% Clients actifs**       | `COUNTIF(status='Active') / COUNT(*) * 100`         | mart_customers   | Santé du portefeuille                    |

---

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
