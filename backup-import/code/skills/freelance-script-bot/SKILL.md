---
name: freelance-script-bot
description: Générateur de scripts Python livrables et revendables à partir d'une demande client. Prend une spécification (marché, trading, automatisation, pédagogie, scraping, API), produit un script Python propre, documenté, exécutable, avec README + requirements, prêt à livrer ou vendre. Inclut un scaffold CLI et un modèle de devis/prix.
---

# Freelance Script Bot

Compétence pour transformer une **demande client** en un **script Python livrable**
(prêt à revendre ou à automatiser). Cible les domaines de l'utilisateur :
marché/trading, automatisation (APIs, scraping, bots), pédagogie, finance.

## Trigger conditions
- L'utilisateur demande de « faire un script », « créer un bot », « générer un
  code pour un client », « un script de <tâche> à vendre », « livrer un script Python ».
- L'utilisateur parle de prestation freelance / prestation de code.
- L'utilisateur veut packager un script existant en produit livrable (README + requirements + CLI).

## Principe de livraison (EXIGEANCE)
Un script « freelance » n'est PAS un bout de code jetable. Il doit être :
1. **Exécutable direct** (`python3 script.py` ou avec `--help` clair) — pas de
   flags obscurs pour le client final.
2. **Documenté** : docstring module + README expliquant install + usage.
3. **Paramétré proprement** : config dans un `.env` ou args clairs, JAMAIS de
   secret en dur.
4. **Livrable** : dossier `nom_du_script/` avec `script.py`, `README.md`,
   `requirements.txt`, `.env.example`.

## Workflow (à suivre dans l'ordre)
1. **Clarifier la demande** (si ambiguë) : entrée/sortie attendues, source de
   données (API ? fichier ? site ?), fréquence, contraintes (gratuit/payant,
   clé API requise ?).
2. **Choisir un modèle** dans `templates/` selon le type :
   - `api_bot.py` — bot interagissant avec une API (REST, clé dans `.env`)
   - `scraper.py` — scraping respectueux (robots.txt, délai, user-agent)
   - `cli_tool.py` — outil ligne de commande avec `argparse` + `--help`
   - `telegram_bot.py` — bot Telegram interactif (menus/boutons, style user)
   - `automation.py` — tâche planifiée / cron
3. **Générer le script** dans `~/freelance/<nom>/` via
   `scripts/scaffold.py` (voir ci-dessous) OU écrire directement le code.
4. **Tester** le script (exécution réelle, pas seulement lint) si possible.
5. **Générer le devis** avec `scripts/quote.py` (modèle prix par défaut).
6. **Livrer** : dossier zippé + README + mode d'emploi client.

## Conventions utilisateur (ne pas re-deriver)
- Style **direct, exécution autonome**, résultat attendu sans pas-à-pas.
- Bots = **interactifs (menus + boutons)**, PAS de CLI complexe pour l'utilisateur final.
- Français pour la doc client ; code commenté en francais si client francophone.
- **Ne JAMAIS toucher au venv Hermes** (`~/.hermes/hermes-agent/venv`).
  Si le script a besoin de deps : venv dédié (voir hermes-termux-ops).

## Scripts fournis
- `scripts/scaffold.py` — crée un dossier projet livrable complet depuis un nom + type.
- `scripts/quote.py` — génère un devis (prix par défaut RDC/freelance).

## Voir aussi
- `templates/` — modèles de scripts de départ (copier/adapter).
- skill `hermes-termux-ops` — pour l'exécution/cron sur ce Termux.
