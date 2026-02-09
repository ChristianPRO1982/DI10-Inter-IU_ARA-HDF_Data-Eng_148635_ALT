# Brief : Construction d'un Data Warehouse et de Data Marts avec BigQuery

## Partie 0 — Veille : Concepts DW, OLAP et BigQuery

---

# Partie 4 — Data Marts & KPI métier

## Objectifs

À l'issue de cette partie, vous serez capable de :

- créer des **Data Marts** orientés usage métier ;
- écrire des **requêtes d'agrégation** avancées (ROLLUP, CUBE, window functions) ;
- calculer des **KPI métiers** pertinents ;
- optimiser les tables pour la **consommation BI**.

---

## 1. Architecture des Data Marts

```
          dw                              marts
┌──────────────────────┐           ┌──────────────────────┐
│ fact_reseller_sales  │           │                      │
│ dim_date             │──────────►│  mart_sales          │
│ dim_product          │           │  (CA, marge, volume) │
│ dim_reseller         │           │                      │
│ dim_employee         │──────────►│  mart_products       │
│ dim_geography        │           │  (perf produit)      │
│                      │           │                      │
│                      │──────────►│  mart_customers      │
│                      │           │  (perf revendeur)    │
└──────────────────────┘           └──────────────────────┘
```

Chaque Data Mart est une table **dénormalisée** et **pré-agrégée** optimisée pour un usage spécifique.

---

## 2. Data Mart Ventes — `marts.mart_sales`

### 2.1 Table d'agrégation quotidienne

Créez une table `marts.mart_sales_daily` contenant les KPI de vente agrégés par jour, pays et catégorie de revendeur.

**Colonnes attendues :**

| Colonne | Source / Calcul |
|---------|-----------------|
| `order_date` | `fact.order_date` |
| `annee` | `dim_date.annee` |
| `trimestre` | `dim_date.trimestre` |
| `mois` | `dim_date.num_mois` |
| `nom_mois` | `dim_date.nom_mois` |
| `country_name` | `dim_geography.country_name` |
| `business_type` | `dim_reseller.business_type` |
| `nb_orders` | `COUNT(DISTINCT order_number)` |
| `nb_lines` | `COUNT(*)` |
| `total_quantity` | `SUM(quantity)` |
| `total_revenue` | `SUM(sales_amount)` |
| `total_cost` | `SUM(total_cost)` |
| `total_margin` | `SUM(margin)` |
| `total_discount` | `SUM(discount_amount)` |
| `total_tax` | `SUM(tax_amount)` |
| `total_freight` | `SUM(freight)` |
| `avg_order_value` | `total_revenue / nb_orders` |
| `margin_pct` | `total_margin / total_revenue * 100` |

```sql
-- À compléter
CREATE OR REPLACE TABLE marts.mart_sales_daily
PARTITION BY order_date
CLUSTER BY country_name
AS
SELECT
    f.order_date,
    d.annee,
    d.trimestre,
    d.num_mois AS mois,
    d.nom_mois,
    g.country_name,
    r.business_type,

    -- KPI
    COUNT(DISTINCT f.order_number) AS nb_orders,
    ______ AS nb_lines,
    ______ AS total_quantity,
    ______ AS total_revenue,
    ______ AS total_cost,
    ______ AS total_margin,
    ______ AS total_discount,
    ______ AS total_tax,
    ______ AS total_freight,

    -- KPI calculés
    SAFE_DIVIDE(SUM(f.sales_amount), COUNT(DISTINCT f.order_number)) AS avg_order_value,
    SAFE_DIVIDE(______, ______) * 100 AS margin_pct

FROM dw.fact_reseller_sales f
JOIN dw.dim_date d ON f.order_date_key = d.date_key
JOIN dw.dim_reseller r ON f.reseller_key = r.reseller_key
JOIN dw.dim_geography g ON r.geography_key = g.geography_key
GROUP BY 1, 2, 3, 4, 5, 6, 7;
```

- [ ] Créer `marts.mart_sales_daily`
- [ ] Vérifier : `SELECT SUM(total_revenue) FROM marts.mart_sales_daily` doit correspondre au total dans `dw.fact_reseller_sales`

### 2.2 Requêtes OLAP sur mart_sales

Utilisez `marts.mart_sales_daily` pour les analyses suivantes :

**a) CA avec sous-totaux par pays et business_type (ROLLUP)**

