#!/usr/bin/env python3
"""Bot Pédagogique v2 — Dialogue interactif pour fiches de préparation."""

import logging
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from db import (
    ajouter_branche,
    ajouter_calendrier,
    ajouter_classe,
    chercher_fiches,
    find_or_create_branche,
    get_fiche,
    importer_calendrier,
    init,
    lister_branches,
    lister_calendrier,
    lister_classes,
    lister_fiches,
    previsions_semaine,
    sauvegarder_fiche,
)
from llm import generer_fiche_llm
from pdf_generator import generer_fiche_pdf

# ── CONFIG ────────────────────────────────────────────────────────

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ALLOWED_CHAT_IDS = os.getenv("ALLOWED_CHAT_IDS", "*")
BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).parent)).resolve()

ALLOWED: Optional[set] = None
if ALLOWED_CHAT_IDS != "*":
    ALLOWED = {int(x.strip()) for x in ALLOWED_CHAT_IDS.split(",") if x.strip()}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# États utilisateur stockés dans context.user_data
STATE_KEY = "etat"


# ── HELPERS ──────────────────────────────────────────────────────

def _allowed(chat_id: int) -> bool:
    return ALLOWED is None or chat_id in ALLOWED


async def _menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Classes & Matières", callback_data="menu_classes")],
        [InlineKeyboardButton("📅 Ajouter le calendrier", callback_data="menu_calendrier")],
        [InlineKeyboardButton("📝 Générer une fiche", callback_data="menu_fiche")],
        [InlineKeyboardButton("🔮 Prévisions", callback_data="menu_previsions")],
        [InlineKeyboardButton("📋 Mes fiches", callback_data="menu_mesfiches")],
    ])


async def _erreur(update: Update, msg: str = "❌ Une erreur est survenue."):
    """Envoie un message d'erreur et revient au menu."""
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=await _menu_keyboard())
    elif update.message:
        await update.message.reply_text(msg, reply_markup=await _menu_keyboard())


async def _repondre(update: Update, text: str, kb: Optional[InlineKeyboardMarkup] = None):
    """Remplacer le message en cours par du texte + clavier."""
    q = update.callback_query
    if q:
        await q.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)


# ── MENU PRINCIPAL ───────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _allowed(update.effective_chat.id):
        await update.message.reply_text("⛔ Accès non autorisé.")
        return
    context.user_data.clear()
    await update.message.reply_text(
        "📚 *Assistant Pédagogique — Complexe Scolaire Minga la Paix*\n\n"
        "Je t'aide à gérer tes classes, créer des fiches de préparation "
        "et suivre le calendrier scolaire.\n\nQue veux-tu faire ?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await _menu_keyboard(),
    )


async def menu_retour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data.clear()
    await q.edit_message_text(
        "📚 *Menu Principal*\n\nQue veux-tu faire ?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await _menu_keyboard(),
    )


# ── CLASSES & MATIÈRES ──────────────────────────────────────────

async def menu_classes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    classes = lister_classes()
    if not classes:
        await _repondre(update, "Aucune classe. Ajoute-en une :",
                       InlineKeyboardMarkup([
                           [InlineKeyboardButton("➕ Ajouter une classe", callback_data="add_classe")],
                           [InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")],
                       ]))
        return
    kb = [[InlineKeyboardButton(c["nom"], callback_data=f"classe_{c['id']}")] for c in classes]
    kb.append([InlineKeyboardButton("➕ Ajouter une classe", callback_data="add_classe")])
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])
    await q.edit_message_text(
        "📚 *Classes disponibles*\n\nChoisis une classe :",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def add_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data[STATE_KEY] = "add_classe"
    await q.edit_message_text(
        "📝 *Nouvelle classe*\n\nEnvoie le nom de la classe :\nEx: *Commerciale 1*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Annuler", callback_data="menu_retour")]]),
    )


async def add_classe_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get(STATE_KEY) != "add_classe":
        return
    nom = update.message.text.strip()
    if not nom:
        await update.message.reply_text("Le nom ne peut pas être vide.")
        return
    ajouter_classe(nom)
    context.user_data[STATE_KEY] = None
    await update.message.reply_text(
        f"✅ Classe *{nom}* ajoutée !",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await _menu_keyboard(),
    )


