# Cryptobot 🚀

## 📌 Présentation
Cryptobot est un projet de **data engineering** autour des marchés de cryptomonnaies.  
Il couvre l’ensemble d’un pipeline data : **collecte via API, transformation, stockage SQL & NoSQL, et analyse**.

Le projet est développé dans un objectif pédagogique (formation DataScientest) tout en respectant des **bonnes pratiques professionnelles**.

---

## 🏗️ Architecture du projet
cryptobot/
├── scripts/ # Scripts Python (fetch, transform, load, ML)
│ ├── fetch/
│ ├── transform/
│ ├── load/
│ └── ml/
│
├── sql/ # Scripts SQL (PostgreSQL)
│ ├── 01_schema_cryptobot.sql
│ ├── 02_seed_cryptobot.sql
│ └── 02_seed_cryptobot_enriched.sql
│
├── NoSQL/
│ └── mongo/ # Requêtes MongoDB (MQL)
│ ├── find_queries.js
│ ├── aggregation_step4_stats.js
│ ├── aggregation_step5_top_volume.js
│ └── aggregation_step6_daily_agg.js
│
├── docker-compose.yml
└── .gitignore

---

## 🔄 Pipeline de données

### 1️⃣ Collecte
- Récupération des données via **API publiques** :
  - Binance (OHLCV)
  - CoinGecko (données macro)
- Scripts Python dans `scripts/fetch/`

### 2️⃣ Transformation
- Nettoyage et normalisation des données
- Conversion **JSON → CSV**
- Scripts dans `scripts/transform/`

### 3️⃣ Stockage
- **MongoDB / MongoDB Atlas (NoSQL)**  
  - Stockage flexible des données OHLCV
  - Requêtes MQL : find, projection, aggregation pipeline
- **PostgreSQL (SQL)**  
  - Stockage structuré
  - Modélisation relationnelle
  - Requêtes analytiques

### 4️⃣ Analyse
- Agrégations MongoDB (stats, top volumes, agrégation journalière)
- Requêtes SQL analytiques
- Préparation des datasets pour exploitation future (ML)

---

## 🗄️ Bases de données

### 🔹 MongoDB / MongoDB Atlas
Utilisé pour :
- Données brutes et semi-structurées
- Requêtes MQL :
  - filtres simples (`find`)
  - projections
  - agrégations (`$group`, `$sort`, `$limit`)

Scripts disponibles dans : NoSQL/mongo/

---

### 🔹 PostgreSQL
Utilisé pour :
- Données structurées
- Modélisation analytique
- Calculs statistiques et jointures

Scripts disponibles dans : sql/

---

## 🐳 Docker
Le fichier `docker-compose.yml` permet de déployer rapidement :
- PostgreSQL
- MongoDB

---

## 🛠️ Technologies utilisées
- Python
- MongoDB & MongoDB Atlas
- PostgreSQL
- Docker / Docker Compose
- Git & GitHub

---

## 🚀 Évolutions possibles
- Streaming temps réel (Kafka / Spark)
- Automatisation du pipeline
- Enrichissement des données
- Modélisation prédictive

---

## 👤 Auteur
Projet réalisé par **Med Amine Mrizki**  
dans le cadre de la formation **DataScientest**.
