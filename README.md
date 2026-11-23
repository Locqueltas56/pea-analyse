# Analyse PEA

Application web (téléphone et PC) d'analyse des actions éligibles au PEA, pour l'investissement long terme :
screener, fiche valeur (fondamentaux, score), canal de régression en σ, risque, comparateur, suivi.

## Contenu

- `docs/index.html` : l'application (un seul fichier, sans dépendance)
- `docs/data/stocks.json` : les données (actuellement **fictives**, voir ci-dessous)
- `tickers.csv` : la liste des valeurs analysées (à modifier librement)
- `tools/fetch_data.py` : récupère les vraies données Yahoo Finance
- `tools/make_demo.py` : génère des données fictives pour tester
- `.github/workflows/update.yml` : mise à jour automatique chaque jour de semaine

## Mise en ligne (GitHub Pages)

1. Crée un dépôt GitHub dédié (par exemple `pea-analyse`) et publie-y ce dossier avec GitHub Desktop.
2. Sur GitHub : Settings > Pages > Source : branche `main`, dossier `/docs`.
3. Onglet Actions > « Mise à jour des données » > Run workflow : les vraies données remplacent les fictives.
4. L'app est disponible à `https://<ton-compte>.github.io/pea-analyse/`, sur téléphone comme sur PC.

## Utilisation en local

```
cd docs
python -m http.server
```
puis ouvrir http://localhost:8000. Pour des vraies données en local : `pip install yfinance pandas` puis `python tools/fetch_data.py`.

## Limites

- Les données Yahoo Finance sont gratuites, souvent incomplètes (un « – » indique une donnée absente) et non garanties.
- `tickers.csv` ne garantit pas l'éligibilité PEA : vérifie-la auprès de ton courtier.
- Outil d'analyse personnel, pas un conseil en investissement.