async def select_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("classe_"):
        classe_id = int(data.split("_")[1])
        context.user_data["classe_id"] = classe_id
        nom = next((c["nom"] for c in lister_classes() if c["id"] == classe_id), "?")
        branches = lister_branches(classe_id)
        if not branches:
            await q.edit_message_text(
                f"📚 *{nom}* — Aucune matière\n\nAjoute la première matière :",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Ajouter une matière", callback_data=f"new_branche_{classe_id}")],
                    [InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")],
                ]),
            )
            return
        kb = [[InlineKeyboardButton(b["nom"], callback_data=f"branche_{b['id']}_{classe_id}")] for b in branches]
        kb.append([InlineKeyboardButton("➕ Ajouter une matière", callback_data=f"new_branche_{classe_id}")])
        kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])
        await q.edit_message_text(
            f"📚 *{nom}* — Matières :",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(kb),
        )
    elif data.startswith("new_branche_"):
        classe_id = int(data.split("_")[2])
        context.user_data["classe_id"] = classe_id
        context.user_data[STATE_KEY] = "add_branche"
        nom = next((c["nom"] for c in lister_classes() if c["id"] == classe_id), "?")
        await q.edit_message_text(
            f"📝 *{nom}* — Nouvelle matière\n\nEnvoie le nom de la matière :\nEx: *Comptabilité*, *Français*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Annuler", callback_data="menu_retour")]]),
        )


async def add_branche_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get(STATE_KEY) != "add_branche":
        return
    nom = update.message.text.strip()
    classe_id = context.user_data.get("classe_id")
    if not classe_id:
        await update.message.reply_text("Erreur : classe non sélectionnée.")
        return
    if not nom:
        await update.message.reply_text("Le nom ne peut pas être vide.")
        return
    ajouter_branche(classe_id, nom)
    context.user_data[STATE_KEY] = None
    nom_classe = next((c["nom"] for c in lister_classes() if c["id"] == classe_id), "?")
    await update.message.reply_text(
        f"✅ Matière *{nom}* ajoutée à *{nom_classe}* !",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await _menu_keyboard(),
    )


# ── CALENDRIER ──────────────────────────────────────────────────

async def menu_calendrier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    classes = lister_classes()
    if not classes:
        await _repondre(update, "Ajoute d'abord une classe !",
                       InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")]]))
        return
    kb = [[InlineKeyboardButton(c["nom"], callback_data=f"cal_classe_{c['id']}")] for c in classes]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])
    await q.edit_message_text(
        "📅 Pour quelle classe veux-tu ajouter le calendrier ?",
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def cal_choisir_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("cal_classe_"):
        return
    classe_id = int(data.split("_")[2])
    context.user_data["cal_classe_id"] = classe_id
    nom = next((c["nom"] for c in lister_classes() if c["id"] == classe_id), "?")
    context.user_data["cal_classe_nom"] = nom

    branches = lister_branches(classe_id)
    if not branches:
        await q.edit_message_text(
            f"📅 *{nom}* — Ajoute d'abord des matières !\n\nVa dans *Classes & Matières* pour ajouter des matières.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await _menu_keyboard(),
        )
        return

    liste_mat = "\n".join(f"  • {b['nom']}" for b in branches)
    context.user_data[STATE_KEY] = "cal_saisie"

    await q.edit_message_text(
        f"📅 *Calendrier — {nom}*\n\n"
        f"Matières disponibles :\n{liste_mat}\n\n"
        "Envoie le calendrier ligne par ligne :\n\n"
        "```\n"
        "DATE | MATIERE\n"
        "2026-09-15 | Comptabilité\n"
        "2026-09-16 | Français\n"
        "```\n\n"
        "Ou avec horaires :\n"
        "`2026-09-15 | Comptabilité | 8h | 10h | Bilan comptable`\n\n"
        "La matière doit correspondre exactement à celles listées.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")]]),
    )


