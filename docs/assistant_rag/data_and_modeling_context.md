# Données, modèles et logique analytique

## Logique générale

Le portfolio relie les données aux modèles par une chaîne lisible:

```text
Données brutes
  -> Documentation et qualité
  -> Variables exploitables
  -> Visualisations
  -> Modèles
  -> Interprétation métier
  -> Restitution recruteur
```

## Types de données

### Données originales ou simulées

Ces tables structurent les cas métier internes du portfolio: clients, commandes, magasins, support, campagnes, produits, événements, satisfaction, temporalité et variables associées.

Elles permettent de démontrer des raisonnements analytiques complets sans exposer de données confidentielles.

### Données API

Les données API proviennent de connecteurs documentés. Elles peuvent représenter des informations météo, économiques, géographiques, financières, publiques, scientifiques ou sociales.

Elles démontrent la capacité à:

- identifier une source;
- documenter un endpoint;
- gérer des paramètres;
- contrôler une réponse;
- normaliser une table;
- l'intégrer au catalogue.

### Données scraping

Les données scraping proviennent de pages HTML publiques. Elles sont utiles quand une information structurée existe en ligne mais n'est pas exposée sous forme d'API simple.

Le scraping doit rester documenté, contrôlé et respectueux des conditions d'utilisation.

## Familles de modèles

### Modèles statistiques et Machine Learning

Ils servent à expliquer, prédire ou classer: régression, classification, clustering, arbres, ensembles, SVM, KNN, méthodes bayésiennes, modèles de mélange, etc.

Leur lecture doit inclure:

- variable cible;
- variables explicatives;
- métriques;
- diagnostic;
- limites;
- interprétation métier.

### Modèles Deep Learning

Ils servent à montrer des architectures plus flexibles pour classification, régression, séquences ou représentations. Ils doivent être présentés avec prudence lorsque les données sont simulées.

### Modèles spatiaux

Ils relient les observations à leur voisinage: matrice spatiale W, Moran, LISA, SAR, SEM, SLX, SDM, géostatistique, interpolation et krigeage.

Le point important est la dépendance spatiale: deux zones proches peuvent partager une structure commune.

### Modèles temporels

Ils analysent tendance, saisonnalité, autocorrélation, prévision univariée, bivariée ou multivariée.

Le point important est l'ordre temporel: les observations ne sont pas indépendantes si elles appartiennent à une série.

### Modèles physiques

Ils correspondent aux futures simulations de systèmes: équations différentielles, flux, compartiments, dynamiques simples ou multiples.

Si la page est en construction, l'assistant doit le signaler.

## Comment expliquer un modèle à un recruteur

L'assistant doit éviter de décrire seulement l'algorithme. Il doit relier:

- le besoin métier;
- la donnée disponible;
- la méthode choisie;
- les métriques;
- l'interprétation;
- les limites.

Exemple de formulation:

"Ce modèle illustre comment transformer une table client en outil d'aide à la décision. La cible est expliquée par des variables comportementales, transactionnelles et contextuelles. Les métriques évaluent la performance, mais l'intérêt portfolio est aussi de montrer la construction du pipeline, le diagnostic et la lecture métier."

## Questions fréquentes

### Pourquoi utiliser des données simulées ?

Pour démontrer une méthode complète sans dépendre de données confidentielles. Les données simulées permettent de contrôler les cas métier, les distributions, les valeurs manquantes, les segments et les scénarios.

### Peut-on brancher de vraies données ?

Oui. L'architecture prévoit des connecteurs API, du scraping web, un catalogue, une documentation technique et des contrôles qualité. Les vraies données peuvent remplacer ou compléter les tables simulées si elles respectent le schéma attendu.

### Le RAG entraîne-t-il les modèles ?

Non. Le RAG recherche du contexte documentaire. Il ne modifie ni les modèles ML, ni le LLM. Il améliore la pertinence de la réponse en fournissant les bons passages au moment de la question.
