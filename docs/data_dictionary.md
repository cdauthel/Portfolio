# Data Dictionary (résumé)

## Retail
- `stores`: informations magasin (geo, capacité, type).
- `products`: dimension produit, coût/prix/marge cible.
- `customers`: profil client et localisation.
- `orders`: entête commande (timestamp, canal, promo, statut).
- `order_items`: lignes commande (produit, qty, discount, montant).
- `promotions`: campagne promo et uplift attendu.
- `weather_store_day`: météo par magasin et date.
- `events_city_day`: événements locaux et audience attendue.
- `inventory_store_day`: stock mensuel simulé.
- `returns`: retours et remboursements.

## Finance
- `assets`: univers d'actifs.
- `prices_daily`: OHLCV quotidien.
- `macro`: facteurs macro simulés.
- `portfolios_daily`: poids de portefeuilles simulés.
- `trades`: transactions de stratégie momentum simple.
