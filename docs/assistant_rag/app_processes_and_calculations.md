# Processus, calculs et logique interne de l'application

## Chaîne générale

L'application suit une logique de pipeline analytique:

```text
Simulation ou collecte
  -> Typage et catalogue
  -> Qualité et valeurs manquantes
  -> Description et exploration
  -> Analyses métier
  -> Modélisations
  -> Interprétation et restitution
  -> Assistant IA / RAG
```

## Simulation des données

Les données simulées servent à créer un environnement stable, reproductible et démonstratif. Elles permettent de montrer des cas métier sans exposer de données confidentielles.

Les paramètres de simulation contrôlent notamment:

- nombre d'observations;
- variables quantitatives;
- variables qualitatives;
- dates et dimensions temporelles;
- valeurs manquantes;
- bruit, segments et scénarios métier.

Le module de qualité documente ces paramètres afin que l'utilisateur comprenne d'où viennent les tables utilisées.

## Catalogue et dictionnaire

Le catalogue documente les tables disponibles. Le dictionnaire donne le détail des champs: nom, type, rôle possible, présence de valeurs manquantes et contexte d'utilisation.

Le RAG utilise ces informations pour répondre à des questions comme:

- quelle table choisir pour un modèle client ?
- quelle variable peut servir de cible ?
- quelles colonnes sont temporelles ou spatiales ?
- quelles données viennent de l'API ou du scraping ?

## Gestion des valeurs manquantes

Le module distingue la nature des variables:

- quantitatives;
- qualitatives;
- temporelles;
- spatiales;
- spatio-temporelles.

Les méthodes disponibles sont comparées selon un backtest ou une logique de reconstruction. Les tests MCAR/MAR indicatifs ne prouvent pas définitivement le mécanisme de manque: ils détectent seulement si l'indicatrice "manquant / observé" semble associée à d'autres variables.

## Scraping et API

La collecte externe est séparée en deux logiques:

- **API**: endpoint documenté, paramètres explicites, réponse structurée JSON/CSV;
- **Scraping Web**: extraction HTML à partir de sélecteurs CSS/XPath, normalisation, tests et documentation.

Les données collectées alimentent ensuite:

- Catalogue de données;
- Validation des APIs ou du scraping;
- Description des données;
- RAG;
- futures jointures vers les modèles.

## Description automatique des données

Le système de description cherche à comprendre automatiquement la table sélectionnée:

- variables numériques;
- variables catégorielles;
- variables temporelles;
- coordonnées spatiales;
- dimensions métier;
- pertinence des graphiques.

L'objectif est d'afficher les représentations adaptées plutôt que de demander à l'utilisateur de choisir manuellement chaque graphique.

## Modélisation

Les modèles sont organisés par famille:

- Machine Learning supervisé: classification et régression;
- Machine Learning non supervisé: clustering, projections, mélanges;
- séries temporelles: univarié, bivarié, multivarié;
- spatial: voisinage, autocorrélation, modèles SAR/SEM/SDM, géostatistique;
- Deep Learning;
- physiques, en construction.

Le RAG doit toujours relier un modèle à:

- la cible;
- les variables explicatives;
- le type de données;
- les métriques;
- les hypothèses;
- les limites;
- l'usage métier possible.

## Assistant IA

Le module Assistant IA construit un contexte documentaire à partir:

- des pages de navigation;
- des tables en mémoire;
- de la documentation RAG;
- de certains extraits ciblés du code de l'application;
- du manifeste des modèles LLM;
- des fichiers projet.

Le mode `LLM seul` envoie seulement la question au modèle. Le mode `LLM + RAG` récupère des passages pertinents, les injecte dans le prompt, puis demande au modèle de répondre à partir de ce contexte.
