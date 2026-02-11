# Liens entre le SQL et les opérateurs

## 1) Roll-up & Drill-down (changement de granularité)

### ✅ Roll-up (agréger “vers le haut”)

En SQL, c’est **GROUP BY + agrégats**, et quand tu veux *plusieurs niveaux d’agrégation en une requête*, tu utilises :

* `GROUP BY ROLLUP(...)` (hiérarchie)
* ou `GROUP BY GROUPING SETS (...)` (tu choisis explicitement les niveaux)

**Exemple (ROLLUP)** : année → trimestre → total

```sql
SELECT
  year,
  quarter,
  SUM(revenue) AS revenue
FROM sales
GROUP BY ROLLUP(year, quarter);
```

**Lien OLAP :**

* détail (year, quarter)
* sous-total (year)
* total global ()

---

### ✅ Drill-down (détailler “vers le bas”)

SQL n’a pas un mot-clé “DRILLDOWN”. C’est **toi** qui ajoutes un niveau plus fin dans le `GROUP BY`.

**Exemple** : passer de (year) à (year, month)

```sql
SELECT
  year,
  month,
  SUM(revenue) AS revenue
FROM sales
GROUP BY year, month;
```

**Lien OLAP :**

* tu “descends” dans la hiérarchie en ajoutant une colonne de granularité.

---

## 2) Slice & Dice (filtrer le cube)

### ✅ Slice (fixer UNE valeur d’une dimension)

En SQL : **WHERE dimension = valeur**

```sql
SELECT
  product,
  SUM(revenue) AS revenue
FROM sales
WHERE year = 2024
GROUP BY product;
```

---

### ✅ Dice (filtrer sur plusieurs dimensions/valeurs)

En SQL : **WHERE** avec plusieurs conditions (`AND`, `OR`, `IN`, plages, etc.)

```sql
SELECT
  product,
  region,
  SUM(revenue) AS revenue
FROM sales
WHERE year IN (2023, 2024)
  AND region IN ('North', 'South')
  AND product IN ('Gloves', 'Boots')
GROUP BY product, region;
```

---

## 3) Pivot / Rotate (changer la vue)

### ✅ Pivot / Rotate (lignes ↔ colonnes)

En SQL “pur”, tu le fais souvent via :

* soit `PIVOT` (selon le SGBD),
* soit des `SUM(CASE WHEN ...)` (portable).

**Exemple portable :** colonnes par année

```sql
SELECT
  product,
  SUM(CASE WHEN year = 2023 THEN revenue ELSE 0 END) AS revenue_2023,
  SUM(CASE WHEN year = 2024 THEN revenue ELSE 0 END) AS revenue_2024
FROM sales
GROUP BY product;
```

**Lien OLAP :**

* tu “tournes” le cube pour présenter une dimension en colonnes.

---

## 4) “CUBE” en SQL (équivalent “cube complet”)

### ✅ CUBE (toutes les combinaisons)

En SQL : `GROUP BY CUBE(a, b, c)` → produit tous les sous-totaux possibles.

```sql
SELECT
  year,
  region,
  SUM(revenue) AS revenue
FROM sales
GROUP BY CUBE(year, region);
```

---

## 5) Distinguer les vrais NULL vs les NULL “agrégats”

Quand tu utilises `ROLLUP` / `CUBE`, certains champs deviennent `NULL` pour représenter “total”.
SQL fournit `GROUPING(col)` pour savoir si le `NULL` vient d’une agrégation. 

```sql
SELECT
  region,
  SUM(revenue) AS revenue,
  GROUPING(region) AS is_total
FROM sales
GROUP BY ROLLUP(region);
```

* `is_total = 0` → valeur réelle
* `is_total = 1` → ligne de total/sous-total