```sql
SELECT
    IFNULL(country_name, '*** TOTAL ***') AS country,
    IFNULL(business_type, '** Sous-total **') AS type,
    SUM(total_revenue) AS ca,
    SUM(total_margin) AS marge
FROM marts.mart_sales_daily
WHERE annee = 2013
GROUP BY ROLLUP(country_name, business_type)
ORDER BY country_name NULLS LAST, business_type NULLS LAST;
```

- [ ] Exécuter et analyser le résultat

**b) Toutes les combinaisons pays x trimestre (CUBE)**

```sql
-- À compléter : CUBE sur country_name et trimestre
-- pour l'année 2013
```

- [ ] Écrire et exécuter la requête CUBE

**c) Évolution mensuelle avec croissance (window function)**

```sql
-- CA mensuel avec delta vs mois précédent
SELECT
    annee,
    mois,
    nom_mois,
    SUM(total_revenue) AS ca_mensuel,
    LAG(SUM(total_revenue)) OVER (ORDER BY annee, mois) AS ca_mois_precedent,
    ROUND(
        SAFE_DIVIDE(
            SUM(total_revenue) - LAG(SUM(total_revenue)) OVER (ORDER BY annee, mois),
            LAG(SUM(total_revenue)) OVER (ORDER BY annee, mois)
        ) * 100, 2
    ) AS croissance_pct
FROM marts.mart_sales_daily
GROUP BY annee, mois, nom_mois
ORDER BY annee, mois;
```

- [ ] Exécuter et identifier les mois de plus forte croissance

**d) CA cumulé par année**

```sql
-- À compléter : SUM() OVER avec PARTITION BY annee ORDER BY mois
```

- [ ] Écrire la requête de CA cumulé

---

## 3. Data Mart Produits — `marts.mart_products`

### 3.1 Performance par produit

Créez `marts.mart_products` avec les métriques par produit :

**Colonnes attendues :**

| Colonne | Calcul |
|---------|--------|
| `product_key` | clé produit |
| `product_name` | nom du produit |
| `color` | couleur |
| `total_revenue` | SUM(sales_amount) |
| `total_quantity` | SUM(quantity) |
| `total_margin` | SUM(margin) |
| `margin_pct` | marge / revenue * 100 |
| `nb_orders` | COUNT(DISTINCT order_number) |
| `avg_unit_price` | AVG(unit_price) |
| `revenue_rank` | RANK() par CA |
| `revenue_contribution_pct` | CA produit / CA total * 100 |

```sql
-- À compléter
CREATE OR REPLACE TABLE marts.mart_products AS
SELECT
    p.product_key,
    p.product_name,
    p.color,

    -- Métriques
    SUM(f.sales_amount) AS total_revenue,
    ______ AS total_quantity,
    ______ AS total_margin,
    ______ AS margin_pct,
    ______ AS nb_orders,
    ______ AS avg_unit_price,

    -- Classement
    RANK() OVER (ORDER BY SUM(f.sales_amount) DESC) AS revenue_rank,

    -- Contribution au CA total
    ROUND(
        SUM(f.sales_amount) * 100.0 /
        SUM(SUM(f.sales_amount)) OVER (),
        2
    ) AS revenue_contribution_pct

FROM dw.fact_reseller_sales f
JOIN dw.dim_product p ON f.product_key = p.product_key
GROUP BY p.product_key, p.product_name, p.color;
```

- [ ] Créer `marts.mart_products`

### 3.2 Requêtes d'analyse produit

**a) Top 10 produits par CA**

```sql
SELECT product_name, total_revenue, revenue_rank, revenue_contribution_pct
FROM marts.mart_products
WHERE revenue_rank <= 10
ORDER BY revenue_rank;
```

**b) Top 10 produits par marge**

```sql
-- À compléter
```

**c) Produits représentant 80% du CA (loi de Pareto)**

```sql
-- À compléter : CA cumulé, et filtrer quand le cumul atteint 80%
-- Indice : utiliser SUM() OVER (ORDER BY total_revenue DESC) pour le cumul
```

- [ ] Exécuter les 3 requêtes d'analyse produit

---

## 4. Data Mart Revendeurs — `marts.mart_customers`

### 4.1 Vue Customer 360 (Reseller 360)

Créez `marts.mart_customers` avec les métriques par revendeur :

**Colonnes attendues :**

