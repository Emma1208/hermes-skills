from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

from db import add_calendrier_dates, get_calendrier, previsions_matiere, save_fiche, search_fiches, init_db
from pdfy import LessonPlan, to_pdf


CAL = "calendrier"


def _str(s: Optional[str]) -> str:
    return (s or "").strip()


def import_csv(path: str) -> int:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    total = 0
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            classe = _str(row.get("classe") or row.get("class"))
            matiere = _str(row.get("matiere") or row.get("subject") or row.get("matière"))
            date = _str(row.get("date"))
            if classe and matiere and date:
                add_calendrier_dates(classe, matiere, [date])
                total += 1
    return total


def import_excel(path: str) -> int:
    try:
        from openpyxl import load_workbook
    except Exception as e:
        raise RuntimeError("openpyxl requis pour Excel. Installe-le: pip install openpyxl") from e

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    wb = load_workbook(p, read_only=True, data_only=True)
    total = 0
    try:
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return 0
        header = [str(h).strip().lower() if h else "" for h in rows[0]]
        ci = next((i for i, h in enumerate(header) if h in ("classe", "class")), None)
        mi = next((i for i, h in enumerate(header) if h in ("matiere", "matière", "subject")), None)
        di = next((i for i, h in enumerate(header) if h == "date"), None)
        if ci is None or mi is None or di is None:
            raise RuntimeError("Colonnes requises: classe, matiere, date")
        for row in rows[1:]:
            if len(row) <= max(ci, mi, di):
                continue
            classe = _str(row[ci])
            matiere = _str(row[mi])
            date = _str(row[di])
            if classe and matiere and date:
                add_calendrier_dates(classe, matiere, [date])
                total += 1
    finally:
        wb.close()
    return total


def cmd_init(args: argparse.Namespace) -> int:
    init_db()
    print("Base initialisée: fiches.db")
    return 0


def cmd_calendrier(args: argparse.Namespace) -> int:
    if args.action == "add":
        dates = [d.strip() for d in args.dates.split(",") if d.strip()]
        n = add_calendrier_dates(args.classe, args.matiere, dates)
        print(f"Ajouté {n} date(s) calendrier: {args.classe}/{args.matiere}")
    elif args.action == "show":
        data = get_calendrier(args.classe or None)
        if not data:
            print("Calendrier vide")
            return 0
        for cl, mats in data.items():
            if args.classe and cl != args.classe:
                continue
            print(f"\nClasse: {cl}")
            for mat, ds in mats.items():
                print(f"  {mat}: {', '.join(sorted(ds))}")
    return 0


def cmd_prevue(args: argparse.Namespace) -> int:
    data = previsions_matiere(args.classe, args.from_date, args.to_date)
    if not data:
        print("Aucune prévision dans cette période")
        return 0
    print(f"Prévisions {args.classe} ({args.from_date} → {args.to_date}):")
    for mat, ds in sorted(data.items()):
        print(f"  {mat}: {', '.join(sorted(ds))}")
    return 0


def cmd_fiche(args: argparse.Namespace) -> int:
    plan = LessonPlan(
        classe=args.classe,
        matiere=args.matiere,
        date_str=args.date,
        objectif=_str(args.objectif),
        contenu=[l.strip() for l in (_str(args.contenu) or "").splitlines() if l.strip()] or ["(à compléter)"],
        exercice=[l.strip() for l in (_str(args.exercice) or "").splitlines() if l.strip()] or ["(à compléter)"],
        evaluation=_str(args.evaluation) or None,
        ressources=[l.strip() for l in (_str(args.ressources) or "").splitlines() if l.strip()] or None,
    )
    pdf = to_pdf(plan)
    save_fiche(
        classe_nom=args.classe,
        matiere_nom=args.matiere,
        date_str=args.date.isoformat() if hasattr(args.date, "isoformat") else str(args.date),
        objectif=plan.objectif,
        contenu="\n".join(plan.contenu),
        exercice="\n".join(plan.exercice),
        evaluation=plan.evaluation or "",
        ressources="\n".join(plan.ressources or []),
        pdf_path=str(pdf),
    )
    print(f"Fiche générée: {pdf}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    p = Path(args.path)
    if not p.exists():
        print(f"Fichier introuvable: {args.path}")
        return 2
    if p.suffix.lower() in (".xlsx", ".xlsm", ".xltx", ".xltm"):
        n = import_excel(args.path)
    elif p.suffix.lower() == ".csv":
        n = import_csv(args.path)
    else:
        print("Format supporté: .csv, .xlsx")
        return 2
    print(f"Import calendrier OK: {n} entrées depuis {p.name}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    rows = search_fiches(classe_nom=args.classe or None, matiere_nom=args.matiere or None, q=args.q or "")
    if not rows:
        print("Aucun résultat")
        return 0
    for r in rows:
        print(f"[{r['date']}] {r['classe']}/{r['matiere']} — {r['objectif'][:80]}")
        print(f"  PDF: {r['pdf_path'] or 'aucun'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="edu", description="Assistant pédagogique")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("init")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("calendrier")
    s.add_argument("action", choices=["add", "show"])
    s.add_argument("--classe", required=False)
    s.add_argument("--matiere", required=False)
    s.add_argument("--dates", required=False)
    s.set_defaults(func=cmd_calendrier)

    s = sub.add_parser("prevue")
    s.add_argument("classe")
    s.add_argument("--from", dest="from_date", required=True)
    s.add_argument("--to", dest="to_date", required=True)
    s.set_defaults(func=cmd_prevue)

    s = sub.add_parser("fiche")
    s.add_argument("classe")
    s.add_argument("matiere")
    s.add_argument("date")
    s.add_argument("--objectif", default="")
    s.add_argument("--contenu", default="")
    s.add_argument("--exercice", default="")
    s.add_argument("--evaluation", default="")
    s.add_argument("--ressources", default="")
    s.set_defaults(func=cmd_fiche)

    s = sub.add_parser("import")
    s.add_argument("path")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("search")
    s.add_argument("--classe", default="")
    s.add_argument("--matiere", default="")
    s.add_argument("q", nargs="?", default="")
    s.set_defaults(func=cmd_search)

    return p


def main() -> int:
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
