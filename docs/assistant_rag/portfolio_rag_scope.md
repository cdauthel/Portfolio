# Périmètre RAG du portfolio

Le RAG de l'application indexe automatiquement plusieurs familles de connaissances.

## Navigation de l'application

Chaque section et sous-page est indexée:

- Tableau de bord;
- Scraping et API;
- Business Intelligence;
- Analyse exploratoire;
- Analyse client;
- Analyse spatiale;
- Analyse temporelle;
- Modélisations spatiales, temporelles, physiques, Machine Learning et Deep Learning;
- Assistant IA;
- Architecture Cloud;
- Ops et Reproductibilité.

## Datasets

Chaque table disponible en mémoire est résumée:

- nombre de lignes et colonnes;
- colonnes principales;
- types de données;
- variables quantitatives;
- variables temporelles;
- valeurs manquantes principales.

Cette indexation permet à l'assistant de répondre à des questions comme:

- Quelle table utiliser pour analyser la satisfaction client ?
- Quelles variables intégrer dans un modèle de forecasting ?
- Quels jeux de données contiennent des coordonnées géographiques ?

## Documents projet

Les fichiers suivants sont indexés lorsqu'ils existent:

- `README.md`;
- `README_RECRUTEUR.md`;
- `requirements.txt`;
- `pyproject.toml`;
- fichiers markdown et texte placés dans `docs/assistant_rag/`.

Les documents RAG ajoutés dans `docs/assistant_rag/` couvrent notamment:

- l'identité de Cyriack Dauthel comme candidat et auteur du portfolio;
- le rôle du chatbot comme assistant documentaire;
- l'audience principale: recruteurs, testeurs, managers data et évaluateurs techniques;
- la carte des entités: candidat, app Streamlit, données, modèles, RAG, LLM, GitHub et Streamlit Cloud;
- les parcours de lecture selon les profils: recruteur, data analyst, data scientist, data engineer;
- les limites à respecter: ne pas inventer d'informations personnelles, ne pas exposer de secrets, ne pas confondre simulation et données réelles.
- les processus internes: simulation, catalogue, qualité, collecte API/scraping, description automatique, modélisation et assistant IA;
- des extraits ciblés du code de `app/main.py`, notamment les fonctions liées au RAG, aux données, au scraping, aux modèles et au routage Streamlit.

## Limites

Le RAG ne modifie pas les données et ne réentraîne pas un modèle. Il récupère les passages les plus proches de la question, puis les transmet au LLM ou au mode extractif local.

Si une information n'est pas dans l'index, l'assistant doit le signaler.
