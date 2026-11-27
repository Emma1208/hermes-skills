from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List

from db import get_calendrier, previsions_matiere, save_fiche
from pdfy import LessonPlan, to_pdf


DATA_DIR = Path(__file__).with_name("data")


def add_calendrier(classe: str, matiere: str, dates: List[str]) -> None:
    from db import add_calendrier_dates
    add_calendrier_dates(classe, matiere, dates)


def make_and_save_fiche(
    classe: str,
    matiere: str,
    d: str | date,
    objectif: str,
    contenu: List[str],
    exercice: List[str],
    evaluation: str | None = None,
    ressources: List[str] | None = None,
) -> Path:
    plan = LessonPlan(
        classe=classe,
        matiere=matiere,
        date_str=d,
        objectif=objectif,
        contenu=contenu,
        exercice=exercice,
        evaluation=evaluation,
        ressources=ressources,
    )
    out = to_pdf(plan)
    save_fiche(
        classe_nom=classe,
        matiere_nom=matiere,
        date_str=plan.date.isoformat(),
        objectif=objectif,
        contenu="\n".join(contenu),
        exercice="\n".join(exercice),
        evaluation=evaluation or "",
        ressources="\n".join(ressources or []),
        pdf_path=str(out),
    )
    return out


def cli_example() -> None:
    add_calendrier("6eme", "francais", ["2026-09-01", "2026-09-08", "2026-09-15"])
    add_calendrier("6eme", "maths", ["2026-09-03", "2026-09-10"])

    prev = previsions_matiere("6eme", "2026-09-01", "2026-09-10")
    print("Previsions:", prev)

    out = make_and_save_fiche(
        classe="6eme",
        matiere="francais",
        d="2026-09-08",
        objectif="Lire et comprendre un texte narratif court.",
        contenu=["Texte : Le voyage de Kali", "Vocabulaire : les champs lexicaux", "Grammaire : le passe compose"],
        exercice=["Resumer en 5 lignes", "Repondre a 3 questions de comprehension"],
        evaluation="Quiz ecrit 5 min",
        ressources=["Extrait photocopie"],
    )
    print("PDF:", out)


if __name__ == "__main__":
    cli_example()
