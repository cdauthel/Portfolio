# Guide de compréhension du code pour le RAG

## Organisation générale

Le fichier principal `app/main.py` contient la majorité de l'application Streamlit. La navigation est définie par `SECTIONS`, puis la fonction `main()` route vers les fonctions de rendu selon la section et la sous-page choisies.

Le code est structuré en grands blocs:

- configuration, traduction déterministe et navigation;
- génération et chargement des données;
- pages Données;
- pages Scraping et API;
- pages d'analyse;
- pages spatiales;
- pages temporelles;
- pages Machine Learning;
- pages Deep Learning;
- Assistant IA;
- Architecture Cloud;
- Ops et reproductibilité.

## Fonctions importantes pour l'Assistant IA

### `_build_assistant_rag_documents`

Construit la base documentaire du RAG. Elle assemble:

- navigation;
- profils des tables;
- documents projet;
- fichiers dans `docs/assistant_rag/`;
- manifeste modèles;
- extraits ciblés du code.

### `_assistant_table_profile`

Produit un résumé textuel d'une table:

- nombre de lignes et colonnes;
- colonnes principales;
- types;
- variables quantitatives;
- variables qualitatives;
- variables temporelles;
- valeurs manquantes;
- exemples de lignes;
- statistiques descriptives simplifiées.

### `_retrieve_assistant_context`

Utilise TF-IDF et similarité cosinus pour sélectionner les passages les plus proches de la question utilisateur.

### `_call_assistant_llm`

Envoie la requête au fournisseur LLM:

- Ollama local ou Ollama Cloud via API native;
- Jan.ai, LM Studio ou proxy via API compatible OpenAI.

### `_render_ai_chatbot_rag`

Affiche la configuration du fournisseur, endpoint, modèle, mode, paramètres et RAG.

### `_render_ai_chat_messages_fragment`

Gère la zone conversationnelle avec `st.fragment` afin d'éviter de relancer toute la page à chaque message.

## Comment répondre à une question sur le code

L'assistant doit expliquer le rôle de la fonction, pas seulement citer son nom.

Exemple:

"La fonction `_retrieve_assistant_context` sert à sélectionner les passages RAG les plus pertinents. Elle transforme la question et les documents en vecteurs TF-IDF, calcule une similarité cosinus, puis renvoie les meilleurs extraits dans une table."

## Limite

Le RAG indexe des extraits ciblés du code pour rester performant. Il ne doit pas prétendre connaître chaque ligne du fichier si l'extrait correspondant n'a pas été récupéré dans le contexte.
