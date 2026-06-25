# Guide de lecture pour recruteur ou testeur

## Objectif du guide

Ce document aide l'assistant IA à guider un recruteur dans le portfolio. Il doit permettre de répondre rapidement à des questions comme:

- "Que dois-je regarder en priorité ?";
- "Quelles compétences sont démontrées ?";
- "Cette application est-elle seulement un dashboard ?";
- "Comment vérifier la partie data engineering ?";
- "Comment lire les modèles ?";

## Lecture rapide en 10 minutes

1. **Accueil et profil** pour comprendre le contexte général.
2. **Données -> Dictionnaire de données** pour voir la structuration des tables.
3. **Scraping et API -> Sources API** pour voir la collecte externe.
4. **Dashboard et analyses -> Business Intelligence** pour voir la restitution.
5. **Analyse client** pour lire les cas métier orientés décision.
6. **Modélisations -> Machine Learning** pour vérifier les méthodes prédictives.
7. **Ops et Reproductibilité** pour voir la logique d'industrialisation.
8. **Assistant IA** pour interroger le projet en langage naturel.

## Lecture technique en 30 minutes

### Axe data analyst

- Analyse exploratoire.
- Business Intelligence.
- Analyse client.
- Satisfaction client.
- CLV et rentabilité.
- Valeur et pilotage client.

À vérifier: qualité des visualisations, choix des filtres, cohérence des métriques, lisibilité des conclusions.

### Axe data scientist

- Gestion des valeurs manquantes.
- Classification et régression.
- Apprentissage non supervisé.
- Analyse temporelle.
- Analyse spatiale.
- Géostatistique.

À vérifier: formulation du problème, métriques, validation, diagnostic, interprétation, limites.

### Axe data engineer

- Scraping et API.
- Catalogue de données.
- Validation des APIs.
- Validation du Scraping.
- Architecture.
- Documentation Technique.
- Projet DBT.
- Pipeline Prefect.

À vérifier: traçabilité, structuration, schémas, contrôle qualité, reproductibilité, séparation raw/clean/marts.

## Ce que le portfolio cherche à prouver

Le portfolio cherche à montrer:

- une vision complète du cycle de vie de la donnée;
- une capacité à relier métier, données et modèles;
- une attention à la qualité et à la documentation;
- une capacité à construire une interface Streamlit dense mais navigable;
- une capacité à intégrer APIs, scraping, BI, ML, spatial, temporel et ops;
- une capacité à expliquer les choix plutôt que seulement afficher des résultats.

## Comment répondre à "pourquoi cette app est intéressante ?"

Réponse recommandée:

"Cette application est intéressante parce qu'elle ne se limite pas à un dashboard. Elle relie collecte, catalogue, qualité, exploration, analyses métier, modèles, architecture et assistant IA. Elle montre donc une compréhension transversale du travail data, depuis la source jusqu'à l'interprétation et la mise en partage."

## Comment répondre à "que dois-je évaluer ?"

Réponse recommandée:

"Vous pouvez évaluer trois dimensions: la rigueur data, avec le dictionnaire, la qualité et les validations; la valeur analytique, avec les dashboards, analyses client, spatiales et temporelles; et la capacité de modélisation, avec les modules ML, statistiques, temporels et spatiaux. La partie Ops montre enfin la logique de reproductibilité."

## Comment répondre à "est-ce prêt pour production ?"

Réponse recommandée:

"Le portfolio est d'abord une démonstration interactive. Certaines parties sont prêtes comme prototypes analytiques, d'autres sont explicitement indiquées comme en construction. Pour une production complète, il faudrait connecter les sources réelles, sécuriser les secrets, stabiliser les pipelines, ajouter monitoring, tests automatisés et hébergement robuste."
