# ChatMD, LLM et RAG

## Principe

ChatMD peut appeler un LLM depuis un parcours scénarisé. L'intérêt est de garder un contrôle fort sur les moments où l'IA intervient, les consignes transmises et les connaissances utilisées.

## Appels LLM

Deux usages principaux sont prévus:

- appel explicite par l'utilisateur avec `!useLLM`, utile pour les tests;
- appel intégré dans un message du chatbot avec un bloc:

```md
`!useLLM`
Prompt
`END !useLLM`
```

Pour un portfolio public, il est préférable de désactiver l'appel libre avec `userCanCallLLM: false` afin d'éviter les usages non contrôlés.

## Historique

L'historique peut être activé globalement avec `useHistory: true`, ou ponctuellement dans un prompt avec `!useHistory`.

Cela permet de poursuivre une conversation, mais il faut prévoir des conditions de sortie pour éviter une boucle infinie.

## RAG

Le RAG consiste à fournir au modèle des passages issus d'une base de connaissances. ChatMD peut sélectionner les passages pertinents avec:

```md
!RAG: {question} {url:"URL_DU_FICHIER" maxResults:5 separator:"---"}
```

La réponse doit prioriser le contexte fourni. Si l'information n'est pas présente dans le contexte, le chatbot doit l'indiquer explicitement.

## Configuration YAML type

```yaml
---
variablesDynamiques: true
useLLM:
  url: http://localhost:11434/api/chat
  model: llama3.2
  userCanCallLLM: false
  useHistory: true
  maxTokens: 600
  stream: true
  RAGinformations: useFile
  RAGmaxTopElements: 5
  RAGprompt: |
    Réponds uniquement à partir du contexte fourni. Si l'information manque, indique-le clairement.
---
```

## Bonnes pratiques portfolio

- Protéger l'accès par mot de passe.
- Garder les clés hors du fichier public.
- Préférer un proxy backend pour un usage recruteur public.
- Journaliser les erreurs sans stocker de données sensibles.
- Encadrer les réponses: citations du contexte, limites, prochaines actions.

