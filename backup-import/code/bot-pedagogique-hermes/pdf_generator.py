#!/usr/bin/env python3
"""Génération de PDF — Fiche de préparation modèle Minga la Paix."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fpdf import FPDF

DATA_DIR = Path(__file__).parent / "data" / "out"


class FichePDF(FPDF):
    """PDF formaté selon le modèle de fiche de préparation."""

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, "COMPLEXE SCOLAIRE MINGA LA PAIX", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 5, "FICHE DE PREPARATION DE LEÇON", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def _section_title(self, title: str):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(220, 220, 220)
        self.cell(0, 6, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def _field(self, label: str, value: str):
        self.set_font("Helvetica", "B", 8)
        self.cell(40, 5, f"  {label} : ")
        self.set_font("Helvetica", "", 8)
        # For multi-line values, use multi_cell
        w = self.w - self.l_margin - self.r_margin - 40
        if self.get_string_width(value) > w:
            x = self.get_x() + 40
            self.cell(40, 5, "")
            self.set_xy(x, self.get_y() - 5)
            self.multi_cell(w, 5, value, new_x="LMARGIN", new_y="NEXT")
        else:
            self.cell(0, 5, value, new_x="LMARGIN", new_y="NEXT")

    def _table_header(self):
        """En-tête du tableau 3 colonnes."""
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(200, 200, 200)
        col_w = [30, 70, 70]
        headers = ["Timing", "Activites du Facilitateur", "Activites de l'Apprenant"]
        for i, h in enumerate(headers):
            self.cell(col_w[i], 6, h, border=1, fill=True, align="C")
        self.ln()

    def _table_row(self, timing: str, fac: str, app: str):
        """Ligne du tableau 3 colonnes."""
        col_w = [30, 70, 70]
        self.set_font("Helvetica", "", 7)

        # Calculer le nombre de lignes nécessaires
        lines_fac = self._count_lines(fac, col_w[1] - 2)
        lines_app = self._count_lines(app, col_w[2] - 2)
        lines_timing = 1
        max_lines = max(lines_fac, lines_app, lines_timing)

        row_h = max(max_lines * 4, 6)

        # Vérifier si on a assez de place
        if self.get_y() + row_h > self.h - 25:
            self.add_page()
            self._table_header()

        x_start = self.get_x()
        y_start = self.get_y()

        # Timing
        self.set_xy(x_start, y_start)
        self.cell(col_w[0], row_h, timing, border=1, align="C")

        # Facilitateur
        self.set_xy(x_start + col_w[0], y_start)
        x_fac = self.get_x()
        self.multi_cell(col_w[1], 4, fac, border=1)
        y_after_fac = self.get_y()

        # Apprenant
        self.set_xy(x_start + col_w[0] + col_w[1], y_start)
        self.multi_cell(col_w[2], 4, app, border=1)
        y_after_app = self.get_y()

        # Ajuster la hauteur et combler si nécessaire
        final_y = max(y_after_fac, y_after_app, y_start + row_h)
        self.set_y(final_y)

    def _count_lines(self, text: str, width: float) -> int:
        """Estime le nombre de lignes nécessaires."""
        if not text:
            return 1
        self.set_font("Helvetica", "", 7)
        words = text.split()
        lines = 1
        current = ""
        for w in words:
            test = f"{current} {w}".strip()
            if self.get_string_width(test) > width:
                lines += 1
                current = w
            else:
                current = test
        return lines


def generer_fiche_pdf(
    classe_nom: str,
    branche_nom: str,
    sujet: str,
    objectif: str,
    methodes: str,
    reference: str,
    revision_question: str,
    revision_reponse: str,
    motivation: str,
    annonce_sujet: str,
    analyse: Optional[List[Dict]] = None,
    synthese: str = "",
    evaluation: str = "",
) -> Path:
    """Génère le PDF de la fiche de préparation."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    date_slug = Path(__file__).parent.parent.stem if False else "now"
    from datetime import date
    datestr = date.today().isoformat()
    filename = f"fiche_{classe_nom}_{branche_nom}_{sujet[:20]}_{datestr}.pdf"
    # Nettoyer le nom
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in filename)
    out_path = DATA_DIR / safe

    pdf = FichePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── EN-TÊTE ──────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 9)
    pdf._section_title("EN-TETE")

    pdf._field("Niveau", classe_nom)
    pdf._field("Branche", branche_nom)
    pdf._field("Sujet de la lecon", sujet)
    pdf._field("Objectif specifique", objectif)
    pdf._field("Methodes", methodes)
    pdf._field("Reference", reference)
    pdf.ln(2)

    # ── CORPS : TABLEAU 3 COLONNES ────────────────────────────
    pdf._section_title("CORPS DE LA FICHE")
    pdf._table_header()

    # ➤ I. ACTIVITÉS INITIALES
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(0, 5, "I. ACTIVITES INITIALES", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf._table_row(
        "5 min",
        f"A. REVISION\nQuestion : {revision_question}",
        f"Reponse attendue : {revision_reponse}",
    )

    pdf._table_row(
        "5 min",
        f"B. MOTIVATION\n{motivation}",
        "Les eleves reflechissent et participent.",
    )

    pdf._table_row(
        "2 min",
        f"Annonce du sujet : {annonce_sujet}",
        "Les eleves notent le sujet.",
    )
    pdf.ln(1)

    # ➤ II. ACTIVITÉS PRINCIPALES
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(0, 5, "II. ACTIVITES PRINCIPALES", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf._table_header()
    if analyse:
        for item in analyse:
            timing = item.get("timing", "10 min")
            fac = item.get("facilitateur", "")
            app = item.get("apprenant", "")
            pdf._table_row(
                f"A. ANALYSE\n{timing}",
                fac,
                app,
            )
    else:
        pdf._table_row("15 min", "(Analyse a developper)", "(Participation)")

    pdf._table_row(
        "5 min",
        f"B. SYNTHESE\n{synthese}",
        "Les eleves notent la synthese dans leurs cahiers.",
    )
    pdf.ln(1)

    # ➤ III. ACTIVITÉS DE CONTRÔLE
    pdf.set_font("Helvetica", "B", 7)
    pdf.cell(0, 5, "III. ACTIVITES DE CONTRÔLE ET D'INTEGRATION", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf._table_row(
        "10 min",
        f"Evaluation :\n{evaluation}",
        "Les eleves realisent l'exercice.",
    )

    pdf.output(str(out_path))
    return out_path
