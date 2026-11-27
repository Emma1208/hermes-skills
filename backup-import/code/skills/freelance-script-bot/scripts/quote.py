#!/usr/bin/env python3
"""Generation d'un devis freelance pour un script Python.

Usage:
    python3 quote.py <type> <heures> [--complexite 1|2|3] [--urgence]

Tarif par defaut (RDC / freelance debutant-intermediaire) :
    - taux horaire de base : 15 USD/h
    - complexite 2 : x1.5, complexite 3 : x2.2
    - urgence (< 48h) : +30%
    - minimum de facturation : 30 USD
"""
import argparse

TAUX_BASE = 15.0  # USD / heure
MULT_COMPLEXITE = {1: 1.0, 2: 1.5, 3: 2.2}
MIN_FACTURE = 30.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("type", help="Type de script (api_bot, scraper, cli_tool, telegram_bot, automation)")
    ap.add_argument("heures", type=float, help="Heures estimees")
    ap.add_argument("--complexite", type=int, choices=[1, 2, 3], default=1)
    ap.add_argument("--urgence", action="store_true", help="Livraison < 48h (+30%)")
    args = ap.parse_args()

    prix = TAUX_BASE * args.heures * MULT_COMPLEXITE[args.complexite]
    if args.urgence:
        prix *= 1.3
    prix = max(prix, MIN_FACTURE)

    print("=" * 44)
    print("  DEVIS — Script Python freelance")
    print("=" * 44)
    print(f"  Type           : {args.type}")
    print(f"  Heures est.    : {args.heures}")
    print(f"  Complexite     : {args.complexite} (x{MULT_COMPLEXITE[args.complexite]})")
    print(f"  Urgence        : {'oui (+30%)' if args.urgence else 'non'}")
    print("-" * 44)
    print(f"  PRIX TOTAL     : {prix:.0f} USD")
    print("=" * 44)
    print("  Delai suggéré  : 3-7 jours ouvrés (sauf urgence)")
    print("  Paiement       : 50% avance / 50% livraison")
    print("  Inclut         : code + README + requirements + 1 revision")

if __name__ == "__main__":
    main()