async def cal_saisie_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get(STATE_KEY) != "cal_saisie":
        return
    classe_id = context.user_data.get("cal_classe_id")
    nom_classe = context.user_data.get("cal_classe_nom", "?")
    text = update.message.text or ""

    lignes = [l.strip() for l in text.split("\n") if l.strip()]
    if not lignes:
        await update.message.reply_text("Aucune donnée trouvée.")
        return

    branches = {b["nom"].lower(): (b["id"], b["nom"]) for b in lister_branches(classe_id)}
    importes = 0
    erreurs = []

    for ligne in lignes:
        parts = [p.strip() for p in ligne.split("|")]
        if len(parts) < 2:
            continue
        date_str = parts[0].strip()
        matiere_nom = parts[1].strip()
        debut = parts[2].strip() if len(parts) > 2 else None
        fin = parts[3].strip() if len(parts) > 3 else None
        sujet = parts[4].strip() if len(parts) > 4 else None

        # Chercher la matière (insensible à la casse)
        mat_key = matiere_nom.lower().strip()
        info = branches.get(mat_key)
        if not info:
            erreurs.append(f"📅 {date_str} : matière '{matiere_nom}' inconnue")
            continue

        branche_id = info[0]
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            erreurs.append(f"📅 {date_str} : date invalide (YYYY-MM-DD)")
            continue

        ajouter_calendrier(classe_id, branche_id, date_str, debut, fin, sujet)
        importes += 1

    msg = f"✅ Calendrier *{nom_classe}* : **{importes} cours** importés"
    if erreurs:
        msg += "\n\n⚠️ *Erreurs* :\n" + "\n".join(erreurs[:5])
    if importes > 0:
        msg += "\n\n✅ Terminé !"

    context.user_data[STATE_KEY] = None
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=await _menu_keyboard())


# ── FICHE ────────────────────────────────────────────────────────

async def menu_fiche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    classes = lister_classes()
    if not classes:
        await _repondre(update, "Ajoute d'abord une classe !",
                       InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")]]))
        return
    kb = [[InlineKeyboardButton(c["nom"], callback_data=f"fclasse_{c['id']}")] for c in classes]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])
    await q.edit_message_text(
        "📝 Pour quelle classe générer une fiche ?",
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def fiche_choisir_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("fclasse_"):
        return
    classe_id = int(data.split("_")[1])
    context.user_data["f_classe_id"] = classe_id
    nom = next((c["nom"] for c in lister_classes() if c["id"] == classe_id), "?")
    context.user_data["f_classe_nom"] = nom

    branches = lister_branches(classe_id)
    if not branches:
        await q.edit_message_text(
            f"📝 *{nom}* — Ajoute d'abord des matières !\n\nVa dans *Classes & Matières*.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await _menu_keyboard(),
        )
        return

    kb = [[InlineKeyboardButton(b["nom"], callback_data=f"fbranche_{b['id']}")] for b in branches]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])
    await q.edit_message_text(
        f"📝 *{nom}* — Choisis la matière :",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def fiche_choisir_branche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("fbranche_"):
        return
    branche_id = int(data.split("_")[1])
    context.user_data["f_branche_id"] = branche_id
    nom_b = next((b["nom"] for b in lister_branches(context.user_data["f_classe_id"]) if b["id"] == branche_id), "?")
    context.user_data["f_branche_nom"] = nom_b

    context.user_data[STATE_KEY] = "f_sujet"
    await q.edit_message_text(
        f"📝 *{context.user_data['f_classe_nom']} / {nom_b}*\n\n"
        "Quel est le **sujet** de la leçon ?\n"
        "Ex: *Le bilan comptable*, *Le présent de l'indicatif*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Annuler", callback_data="menu_retour")]]),
    )


async def fiche_sujet_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get(STATE_KEY) != "f_sujet":
        return
    sujet = update.message.text.strip()
    if not sujet:
        await update.message.reply_text("Le sujet ne peut pas être vide.")
        return
    context.user_data["f_sujet"] = sujet
    context.user_data[STATE_KEY] = "f_date"
    await update.message.reply_text(
        f"📝 Sujet : *{sujet}*\n\n"
        "Pour quelle **date** ?\n"
        "Format: *YYYY-MM-DD* (ex: *2026-09-15*)\n"
        "ou *ajd* pour aujourd'hui, *dem* pour demain",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Annuler", callback_data="menu_retour")]]),
    )


