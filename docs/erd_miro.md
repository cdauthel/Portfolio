# Page Schémas ERD - Intégration Miro (backend) + fallback local

## Objectif
La page `Schémas ERD` permet de:
- sélectionner une base DuckDB,
- introspecter automatiquement son schéma relationnel,
- générer un ERD,
- synchroniser le diagramme vers Miro en arrière-plan (optionnel),
- afficher le schéma directement dans l'application (embed Miro si disponible, sinon rendu local).

## Variables d'environnement
- `MIRO_ACCESS_TOKEN`: token d'accès Miro (requis pour synchroniser).
- `MIRO_API_BASE_URL` (optionnel): URL API Miro (défaut: `https://api.miro.com/v2`).
- `MIRO_CLIENT_ID` (optionnel): client OAuth Miro.
- `MIRO_CLIENT_SECRET` (optionnel): secret OAuth Miro.
- `MIRO_REDIRECT_URI` (optionnel): URL callback OAuth.

Important:
- Les secrets restent côté serveur Python.
- Ne jamais exposer ces variables dans le front.

## Flux de fonctionnement
1. L'utilisateur ouvre `Données > Schémas ERD`.
2. L'utilisateur choisit:
   - connexion/environnement (`DuckDB local`),
   - base (`*.duckdb` détectées),
   - schéma logique.
3. L'app introspecte la base et construit le modèle ERD.
4. Si Miro est configuré et que l'utilisateur clique `Mettre à jour le diagramme`, l'app:
   - crée/récupère un board,
   - efface les éléments ERD gérés par l'app,
   - recrée tables + relations,
   - calcule une URL embed.
5. L'app affiche:
   - la vue Miro embarquée (si disponible), sinon
   - le fallback local Plotly.

## Fichiers principaux
- `src/portfolio_app/erd.py`
  - introspection DB,
  - typage du schéma,
  - génération du modèle ERD,
  - layout automatique.
- `src/portfolio_app/miro.py`
  - service backend Miro,
  - création/récupération board,
  - synchronisation d'objets,
  - statut board,
  - URL embed.
- `app/main.py`
  - UI complète de la page `Schémas ERD`.

## Stratégie multi-bases
- Clé de board: `user_id + workspace + database:schema`.
- Mapping persisté dans `data/metadata/miro_boards.json`.
- Changement de base/schéma => nouveau contexte de génération, sans mélange visuel.

## Limites connues
- L'API Miro peut varier selon le plan (permissions, endpoints connecteurs).
- Sur très grands schémas, le fallback local reste lisible mais peut devenir dense.
- Les contraintes FK absentes côté DB sont inférées heuristiquement.

## Fallback local
Si Miro n'est pas configuré ou indisponible:
- la page ne casse pas,
- le diagramme reste visualisable via le rendu local,
- l'analyse et l'export JSON du schéma restent disponibles.
