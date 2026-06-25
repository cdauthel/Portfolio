# Assistant IA - Streamlit Cloud, GitHub et runtimes LLM

## Principe

En local, l'application peut piloter un runtime installé sur la machine: Ollama, Jan.ai ou LM Studio. Elle peut aussi stocker les modèles Ollama dans `models/llm/ollama` pour éviter de polluer le dossier système.

Sur Streamlit Community Cloud, l'application tourne dans un conteneur Linux distant. Elle ne peut pas ouvrir une application desktop locale comme Jan.ai ou LM Studio, ni garantir l'installation et le maintien de modèles LLM de plusieurs gigaoctets dans le dépôt GitHub.

Il faut donc distinguer deux familles de connexions:

- **connexion locale**: l'app appelle un serveur présent sur la même machine, par exemple `http://localhost:11434` pour Ollama;
- **connexion hébergée**: l'app appelle un service distant ou un proxy HTTPS, par exemple Ollama Cloud, OpenAI-compatible, OpenRouter, serveur VPS ou backend privé.

La bonne architecture pour une application publique est donc:

```text
Recruteur
  -> Streamlit Cloud
  -> st.secrets
  -> endpoint LLM distant ou proxy sécurisé
  -> RAG construit par l'application
  -> réponse chatbot
```

## Ce qui doit être versionné

- Code Streamlit.
- Fichiers de configuration non sensibles.
- Manifeste des modèles recommandés.
- Documentation RAG et périmètre des données indexées.
- Scripts de setup local.

## Ce qui ne doit pas être versionné

- Clés API.
- Mots de passe.
- Fichiers `secrets.toml`.
- Modèles LLM téléchargés.
- Dossiers `models/`, `secrets/`, `.streamlit/secrets.toml`.

## Configuration Streamlit Cloud

Dans Streamlit Cloud, ouvrir les paramètres de l'application, puis renseigner les secrets au format TOML.

### Option recommandée: endpoint compatible OpenAI

```toml
[assistant_ia]
provider = "Endpoint compatible"
base_url = "https://votre-proxy-ou-fournisseur.example.com/v1/chat/completions"
model = "modele-disponible"
api_key = "COLLER_LA_CLE_DANS_STREAMLIT_SECRETS_UNIQUEMENT"
timeout = 40
temperature = 0.2
```

### Option Ollama Cloud

```toml
[assistant_ia]
provider = "Ollama Cloud"
base_url = "https://ollama.com/api/chat"
model = "modele-cloud-disponible"
api_key = "COLLER_LA_CLE_DANS_STREAMLIT_SECRETS_UNIQUEMENT"
timeout = 40
temperature = 0.2
```

### Option serveur Ollama auto-heberge

```toml
[assistant_ia]
provider = "Ollama"
base_url = "https://votre-serveur-ollama.example.com/api/chat"
model = "llama3.2"
api_key = "CLE_DU_PROXY_SI_PRESENTE"
timeout = 40
temperature = 0.2
```

Dans ce cas, Ollama tourne sur un serveur séparé, par exemple VPS, GPU cloud, machine personnelle exposée via tunnel sécurisé ou reverse proxy HTTPS. Le serveur doit appliquer une authentification, des quotas et des logs.

## Pourquoi `llama3.2` peut marcher sans clé

`llama3.2` fonctionne sans clé lorsque l'app appelle l'endpoint local `http://localhost:11434/api/chat`. Dans ce cas, Ollama tourne sur la même machine que l'application et n'exige pas d'authentification locale.

Les autres fournisseurs peuvent échouer pour des raisons différentes:

- Jan.ai exige que Jan Desktop soit installé, qu'un modèle soit téléchargé, que le serveur local soit démarré et qu'une clé locale soit configurée dans Jan;
- LM Studio exige que l'application soit installée, qu'un modèle soit chargé et que le serveur local soit démarré;
- Ollama Cloud exige une clé API;
- un endpoint compatible exige l'URL exacte, le modèle exposé et souvent une clé API.

## Impact pour les recruteurs

Si l'application hébergée utilise un endpoint distant, le recruteur n'a rien à installer. Il scanne le QR code, ouvre l'application et interroge le chatbot.

Si le recruteur clone le dépôt et lance l'application localement, il doit soit installer un runtime local et télécharger un modèle, soit renseigner un endpoint cloud dans `secrets/assistant_ia.local.txt` ou `.streamlit/secrets.toml`.

## RAG de l'application

Le RAG ne ré-entraine pas le LLM. Il construit un contexte documentaire à partir:

- de la navigation de l'application;
- des profils de tables et jeux de données disponibles;
- des fichiers `README`, `requirements.txt`, `pyproject.toml`;
- des documents dans `docs/assistant_rag/`;
- du manifeste des modèles IA;
- des règles de connexion et de déploiement.

La question utilisateur est comparée aux segments indexés, les passages les plus pertinents sont injectés dans le prompt, puis le LLM répond à partir de ce contexte.

## ChatMD

ChatMD peut appeler un LLM via `!useLLM` et enrichir une réponse avec du RAG via `!RAG`. Dans l'application, l'export ChatMD sert à produire un scénario compatible avec:

- endpoint local Ollama, Jan.ai ou LM Studio;
- endpoint distant compatible OpenAI;
- base de connaissances textuelle exposée par URL ou intégrée au projet.

Pour une version publique, éviter d'exposer une clé dans un fichier ChatMD public. Préférer un proxy serveur qui garde la clé côté backend.
