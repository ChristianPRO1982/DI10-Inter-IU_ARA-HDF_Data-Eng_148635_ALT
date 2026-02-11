# Les opérateurs

## 🎯 À quoi servent les opérateurs OLAP ?

Les opérateurs OLAP permettent **d’explorer un cube de données** :

* sans modifier les données,
* en changeant **le point de vue**,
* **le niveau de détail**,
* ou **le périmètre analysé**.

👉 Ils répondent à des questions métier du type :

> *« Par région ? Par année ? Plus détaillé ? Seulement certains produits ? »*

---

## 🧩 Les 3 grandes catégories d’opérateurs OLAP

---

## 1️⃣ Opérateurs de **changement de granularité**

👉 Ils modifient le **niveau de détail** de l’analyse.

### 🔼 Roll-up (agrégation)

* Monte dans la hiérarchie
* Résume les données

**Exemples :**

* Jour → Mois → Année
* Ville → Région → Pays

➡️ *À quoi ça sert ?*
Voir des **totaux**, des **tendances globales**, des **synthèses**.

---

### 🔽 Drill-down (détaillage)

* Descend dans la hiérarchie
* Affiche plus de détails

**Exemples :**

* Année → Mois → Jour
* Pays → Région → Ville

➡️ *À quoi ça sert ?*
**Analyser une anomalie**, comprendre *pourquoi* un chiffre est élevé ou faible.

---

## 2️⃣ Opérateurs de **sélection (filtrage du cube)**

### 🍰 Slice (projection)

* Fixe **une valeur d’une dimension**
* Réduit le cube d’une dimension

**Exemple :**

* Ventes **pour l’année 2024 uniquement**

➡️ *Résultat* :
Un sous-cube (ou un tableau) plus simple à lire.

---

### 🎲 Dice (sélection multiple)

* Filtre sur **plusieurs dimensions**
* Garde seulement certaines valeurs

**Exemple :**

* Années ∈ {2023, 2024}
* Régions ∈ {Nord, Sud}
* Produits ∈ {Chaussures, Vestes}

➡️ *Résultat* :
Un **sous-cube ciblé**, typiquement utilisé pour une analyse métier précise.

---

## 3️⃣ Opérateurs de **restructuration / visualisation**

👉 Ils ne changent pas les données, seulement **la façon de les voir**.

### 🔄 Pivot / Rotate

* Échange les axes du cube
* Lignes ↔ Colonnes

**Exemple :**

* Produits en lignes → Produits en colonnes

➡️ *Très utilisé en BI* (tableaux croisés, dashboards).

---

### 🔁 Switch

* Réordonne les membres d’une dimension

**Exemple :**

* Afficher les régions dans un autre ordre

➡️ *Purement ergonomique*.

---

### 📊 Split

* Découpe le cube en plusieurs tableaux 2D

➡️ *Pratique pour le reporting*.

---

### 🧬 Nest / Push

* Techniques avancées
* Imbriquent dimensions et mesures

➡️ *Surtout vues dans des outils OLAP dédiés (MDX, cubes MOLAP)*.

---

## 🧠 Résumé express (à mémoriser)

| Opérateur      | Sert à…                        |
| -------------- | ------------------------------ |
| **Roll-up**    | Synthétiser (moins de détail)  |
| **Drill-down** | Détailler                      |
| **Slice**      | Fixer une valeur               |
| **Dice**       | Filtrer sur plusieurs critères |
| **Pivot**      | Changer la vue                 |
| **Switch**     | Réordonner                     |
| **Split**      | Découper en tableaux           |
