# TP — Informatique Décisionnelle & OLAP avec BigQuery

## PARTIE 1 — Prise en main BigQuery

```sql
SELECT
  date,
  city,
  county,
  category_name,
  vendor_name,
  sale_dollars,
  bottles_sold
FROM `bigquery-public-data.iowa_liquor_sales.sales`
LIMIT 1000;
```

**Résultats**

| date | city | county | category_name | vendor_name | sale_dollars | bottles_sold |
|------|------|--------|-------|---------|---------|---------|
| 28/11/2023 | AMES | STORY | CANADIAN WHISKIES | DIAGEO AMERICAS | -629,76 | -24 |
| 29/01/2026 | WEST DES MOINES | POLK | AMERICAN VODKAS | FIFTH GENERATION DISTILLED SPIRITS, INC. | -360 | -24 |
| 30/10/2023 | CLEARLAKE | CERRO GORDO | CANADIAN WHISKIES | DIAGEO AMERICAS | -368,88 | -12 |
| 23/06/2023 | DAVENPORT | SCOTT | AMERICAN VODKAS | MCCORMICK DISTILLING CO. | -79,08 | -12 |
| 08/11/2022 | MOUNT VERNON | LINN | AMERICAN VODKAS | FIFTH GENERATION INC | -237,12 | -12 |
| 02/05/2023 | WASHINGTON | WASHINGTON | IMPORTED DISTILLED SPIRITS SPECIALTY | JOHN ERNEST DISTILLERY, INC. | -130,56 | -12 |
| 15/07/2025 | DES MOINES | POLK | TRIPLE SEC | JIM BEAM BRANDS | -42 | -12 |
| 26/09/2024 | INDIANOLA | WARREN | BOTTLED IN BOND BOURBON | HEAVEN HILL BRANDS | -166,5 | -6 |
| 27/12/2023 | BOONE | BOONE | SPICED RUM | DIAGEO AMERICAS | -170,94 | -6 |
| 08/06/2023 | MUSCATINE | MUSCATINE | AMERICAN VODKAS | SAZERAC COMPANY INC | -63,54 | -6 |