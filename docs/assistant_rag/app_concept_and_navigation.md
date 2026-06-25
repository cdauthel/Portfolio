# Concept de l'application et navigation

## Définition de l'application

L'application est un portfolio data interactif construit avec Streamlit. Elle regroupe des modules de données, d'analyse, de modélisation, de scraping/API, d'architecture cloud, d'ops et d'assistance IA.

Elle doit être lue comme une démonstration structurée d'un environnement analytique complet:

```text
Sources de données
  -> Qualité et documentation
  -> Exploration et visualisation
  -> Modèles analytiques
  -> Interprétation métier
  -> Architecture et reproductibilité
  -> Assistant IA documentaire
```

## Grands espaces de navigation

### Accueil et profil

Présente le point d'entrée du portfolio, le contexte, la posture et les grandes familles de compétences.

### Données

Regroupe les données de référence du portfolio: tableau de bord des données, dictionnaire, schémas ERD, qualité, valeurs manquantes et documentation des champs.

Cette partie sert à prouver que l'analyse ne part pas d'un simple graphique, mais d'une base de données comprise, typée et contrôlée.

### Scraping et API

Montre la capacité à collecter des données externes via APIs et scraping web. Cette section distingue:

- les APIs documentées, reproductibles et paramétrables;
- le scraping HTML, utilisé lorsque la donnée n'est pas exposée via une API exploitable.

Les tables collectées peuvent ensuite alimenter le catalogue, la description des données, les modèles et le RAG.

### Dashboard et analyses

Regroupe la Business Intelligence, l'analyse exploratoire, l'analyse client, l'analyse spatiale et l'analyse temporelle.

Cette partie explique les données par les visualisations, les segments, les cartes, les séries temporelles et les diagnostics.

### Modélisations

Regroupe les modèles spatiaux, temporels, physiques, Machine Learning et Deep Learning.

Cette partie montre la capacité à passer d'une analyse descriptive à une logique prédictive, explicative ou simulatoire.

### Assistant IA

Fournit un chatbot et un RAG pour interroger le portfolio. L'assistant ne remplace pas les pages métier: il aide à les comprendre, à les relier et à trouver les bons modules.

### Architecture Cloud

Présente l'organisation cible ou fictive des flux: sources, ingestion, dbt, warehouse/lake, data visualization, orchestration et notebooks.

### Ops et Reproductibilité

Documente la structure de l'application, les dépendances, les pipelines, MLflow, Prefect, exports et CI/CD.

## Chemins de lecture utiles

### Pour un recruteur pressé

1. Accueil et profil.
2. Données -> Dictionnaire de données.
3. Dashboard et analyses -> Business Intelligence.
4. Modélisations -> Machine Learning.
5. Scraping et API -> Sources API.
6. Ops et Reproductibilité -> Architecture de l'app.

### Pour un évaluateur data scientist

1. Qualité des données.
2. Analyse exploratoire.
3. Modélisations Machine Learning.
4. Modélisations spatiales ou temporelles.
5. Gestion des valeurs manquantes.
6. Comparaison des métriques et diagnostics.

### Pour un évaluateur data engineer

1. Scraping et API.
2. Catalogue de données.
3. Architecture.
4. Documentation Technique.
5. Projet DBT.
6. Ops et Reproductibilité.

## Règle de réponse pour l'assistant

Quand une question concerne une page précise, l'assistant doit:

1. identifier la section de navigation;
2. expliquer le rôle de la page;
3. citer les objets concernés: tables, graphiques, modèles, métriques;
4. proposer le chemin de navigation le plus court;
5. préciser les limites si la page est en construction.
