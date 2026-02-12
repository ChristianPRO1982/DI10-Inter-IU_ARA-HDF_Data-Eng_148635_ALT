# PARTIE 3 - 1-Création

## 🧭 Étape 1 — Problème stratégique avant de commencer

```sql
CREATE OR REPLACE TABLE `adventureworks-dw-christian.staging.stg_dim_date` AS
WITH date_range AS (
  SELECT
    date_day
  FROM UNNEST(GENERATE_DATE_ARRAY('2010-01-01', '2014-12-31')) AS date_day
)

SELECT
  FORMAT_DATE('%Y%m%d', date_day) AS DateKey,
  date_day AS FullDateAlternateKey,
  EXTRACT(DAYOFWEEK FROM date_day) AS DayNumberOfWeek,
  FORMAT_DATE('%A', date_day) AS EnglishDayNameOfWeek,
  EXTRACT(DAY FROM date_day) AS DayNumberOfMonth,
  EXTRACT(MONTH FROM date_day) AS MonthNumberOfYear,
  FORMAT_DATE('%B', date_day) AS EnglishMonthName,
  EXTRACT(QUARTER FROM date_day) AS CalendarQuarter,
  EXTRACT(YEAR FROM date_day) AS CalendarYear,
  EXTRACT(QUARTER FROM date_day) AS FiscalQuarter,
  EXTRACT(YEAR FROM date_day) AS FiscalYear,

  CURRENT_TIMESTAMP() AS _ingested_at,
  'generated_sql' AS _source_file

FROM date_range;
```

**vérification**
```sql
SELECT COUNT(*) FROM `adventureworks-dw-christian.staging.stg_dim_date`;
```

**résultats**

| line | COUNT(0) |
|------|-------------|
|    1 |        1826 |















> création `stg_dim_date` en staging

---
---
---
---
---

> [SUITE DU RENDU ICI](https://github.com/ChristianPRO1982/DI10-Inter-IU_ARA-HDF_Data-Eng_148635_ALT/blob/main/RENDU%20DU%20BRIEF/PARTIE%203%20-%202-R%C3%A9ponses%20aux%20questions.md)