# Mise en contexte des données et modèles

## Données internes

Les données internes simulent un environnement commercial et analytique. Elles peuvent couvrir:

- clients;
- commandes;
- magasins;
- produits;
- campagnes marketing;
- tickets support;
- satisfaction;
- événements temporels;
- géographie des points de vente ou zones;
- variables de contexte.

Ces tables permettent de construire des analyses de panier, rentabilité, segmentation, churn, satisfaction, forecasting, spatialisation et modélisation prédictive.

## Données collectées

Les données collectées via API ou scraping apportent du contexte externe:

- météo;
- économie;
- démographie;
- géographie;
- mobilité;
- finance;
- santé;
- science;
- open data.

Elles peuvent être utilisées comme variables explicatives après jointure par:

- date;
- zone géographique;
- identifiant métier;
- coordonnées latitude / longitude;
- catégorie ou segment.

## Variables métier typiques

### Client

Variables utiles:

- ancienneté;
- fréquence d'achat;
- panier moyen;
- segment;
- satisfaction;
- retour produit;
- tickets support;
- CLV;
- churn.

Usages:

- segmentation;
- scoring;
- recommandation d'action;
- priorisation commerciale.

### Vente et rentabilité

Variables utiles:

- chiffre d'affaires;
- marge;
- volume;
- canal;
- promotion;
- produit;
- magasin;
- période.

Usages:

- analyse BI;
- forecasting;
- optimisation commerciale;
- détection d'anomalies.

### Spatial

Variables utiles:

- latitude;
- longitude;
- distance;
- voisinage;
- densité;
- concurrence;
- accessibilité;
- variables interpolées.

Usages:

- couverture;
- cannibalisation;
- autocorrélation spatiale;
- géostatistique;
- enrichissement de features.

### Temporel

Variables utiles:

- date;
- semaine;
- mois;
- saison;
- retard;
- lag;
- rolling mean;
- tendance.

Usages:

- prévision;
- saisonnalité;
- diagnostic de rupture;
- suivi opérationnel.

## Comment le RAG doit interpréter les modèles

Quand une question concerne un modèle, le RAG doit aider le LLM à répondre selon cette structure:

1. **Objectif**: prédire, expliquer, segmenter, détecter ou simuler.
2. **Données**: tables et variables utilisées.
3. **Méthode**: famille de modèle et hypothèses.
4. **Métriques**: performance et diagnostic.
5. **Lecture métier**: ce que le résultat signifie.
6. **Limites**: simulation, biais possible, taille d'échantillon, hypothèses.
7. **Suite**: enrichissement, test, validation ou mise en production.

## Point de prudence

Les résultats du portfolio sont faits pour démontrer une démarche. Ils ne doivent pas être présentés comme une décision opérationnelle réelle sans validation sur données réelles, contrôle métier et monitoring.
