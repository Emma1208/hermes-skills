from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import List, Optional

from fpdf import FPDF


DATA_DIR = Path(__file__).with_name("data")
OUT_DIR = DATA_DIR / "out"
OUT_DIR.mkdir(exist_ok=True)


class LessonPlan:
    def __init__(
        self,
        classe: str,
        matiere: str,
        date_str: str,
        objectif: str,
        contenu: List[str],
        exercice: List[str],
        evaluation: Optional[str] = None,
        ressources: Optional[List[str]] = None,
    ) -> None:
        self.classe = classe
        self.matiere = matiere
        self.date = date_str if isinstance(date_str, date) else date.fromisoformat(date_str)
        self.objectif = objectif
        self.contenu = contenu
        self.exercice = exercice
        self.evaluation = evaluation
        self.ressources = ressources


class PDFFiche(FPDF):
    def _cw(self) -> float:
        return self.w - self.l_margin - self.r_margin

    def header(self) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "Fiche de cours", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def render(self, plan: LessonPlan) -> None:
        w = self._cw()
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 6, f"{plan.classe} - {plan.matiere} - {plan.date.isoformat()}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        def section(title: str, body: Optional[str], items: Optional[List[str]] = None) -> None:
            self.set_font("Helvetica", "B", 11)
            self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 11)
            text = (body or "") if items is None else "\n".join(f"- {x}" for x in (items or [])) or "-"
            self.multi_cell(w, 6, text)
            self.ln(1)

        section("Objectif", plan.objectif)
        section("Contenu", None, plan.contenu)
        section("Exercices / Activites", None, plan.exercice)
        if plan.evaluation:
            section("Evaluation", plan.evaluation)
        if plan.ressources:
            section("Ressources", None, plan.ressources)

        self.ln(3)
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, f"Genere le {date.today().isoformat()}", align="R")


def to_pdf(plan: LessonPlan) -> Path:
    out = OUT_DIR / f"fiche_{plan.classe}_{plan.matiere}_{plan.date.isoformat()}.pdf"
    pdf = PDFFiche()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.render(plan)
    pdf.output(str(out))
    return out


def to_pdf_from_fields(
    classe: str,
    matiere: str,
    date_str: str,
    objectif: str,
    contenu: List[str],
    exercice: List[str],
    evaluation: Optional[str] = None,
    ressources: Optional[List[str]] = None,
) -> Path:
    plan = LessonPlan(
        classe=classe,
        matiere=matiere,
        date_str=date_str,
        objectif=objectif,
        contenu=contenu,
        exercice=exercice,
        evaluation=evaluation,
        ressources=ressources,
    )
    return to_pdf(plan)
