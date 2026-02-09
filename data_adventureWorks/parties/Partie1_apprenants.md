# Brief : Construction d’un Data Warehouse et de Data Marts avec BigQuery

## Partie 0 — Veille : Concepts DW, OLAP et BigQuery

---

# Partie 1 — Découverte, cadrage et modélisation d’AdventureWorks DW

## Objectifs

À l’issue de cette partie, vous serez capable de :

- analyser un jeu de données décisionnel existant ;
- identifier une **table de faits** ;
- identifier les **dimensions associées** ;
- définir la **granularité** du fait principal ;
- concevoir un **modèle décisionnel** (schéma en étoile) ;
- proposer des **axes d’analyse** et des **indicateurs métier (KPI)**.

---

## Données utilisées

Vous disposez des fichiers suivants :

- **FactResellerSales**  
  <https://github.com/microsoft/sql-server-samples/blob/master/samples/databases/adventure-works/data-warehouse-install-script/FactResellerSales.csv>

- **DimProduct**  
  <https://github.com/microsoft/sql-server-samples/blob/master/samples/databases/adventure-works/data-warehouse-install-script/DimProduct.csv>

- **DimReseller**  
  <https://github.com/microsoft/sql-server-samples/blob/master/samples/databases/adventure-works/data-warehouse-install-script/DimReseller.csv>

- **DimEmployee**  
  <https://github.com/microsoft/sql-server-samples/blob/master/samples/databases/adventure-works/data-warehouse-install-script/DimEmployee.csv>

- **DimGeography**  
  <https://github.com/microsoft/sql-server-samples/blob/master/samples/databases/adventure-works/data-warehouse-install-script/DimGeography.csv>

---

## 1. Analyse de la table FactResellerSales

### 1.1 Comprendre l’événement métier
À partir du fichier `AdventureWorks_DataDescription`, décrire, en une phrase métier, à quel événement réel correspond **une ligne** de la table `FactResellerSales`.


### 1.2 Identifier mesures, clés, types de mesures (FLOW / VPU / STOCK)
À partir de `FactResellerSales` et du fichier `AdventureWorks_DataDescription`, vous devez :

- identifier les **mesures potentielles**  
  *(colonnes numériques représentant une quantité ou une valeur métier)* ;
- identifier les **clés** permettant de relier la table de faits aux **tables de dimensions** ;
- préciser, pour chaque mesure identifiée :
  - son **type** (FLOW / VPU / STOCK),
  - si elle est **additive ou non**,
  - l’**agrégation recommandée**.

#### Types de mesures (FLOW / VPU / STOCK)

- **FLOW** : un flux qui s’accumule  
  *Exemples : quantités, montants, chiffre d’affaires*
- **VPU** : une valeur par unité ou un ratio  
  *Exemples : prix unitaire, pourcentage de remise*
- **STOCK** : une valeur de référence ou un état  
  *Exemple : coût standard d’un produit*

#### Comment savoir si une mesure est additive ?

Une mesure est **additive** si la somme de ses valeurs sur plusieurs lignes de faits produit un **résultat métier cohérent**.  
Si l’agrégation par somme **n’a pas de sens métier**, alors la mesure est **non additive** et nécessite une autre forme d’agrégation (moyenne, ratio, minimum, maximum…).


### 1.3 Déterminer la granularité du fait
La **granularité du fait** correspond à la **plus petite unité d’information métier** stockée dans la table de faits.  
Elle est définie par la **combinaison des clés** reliant la table de faits aux dimensions.


## 2. Analyse des dimensions

Pour chaque table de dimension :

- identifier les informations descriptives principales (**attributs métier**) ;
- expliquer **ce que cette dimension permet d’analyser** (axes d’analyse possibles sur les faits).

À compléter :

| Dimension    | Informations clés                                                  | Analyses possibles                                                   |
| ------------ | ------------------------------------------------------------------ | -------------------------------------------------------------------- |
| DimProduct   | Nom du produit, catégorie, sous-catégorie, couleur, taille, modèle | Analyse des ventes par produit, par catégorie, par gamme de produits |
| DimReseller  |                                                                    |                                                                      |
| DimEmployee  |                                                                    |                                                                      |
| DimGeography |                                                                    |                                                                      |



## 3. Axes d’analyse

À partir des dimensions identifiées précédemment :

- lister les **axes d’analyse** ;
- préciser leurs **niveaux de granularité** (ex. : jour / mois / année).

Complétez le tableau suivant :

| Dimension        | Axe d’analyse | Niveaux de granularité possibles     |
| ---------------- | ------------- | ------------------------------------ |
| **DimProduct**   |               | Produit → Sous-catégorie → Catégorie |
| **DimReseller**  |               |                                      |
| **DimEmployee**  |               |                                      |
| **DimGeography** |               |                                      |
| **DimDate**      | Temps         |                                      |

**Remarque — Dimension Temps**

Même si la dimension Temps n’est pas listée explicitement parmi les tables de dimensions fournies, elle est **indissociable** de toute table de faits.  
Dans `FactResellerSales`, plusieurs clés temporelles sont présentes (date de commande, date d’expédition, date d’échéance).  
Cela implique que chaque fait est rattaché à un instant précis dans le temps, rendant l’analyse temporelle incontournable.



## 4. Indicateurs métier (KPI)

### 4.1 Mesures utilisables comme KPI

Parmi les mesures de la table de faits `FactResellerSales`, seules les **mesures additives de type FLOW** peuvent être utilisées comme **KPI directs**.

Les mesures suivantes doivent être retenues comme base de KPI :

- `SalesAmount`
- `OrderQuantity`
- `TotalProductCost`
- `DiscountAmount`
- `Freight`
- `TaxAmt`

Les mesures suivantes **ne doivent pas** être utilisées comme KPI directs :

- `UnitPrice`
- `UnitPriceDiscountPct`
- `ProductStandardCost`

*(elles pourront éventuellement servir à des analyses complémentaires ou à des calculs dérivés)*

---

### 4.2 Exemple de construction d’un KPI (méthode attendue)

Avant de formuler vos propres KPI, observez l’exemple suivant :

> **Mesure retenue** : `SalesAmount`  
> **Agrégation** : `SUM`  
> **Axe d’analyse** : Temps  
>
> **KPI formulé** :  
> **Chiffre d’affaires par période = SUM(SalesAmount) par jour / mois / année**

Méthode : **mesure additive → agrégation → axe d’analyse → KPI**

---

### 4.3 Formuler d’autres KPI

En appliquant la même méthode aux autres mesures identifiées à l’étape 4.1, formulez d’autres (2 ou 3) KPI pertinents.

> **Rappel :**  
> Un KPI n’est pas une mesure au hasard ;  
> c’est une **mesure additive**, **correctement agrégée** et **contextualisée** par un axe d’analyse.

## 5. Modélisation décisionnelle
- Proposer un **schéma en étoile**


---

## Livrables — Partie 1
- description de la granularité du fait ;
- tableau d’analyse des dimensions complété ;
- liste argumentée des axes d’analyse ;
- liste des KPI proposés ;
- schéma décisionnel cible.
