# Connecteurs LLM locaux

## Ollama

### Ollama local

Endpoint local natif par défaut:

```text
http://localhost:11434/api
```

Chat:

```text
http://localhost:11434/api/chat
```

OpenAI-compatible:

```text
http://localhost:11434/v1/chat/completions
```

Liste des modèles locaux:

```text
GET http://localhost:11434/api/tags
```

Aucune authentification n'est requise en local. L'API cloud `https://ollama.com/api` nécessite une clé API avec header `Authorization: Bearer ...`.

Dans l'application portfolio, Ollama peut être lancé directement depuis la page `Assistant IA -> Chatbot et RAG`.

Lorsque l'application lance Ollama, elle définit:

```text
OLLAMA_MODELS=models/llm/ollama
```

Ainsi, les modèles téléchargés via le bouton de l'application sont stockés dans le dossier du projet local, mais ce dossier est ignoré par Git.

Modèles utiles pour le portfolio:

- `llama3.2`: assistant général léger;
- `mistral`: réponses générales sobres;
- `qwen3:8b`: raisonnement et code;
- `qwen3-coder`: code et debug;
- `gpt-oss:20b`: généraliste plus lourd;
- `gemma3`: assistant compact.

### Ollama Cloud

Endpoint cloud natif:

```text
https://ollama.com/api/chat
```

Endpoint cloud compatible OpenAI lorsque disponible:

```text
https://ollama.com/v1/chat/completions
```

Contrairement à l'endpoint local, l'endpoint cloud nécessite une clé API. Cette clé doit être placée dans `st.secrets` sur Streamlit Cloud ou dans `secrets/assistant_ia.local.txt` en local.

Ollama local fonctionne sans clé parce que le serveur écoute sur la machine de l'utilisateur. Ollama Cloud fonctionne avec authentification parce que le calcul se fait sur l'infrastructure distante.

Dans le contexte de cette application, `gpt-oss:120b` est conseillé avec Ollama Cloud lorsqu'il est disponible. C'est l'un des meilleurs compromis pour un usage recruteur entre:

- vitesse d'exécution perçue;
- temps de calcul de la requête;
- temps d'affichage du résultat;
- qualité de la réponse;
- capacité à exploiter correctement le contexte RAG.

`gpt-oss:20b` peut rester utile pour des tests plus légers ou moins coûteux, mais la qualité de synthèse et de raisonnement attendue pour expliquer un portfolio dense est généralement meilleure avec `gpt-oss:120b`.

## Jan.ai

Jan Desktop peut exposer un serveur local OpenAI-compatible, souvent sur:

```text
http://127.0.0.1:1337/v1/chat/completions
```

Les modèles dépendent de ceux téléchargés dans Jan. Exemples utiles:

- Jan-v3-4B;
- Jan-Code-4B;
- Jan-v1;
- Jan-Nano-128k;
- Lucy.

L'application peut tenter d'ouvrir Jan Desktop sur macOS. Le téléchargement des modèles reste géré par le Hub Jan, car Jan contrôle son propre stockage de modèles.

Jan.ai est pertinent pour une démonstration locale privée. Pour une application Streamlit Cloud consultée par des recruteurs, Jan Desktop ne peut pas être lancé par le conteneur Streamlit. Il faut alors utiliser un endpoint cloud, un proxy compatible OpenAI ou un serveur Jan auto-hébergé et exposé de façon sécurisée.

## LM Studio

LM Studio expose un serveur local OpenAI-compatible, souvent sur:

```text
http://localhost:1234/v1/chat/completions
```

La liste des modèles exposés dépend du modèle chargé dans l'interface. L'endpoint `/v1/models` peut être utilisé pour découvrir les modèles disponibles.

L'application peut tenter de lancer `lms server start --port 1234` si la CLI `lms` est installée. Sinon, elle peut ouvrir LM Studio sur macOS. Le téléchargement et la sélection du modèle restent gérés par l'interface LM Studio.

LM Studio est pertinent pour tester localement des modèles. Pour un QR code public Streamlit Cloud, le serveur LM Studio local de la machine de Cyriack n'est pas accessible par les recruteurs. Il faut donc passer par un endpoint distant ou un proxy sécurisé.

## Endpoint compatible

Un proxy OpenAI-compatible peut être utilisé pour cacher les clés et appliquer quotas, logs, règles de sécurité et filtrage.

En production recruteur, cette option est préférable à une clé exposée dans une application frontale ou dans un fichier ChatMD public.

## Partage de l'application

Pour un QR code public, il est préférable d'héberger l'app avec un endpoint cloud/proxy sécurisé. Dans ce cas, les recruteurs n'ont rien à télécharger.

Si le recruteur clone le repo et exécute l'app localement, il devra disposer d'un runtime local ou utiliser un endpoint cloud. Les poids LLM ne doivent pas être inclus dans Git car ils sont volumineux, spécifiques aux runtimes et parfois soumis à des licences propres.
