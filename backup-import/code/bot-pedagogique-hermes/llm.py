#!/usr/bin/env python3
"""Appel OpenRouter pour générer les fiches de préparation."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen


def get_openrouter_key() -> Optional[str]:
    """Récupère la clé OpenRouter depuis l'environnement."""
    # 1) .env du bot
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(str(env_path))

    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key

    # 2) .env d'Hermes
    hermes_env = Path.home() / ".hermes" / ".env"
    if hermes_env.exists():
        from dotenv import load_dotenv
        load_dotenv(str(hermes_env))
        return os.getenv("OPENROUTER_API_KEY")

    return None


_PROMPT_TEMPLATE = """Tu es un expert en pédagogie pour l'option {branche} au Complexe Scolaire Minga la Paix.

Tâche : Rédige une fiche de préparation de leçon complète en utilisant scrupuleusement la structure suivante issue de mon modèle :

1. En-tête :
   * Niveau : {classe}
   * Branche : {branche}
   * Sujet de la leçon : {sujet}
   * Objectif spécifique : (Rédige un objectif clair commençant par "À l'issue de la leçon, l'élève sera capable de...").
   * Méthodes : Utilise un mélange de : Expositive, Travail en groupe, Débat, ou Brainstorming.
   * Référence : Cite les manuels scolaires standards.

2. Corps de la fiche (Tableau en 3 colonnes : Timing | Activités du Facilitateur | Activités de l'Apprenant) :
   * I. ACTIVITÉS INITIALES :
     * A. RÉVISION : Propose une question sur les prérequis et la réponse attendue.
     * B. MOTIVATION : Crée une situation concrète ou un petit problème pour susciter l'intérêt.
     * Annonce du sujet : Formule la phrase de transition.
   * II. ACTIVITÉS PRINCIPALES :
     * A. ANALYSE : Décompose la matière point par point avec des questions précises du facilitateur et les actions/réponses de l'apprenant. Donne 2 à 4 étapes d'analyse.
     * B. SYNTHÈSE : Rédige un court résumé structuré de ce que l'élève doit noter.
   * III. ACTIVITÉS DE CONTRÔLE ET D'INTÉGRATION :
     * Évaluation : Propose un exercice d'application immédiate pour vérifier la compréhension.

Consigne de style : Sois bref, concis et utilise un langage simple adapté aux élèves.

Sujet à traiter : {sujet}

Réponds UNIQUEMENT au format JSON suivant, sans texte avant ni après :
{{
  "objectif": "...",
  "methodes": "...",
  "reference": "...",
  "revision_question": "...",
  "revision_reponse": "...",
  "motivation": "...",
  "annonce_sujet": "...",
  "analyse": [
    {{"timing": "...", "facilitateur": "...", "apprenant": "..."}},
    {{"timing": "...", "facilitateur": "...", "apprenant": "..."}}
  ],
  "synthese": "...",
  "evaluation": "..."
}}"""


def generer_fiche_llm(
    classe: str,
    branche: str,
    sujet: str,
    model: str = "deepseek/deepseek-chat-v3-0324:free",
) -> Tuple[Optional[Dict], Optional[str]]:
    """Appelle OpenRouter pour générer le contenu de la fiche.

    Retourne (dict_fiche, error_message).
    """
    key = get_openrouter_key()
    if not key:
        return None, "❌ Clé API OpenRouter introuvable. Configure OPENROUTER_API_KEY dans .env"

    prompt = _PROMPT_TEMPLATE.format(classe=classe, branche=branche, sujet=sujet)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    req = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://t.me/Mpedabotbot",
            "X-Title": "Bot Pedagogique",
        },
    )

    try:
        with urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
    except Exception as e:
        return None, f"❌ Erreur appel OpenRouter : {e}"

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None, f"❌ Réponse inattendue de l'API : {json.dumps(body, indent=2)[:500]}"

    # Extraire le JSON de la réponse
    content = content.strip()
    # Enlever les délimiteurs markdown si présents
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None, f"❌ Impossible d'analyser la réponse JSON. Réponse brute :\n{content[:1000]}"

    # Validation des champs requis
    required = ["objectif", "methodes", "revision_question", "revision_reponse",
                 "motivation", "annonce_sujet", "synthese", "evaluation"]
    for field in required:
        if field not in data:
            data[field] = f"(Champ '{field}' manquant)"

    if "analyse" not in data or not isinstance(data["analyse"], list):
        data["analyse"] = [
            {"timing": "10 min", "facilitateur": "(Analyse à développer)", "apprenant": "(Participation)"}
        ]

    return data, None
