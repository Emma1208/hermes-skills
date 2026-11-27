#!/usr/bin/env python3
"""Scaffold d'un projet script livrable freelance.

Usage:
    python3 scaffold.py <nom_projet> <type> [--desc "..."]

Types: api_bot | scraper | cli_tool | telegram_bot | automation

Cree ~/freelance/<nom>/ avec script.py, README.md, requirements.txt, .env.example
"""
import argparse
import os
from pathlib import Path

TEMPLATES = {
    "api_bot": '''#!/usr/bin/env python3
"""Bot API - {desc}
Clee API lue depuis .env (JAMAIS en dur).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("API_BASE_URL", "https://api.exemple.com")

def main():
    if not API_KEY:
        raise SystemExit("API_KEY manquante dans .env")
    print(f"Connexion a {{BASE_URL}} ...")
    # TODO: implementer la logique metier ici

if __name__ == "__main__":
    main()
''',
    "scraper": '''#!/usr/bin/env python3
"""Scraper respectueux - {desc}
Respecte robots.txt, delai entre requetes, user-agent declare.
"""
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "MonScriptFreelance/1.0 (+contact: client@exemple.com)"}
DELAY = 1.5  # secondes entre requetes

def scrape(url: str):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # TODO: extraire les donnees cibles
    return soup.get_text()[:200]

def main():
    urls = []  # TODO: lister les URLs cibles
    for url in urls:
        print(scrape(url))
        time.sleep(DELAY)

if __name__ == "__main__":
    main()
''',
    "cli_tool": '''#!/usr/bin/env python3
"""Outil CLI - {desc}
"""
import argparse

def main():
    p = argparse.ArgumentParser(description="{desc}")
    p.add_argument("entree", help="Fichier/valeur d'entree")
    p.add_argument("-o", "--output", help="Fichier de sortie")
    args = p.parse_args()
    # TODO: logique
    print(f"Traitement de {{args.entree}} -> {{args.output or 'stdout'}}")

if __name__ == "__main__":
    main()
''',
    "telegram_bot": '''#!/usr/bin/env python3
"""Bot Telegram interactif - {desc}
Menus + boutons (style utilisateur). Token depuis .env.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Option A", callback_data="a"),
           InlineKeyboardButton("Option B", callback_data="b")]]
    await update.message.reply_text("Choisis :", reply_markup=InlineKeyboardMarkup(kb))

async def choix(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"Tu as choisi : {{q.data}}")
    # TODO: logique metier

def main():
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN manquant dans .env")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choix))
    app.run_polling()

if __name__ == "__main__":
    main()
''',
    "automation": '''#!/usr/bin/env python3
"""Tache automatisee - {desc}
Pensee pour etre lancee par cron (hermes cron create ... --no-agent).
Sortie via print() -> livree telle quelle.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    # TODO: logique metier (ex: appel API, generation rapport)
    print("Tache executee avec succes")

if __name__ == "__main__":
    main()
''',
}

REQS = {
    "api_bot": "python-dotenv>=1.0\nrequests>=2.31\n",
    "scraper": "requests>=2.31\nbeautifulsoup4>=4.12\n",
    "cli_tool": "",
    "telegram_bot": "python-dotenv>=1.0\npython-telegram-bot>=20.0\n",
    "automation": "python-dotenv>=1.0\n",
}

README = """# {name}

{desc}

## Installation
```bash
pip install -r requirements.txt
cp .env.example .env   # remplir les valeurs
```

## Utilisation
```bash
python3 {script}
```

## Configuration (.env)
Voir `.env.example`. **Aucun secret n'est en dur dans le code.**

## Livrable freelance
Script genere via la skill `freelance-script-bot`.
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nom")
    ap.add_argument("type", choices=list(TEMPLATES))
    ap.add_argument("--desc", default="Script genere pour client")
    args = ap.parse_args()

    base = Path.home() / "freelance" / args.nom
    base.mkdir(parents=True, exist_ok=True)
    script = base / f"{args.nom}.py"
    script.write_text(TEMPLATES[args.type].format(desc=args.desc))
    script.chmod(0o755)
    (base / "requirements.txt").write_text(REQS[args.type])
    (base / ".env.example").write_text("# Remplir ces valeurs\nAPI_KEY=\nTELEGRAM_BOT_TOKEN=\n")
    (base / "README.md").write_text(README.format(name=args.nom, desc=args.desc, script=args.nom + ".py"))
    print(f"Projet cree : {base}")
    print(f"  - {args.nom}.py ({args.type})")
    print(f"  - requirements.txt, .env.example, README.md")

if __name__ == "__main__":
    main()