| Colonne | Calcul |
|---------|--------|
| `reseller_key` | clé revendeur |
| `reseller_name` | nom |
| `business_type` | type (Warehouse, VAR, Specialty) |
| `country_name` | pays |
| `first_order_date` | MIN(order_date) |
| `last_order_date` | MAX(order_date) |
| `nb_orders` | COUNT(DISTINCT order_number) |
| `total_items` | SUM(quantity) |
| `lifetime_value` | SUM(sales_amount) |
| `total_margin` | SUM(margin) |
| `avg_order_value` | lifetime_value / nb_orders |
| `order_frequency_days` | durée / nb_orders (jours entre commandes) |
| `days_since_last_order` | DATE_DIFF(MAX date dans le dataset, last_order_date) |
| `customer_status` | Active / At Risk / Churned |

**Règles de statut :**
- **Active** : dernière commande < 180 jours avant la fin du dataset
- **At Risk** : entre 180 et 365 jours
- **Churned** : > 365 jours

```sql
-- À compléter
CREATE OR REPLACE TABLE marts.mart_customers AS
WITH max_date AS (
    SELECT MAX(order_date) AS dataset_end_date
    FROM dw.fact_reseller_sales
)
SELECT
    r.reseller_key,
    r.reseller_name,
    r.business_type,
    g.country_name,

    -- Temporel
    MIN(f.order_date) AS first_order_date,
    MAX(f.order_date) AS last_order_date,

    -- Volume
    COUNT(DISTINCT f.order_number) AS nb_orders,
    SUM(f.quantity) AS total_items,
    SUM(f.sales_amount) AS lifetime_value,
    SUM(f.margin) AS total_margin,

    -- Moyennes
    SAFE_DIVIDE(SUM(f.sales_amount), COUNT(DISTINCT f.order_number)) AS avg_order_value,

    -- Fréquence
    SAFE_DIVIDE(
        DATE_DIFF(MAX(f.order_date), MIN(f.order_date), DAY),
        GREATEST(COUNT(DISTINCT f.order_number) - 1, 1)
    ) AS order_frequency_days,

    -- Récence
    DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) AS days_since_last_order,

    -- Statut
    CASE
        WHEN DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) < 180 THEN 'Active'
        WHEN DATE_DIFF(md.dataset_end_date, MAX(f.order_date), DAY) < 365 THEN 'At Risk'
        ELSE 'Churned'
    END AS customer_status

FROM dw.fact_reseller_sales f
JOIN dw.dim_reseller r ON f.reseller_key = r.reseller_key
JOIN dw.dim_geography g ON r.geography_key = g.geography_key
CROSS JOIN max_date md
GROUP BY r.reseller_key, r.reseller_name, r.business_type, g.country_name, md.dataset_end_date;
```

- [ ] Créer `marts.mart_customers`

### 4.2 Requêtes d'analyse revendeur

**a) Répartition des statuts**

```sql
SELECT
    customer_status,
    COUNT(*) AS nb_resellers,
    SUM(lifetime_value) AS total_ltv,
    ROUND(AVG(lifetime_value), 2) AS avg_ltv
FROM marts.mart_customers
GROUP BY customer_status
ORDER BY total_ltv DESC;
```

**b) Top 10 revendeurs par lifetime value**

```sql
-- À compléter
```

**c) Segmentation par quartile (NTILE)**

```sql
-- À compléter : segmenter les revendeurs en 4 groupes (quartiles)
-- selon leur lifetime_value
-- Résultat : reseller_name, lifetime_value, quartile
```

- [ ] Exécuter les 3 requêtes d'analyse revendeur

---

## 5. Requêtes KPI pour la direction

Répondez aux questions suivantes avec des requêtes SQL sur vos Data Marts :

1. **Quel est le chiffre d'affaires total par année ?**
2. **Quels sont les 5 pays avec le plus de CA ?**
3. **Quel est le taux de marge moyen par type de revendeur ?**
4. **Quels sont les 3 mois les plus performants (tous les temps confondus) ?**
5. **Combien de revendeurs sont "Churned" et quel CA ils représentaient ?**
6. **Quel produit a le meilleur ratio marge/CA ?**
7. **Quelle est la croissance annuelle du CA (2011 vs 2012, 2012 vs 2013) ?**

- [ ] Écrire et exécuter les 7 requêtes
- [ ] Documenter les résultats (valeurs + interprétation en 1 phrase)

---

## Livrables — Partie 4

1. **Scripts SQL** de création des 3 Data Marts
2. **Requêtes OLAP** (ROLLUP, CUBE, window functions) exécutées avec résultats
3. **Requêtes d'analyse** produit et revendeur
4. **7 requêtes KPI** avec résultats et interprétation
5. **Vérification de cohérence** : total revenue du mart == total revenue du DW