async def fiche_date_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get(STATE_KEY) != "f_date":
        return
    date_input = update.message.text.strip().lower()
    today = date.today()

    if date_input in ("ajd", "aujourd'hui", "auj"):
        date_str = today.isoformat()
    elif date_input in ("dem", "demain"):
        date_str = (today + timedelta(days=1)).isoformat()
    else:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            date_str = date_input
        except ValueError:
            await update.message.reply_text(
                "❌ Format invalide. Utilise YYYY-MM-DD, 'ajd' ou 'dem'."
            )
            return

    context.user_data["f_date"] = date_str
    classe_nom = context.user_data["f_classe_nom"]
    branche_nom = context.user_data["f_branche_nom"]
    sujet = context.user_data["f_sujet"]
    context.user_data[STATE_KEY] = None

    await update.message.reply_text(
        f"🧠 *Génération en cours...*\n"
        f"📚 {classe_nom} / {branche_nom}\n"
        f"📖 {sujet}\n"
        f"📅 {date_str}\n\n⏳ Appel IA OpenRouter...",
        parse_mode=ParseMode.MARKDOWN,
    )

    # Appel IA
    data_llm, error = generer_fiche_llm(classe_nom, branche_nom, sujet)
    if error or not data_llm:
        await update.message.reply_text(f"{error}", reply_markup=await _menu_keyboard())
        return

    # Sauvegarder
    fiche_id = sauvegarder_fiche(
        classe_id=context.user_data["f_classe_id"],
        branche_id=context.user_data["f_branche_id"],
        date_str=date_str,
        sujet=sujet,
        objectif=data_llm.get("objectif"),
        methodes=data_llm.get("methodes"),
        reference=data_llm.get("reference", ""),
        revision_question=data_llm.get("revision_question"),
        revision_reponse=data_llm.get("revision_reponse"),
        motivation=data_llm.get("motivation"),
        annonce_sujet=data_llm.get("annonce_sujet"),
        analyse=str(data_llm.get("analyse", [])),
        synthese=data_llm.get("synthese"),
        evaluation=data_llm.get("evaluation"),
        raw_llm=str(data_llm),
    )

    # PDF
    pdf_path = None
    try:
        pdf_path = generer_fiche_pdf(
            classe_nom=classe_nom, branche_nom=branche_nom, sujet=sujet,
            objectif=data_llm.get("objectif", ""),
            methodes=data_llm.get("methodes", ""),
            reference=data_llm.get("reference", ""),
            revision_question=data_llm.get("revision_question", ""),
            revision_reponse=data_llm.get("revision_reponse", ""),
            motivation=data_llm.get("motivation", ""),
            annonce_sujet=data_llm.get("annonce_sujet", ""),
            analyse=data_llm.get("analyse"),
            synthese=data_llm.get("synthese", ""),
            evaluation=data_llm.get("evaluation", ""),
        )
        sauvegarder_fiche(classe_id=context.user_data["f_classe_id"],
                          branche_id=context.user_data["f_branche_id"],
                          date_str=date_str, sujet=sujet, pdf_path=str(pdf_path))
    except Exception as e:
        logger.exception("PDF error")

    # Aperçu
    apercu = (
        f"✅ *Fiche générée !*\n\n"
        f"📚 *{classe_nom} / {branche_nom}*\n"
        f"📖 *{sujet}*\n"
        f"📅 {date_str}\n\n"
        f"🎯 *Objectif :*\n{data_llm.get('objectif','?')[:300]}\n\n"
        f"🔧 *Méthodes :* {data_llm.get('methodes','?')}\n\n"
        f"📖 *Révision :*\n{data_llm.get('revision_question','?')[:200]}\n\n"
        f"💡 *Motivation :*\n{data_llm.get('motivation','?')[:200]}"
    )

    kb = []
    if pdf_path:
        kb.append([InlineKeyboardButton("📄 Voir le PDF", callback_data=f"pdf_{fiche_id}")])
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])

    await update.message.reply_text(apercu, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


# ── PRÉVISIONS ──────────────────────────────────────────────────

async def menu_previsions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    classes = lister_classes()
    if not classes:
        await _repondre(update, "Ajoute d'abord une classe !",
                       InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")]]))
        return
    kb = [[InlineKeyboardButton(c["nom"], callback_data=f"prev_classe_{c['id']}")] for c in classes]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu_retour")])
    await q.edit_message_text(
        "🔮 Pour quelle classe veux-tu voir les prévisions ?",
        reply_markup=InlineKeyboardMarkup(kb),
    )


async def previsions_afficher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("prev_classe_"):
        return
    classe_id = int(data.split("_")[2])
    nom_classe = next((c["nom"] for c in lister_classes() if c["id"] == classe_id), "?")
    today = date.today()
    debut = today.isoformat()
    fin = (today + timedelta(days=7)).isoformat()

    entries = previsions_semaine(classe_id, debut, fin)
    if not entries:
        await q.edit_message_text(
            f"🔮 *{nom_classe}* — Aucune prévision du {debut} au {fin}\n\n"
            "Ajoute d'abord le calendrier !",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await _menu_keyboard(),
        )
        return

    dates = {}
    for e in entries:
        dates.setdefault(e["date"], []).append(e)

    lignes = [f"🔮 *{nom_classe}* — Prévisions {debut} à {fin}\n"]
    for d in sorted(dates.keys()):
        lignes.append(f"\n📅 *{d}*")
        for e in dates[d]:
            h = f" {e['heure_debut'] or '?'}-{e['heure_fin'] or '?'}" if e.get('heure_debut') else ""
            fiche = "✅" if e["fiche_existe"] else "⬜"
            lignes.append(f"  {fiche} {h} — *{e['branche_nom']}* — {e.get('sujet','') or '(sans sujet)'}")

    lignes.append("\n\n✅ = Fiche prête | ⬜ = À préparer")
    await q.edit_message_text("\n".join(lignes), parse_mode=ParseMode.MARKDOWN, reply_markup=await _menu_keyboard())


# ── MES FICHES ──────────────────────────────────────────────────

async def menu_mesfiches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    fiches = lister_fiches(limit=10)
    if not fiches:
        await q.edit_message_text(
            "📋 Aucune fiche pour le moment.\n\n"
            "Va dans *Générer une fiche* pour en créer une !",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await _menu_keyboard(),
        )
        return
    lignes = ["📋 *Mes 10 dernières fiches*\n"]
    for f in fiches:
        lignes.append(f"• [{f['date']}] *{f['classe_nom']} / {f['branche_nom']}*\n   {f['sujet'][:60]}")
    await q.edit_message_text("\n".join(lignes), parse_mode=ParseMode.MARKDOWN, reply_markup=await _menu_keyboard())


# ── ENVOI PDF ────────────────────────────────────────────────────

async def envoyer_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("pdf_"):
        return
    fiche_id = int(data.split("_")[1])
    fiche = get_fiche(fiche_id)
    if fiche and fiche.get("pdf_path"):
        pdf = Path(fiche["pdf_path"])
        if pdf.exists():
            await q.message.reply_document(
                document=str(pdf), filename=pdf.name,
                caption=f"📄 Fiche : {fiche['classe_nom']} / {fiche['branche_nom']} — {fiche['sujet']}",
            )
            return
    await q.message.reply_text("❌ PDF introuvable.")


# ── FALLBACK TEXTE ──────────────────────────────────────────────

async def fallback_texte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les messages texte selon l'état."""
    etat = context.user_data.get(STATE_KEY)
    if etat == "add_classe":
        await add_classe_texte(update, context)
    elif etat == "add_branche":
        await add_branche_texte(update, context)
    elif etat == "cal_saisie":
        await cal_saisie_texte(update, context)
    elif etat == "f_sujet":
        await fiche_sujet_texte(update, context)
    elif etat == "f_date":
        await fiche_date_texte(update, context)
    else:
        await update.message.reply_text(
            "Utilise /start pour voir le menu.",
            reply_markup=await _menu_keyboard(),
        )


# ── ROUTEUR CALLBACK ────────────────────────────────────────────

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route les callbacks vers les bons handlers."""
    q = update.callback_query
    data = q.data

    # Mapping direct callback → handler
    table = {
        "menu_retour": menu_retour,
        "menu_classes": menu_classes,
        "menu_calendrier": menu_calendrier,
        "menu_fiche": menu_fiche,
        "menu_previsions": menu_previsions,
        "menu_mesfiches": menu_mesfiches,
        "add_classe": add_classe,
    }
    handler = table.get(data)
    if handler:
        return await handler(update, context)

    # Préfixes
    if data.startswith("classe_") or data.startswith("new_branche_"):
        return await select_classe(update, context)
    if data == "branche_" or data.startswith("branche_"):
        # Juste informatif, on ne fait rien
        await q.answer()
        return
    if data.startswith("cal_classe_"):
        return await cal_choisir_classe(update, context)
    if data.startswith("fclasse_"):
        return await fiche_choisir_classe(update, context)
    if data.startswith("fbranche_"):
        return await fiche_choisir_branche(update, context)
    if data.startswith("prev_classe_"):
        return await previsions_afficher(update, context)
    if data.startswith("pdf_"):
        return await envoyer_pdf(update, context)

    await q.answer()
    await q.edit_message_text("Option inconnue.", reply_markup=await _menu_keyboard())


# ── MAIN ─────────────────────────────────────────────────────────

def main():
    init()
    from telegram.request import HTTPXRequest
    req = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30, pool_timeout=30)
    app = Application.builder().token(BOT_TOKEN).request(req).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_retour))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_router))

    # Messages texte
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_texte))

    logger.info("🤖 Bot Pédagogique v2 démarré")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
