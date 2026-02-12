# PARTIE 4 - 1.Création

## 🧭 Étape 9 — Requêtes de validation (les 3 requêtes du brief)

```sql
SELECT d.annee, SUM(f.sales_amount) AS ca
FROM `adventureworks-dw-christian.dw.fact_reseller_sales` f
JOIN `adventureworks-dw-christian.dw.dim_date` d
  ON f.order_date_key = d.date_key
GROUP BY d.annee
ORDER BY d.annee;
```

**résultats**

| Année | Chiffre d’affaires |
|--------|-------------------|
| 2010   | 489 328,58 |
| 2011   | 18 192 802,71 |
| 2012   | 28 193 631,53 |
| 2013   | 33 574 834,16 |

**Analyse :**

- 2010 correspond à une année partielle (décembre uniquement).
- Forte croissance entre 2011 et 2013.
- Le modèle DW permet bien une agrégation temporelle fiable.
