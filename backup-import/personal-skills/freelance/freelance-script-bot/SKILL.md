---
name: freelance-script-bot
description: Build, deploy and maintain Emmanuel's Telegram script-bots (school bot Minga la Paix, freelance 2MT sports-betting bot, client-address manager) on Termux. Covers JSON/SQLite storage, roles, deps, deployment and invoicing conventions.
tags: [freelance, telegram, bot, termux, python, school, betting]
related_skills: [hermes-gateway-telegram, emmanuel-collaboration]
triggers:
  - bot telegram / créer un bot / déployer bot
  - Minga la Paix / fiche pédagogique / bot scolaire
  - freelance 2MT / pari sportif / 1xBet / Sofascore
  - bot adresse client / gestion clients / base de données clients
  - devis / invoice / livraison freelance
---

# Freelance Script-Bot (Emmanuel)

Emmanuel builds **Telegram bots** for clients and for his own school (Complexe Scolaire **Minga la Paix**, Kinshasa). The defining requirement: a bot is NOT done when the code runs locally — it must be **deployed, online, with buttons that actually react**. He tests bots for real on his phone (sends a Telegram screenshot + "Regarde") and expects you to diagnose FROM the image and fix.

## Hard rules (non-negotiable)
- **Deploy, don't just code.** Deliver a running bot (polling or webhook live on Termux/serveur). A local script is a failure.
- **Prove it with a real screenshot.** When validating, send a Telegram capture and say "Regarde"; fix against what the image shows.
- **Invoice separate from code.** For freelance work, produce a `devis`/invoice as a distinct artifact from the delivered code.
- **PTB version**: use **python-telegram-bot 22.6/22.8** on Termux Python 3.14. 21.x crashes (`Application.__stop_running_marker`). Always `pgrep -af python` before relaunching to avoid a second instance polling the same token (HTTP 409).
- **Token guard**: tokens starting `820389` are Hermes-EXCLUSIVE. A client bot using one triggers HTTP 409 and kills the gateway. Use a separate @BotFather token + startup guard refusing `820389`.

## Reliable Python deps (Termux)
- `httpx`, `python-dotenv`, `tenacity`, `pytz`, `python-telegram-bot==22.6`
- AVOID `parsel`/`lxml` on Termux unless `libxml2`/`libxslt-dev` are installed.
- Token and secrets live in `.env` (never hardcode). Load with `python-dotenv`.

## Bot 1 — Minga la Paix (school bot)
- **Storage**: JSON files. **Roles**: `enseignant` (teacher) and `parent`.
- **Pedagogical fiche format** (required output shape for fiches):
  - Header: `Niveau | Branche | Sujet | Objectif | Méthodes | Référence`
  - 3-column table `Timing | Facilitateur | Apprenant`, split into:
    - I. Activités initiales (Révision / Motivation / Annnonce)
    - II. Activités principales (Analyse / Synthèse)
    - III. Contrôle et intégration (Évaluation)
- Place: deploy under the school bot skill path; token in `.env`.

## Bot 2 — Freelance 2MT (sports-betting window bot)
- Place code in `~/freelance-2mt/`.
- **Fixtures**: verify via **Sofascore** + **football-data.org** (cross-check both).
- Morning message "statut fenêtre" during off-season (inter-saison).
- **1xBet link format**: `[{home} vs {away}](https://1xbet.com/en/line/football)`.

## Bot 3 — Client address manager (worked example)
Built `/root/freelance-clients-bot/bot_clients.py`: 3-step `ConversationHandler` (nom → tél → adresse),
SQLite `clients.db` storage, auto-generated clickable Google Maps link
(`https://www.google.com/maps/search/?api=1&query=<adresse>`), and filter by name OR phone.
DB logic + Maps + filtering were unit-validated; see `references/ptb-pitfalls.md` for the PTB 22.x
gotchas (timeout kwargs, token guard, dedicated venv, chat-not-found test pattern).

## Deployment target
- Personal Termux server on phone: `10.253.42.225:22`, user `u0_a556`. `~/server` hosts APIs/agents/trading (FastAPI :8000). Run bots there as background processes (see `hermes-termux-recovery` — NEVER inside the Hermes venv).
- Always run a bot in its OWN venv (`/root/freelance-clients-bot/venv` or `~/freelance-clients-bot/venv`), NOT `~/.hermes/hermes-agent/venv`.

## Verification
- `pgrep -af "python.*bot"` shows exactly one instance per token.
- `echo $VIRTUAL_ENV` ≠ `~/.hermes/hermes-agent/venv` (dedicated venv).
- Telegram capture shows buttons reacting to taps (not just text).
- For school bot: a generated fiche matches the 3-part structure above.
- Invoice file exists alongside delivered code.
- End-to-end: user opens bot + `/start` first (can't `sendMessage` to an un-started chat → 400).

## Pitfalls (learned this session)
- **PTB 22.x timeout kwargs** are BUILDER args (`connect_timeout`/`read_timeout`/`pool_timeout`), NOT `run_polling()` kwargs — passing them raises `TypeError`. On slow networks raise them to 30s to avoid `TimedOut`.
- **Token conflict (HTTP 409)**: `820389...` is Hermes-exclusive. Add a startup guard refusing any token starting `820389`.
- **Dedicated venv**: a bot accidentally launched inside the Hermes venv mixes processes — always spin up `venv/`.
- **Long outputs**: Telegram caps ~4096 chars/message — chunk list replies.
