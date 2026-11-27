# Targeted CV procedure — BSF example (concrete, reproducible)

Context: user (KAKESA MUDIMBA Dieudonné) had a live offer — BSF (Bibliothèques Sans
Frontières), Responsable Support (Admin/Finance/Logistique/RH), Kinshasa, deadline 15/07/2026.
We branched the reference CV into a targeted CV + motivation letter.

## Steps taken
1. cp /root/linkedin_app/generate_cv.py /root/linkedin_app/generate_cv_bsf.py
2. Edited the subtitle (header, ~line 121):
   pdf.cell(0, 6, "Candidat au poste de Responsable Support (Admin / Finance / Logistique / RH) — BSF", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
   (title line above stays "Curriculum Vitæ")
3. Inserted a new section right after "DOMAINES DE COMPÉTENCE À ÉVOLUER":
   section("III B. ADÉQUATION AU POSTE BSF — RESPONSABLE SUPPORT")
   para("Gestion financière & comptable : Licencié en Gestion Financière, avec une expérience de "
        "vérification des pièces comptables et de contrôle interne au Ministère des Finances (DRQC), "
        "et la production de rapports financiers.", keywords=set())
   para("Logistique & stocks : Agent d'appui logistique au projet PUC MED de Médecins Sans Frontières "
        "(suivi de stock, chaîne du froid, sécurité des locaux, reporting logistique).", keywords=set())
   para("Administration & conformité : encadrement, organisation et reporting en milieu éducatif et "
        "institutionnel ; sens affirmé de la rigueur et de la confidentialité.", keywords=set())
   para("Outil & langues : maîtrise de Word et Excel ; excellente maîtrise du français (écrit/oral) ; "
        "anglais lu, écrit, parlé (niveau moyen).", keywords=set())
   keywords=set() forces plain black, no keyword coloring — matches the user's FINAL decision.
4. Changed output: pdf.output("/root/linkedin_app/CV_KAKESA_MUDIMBA_BSF.pdf") + matching print.
5. Wrote Lettre_Motivation_BSF.txt mapping the same experiences to BSF's 4 pillars.

## Motivation-letter skeleton (reusable)
- Objet line naming the exact post + employer.
- Para 1: degree + statement that the post matches parcours/aspirations.
- Para 2: Min. Finances (vérification pièces, contrôle interne, rapports) -> rigueur/conformité.
- Para 3: MSF (stock, chaîne du froid, sécurité, reporting) -> standards ONG / environnement complexe.
- Para 4: transversal (encadrement, org, reporting) + outils (Word/Excel) + français + anglais moyen.
- Para 5: soft skills (motivé, intègre, proactif) + closing availability.
- Sign: KAKESA MUDIMBA Dieudonné, tel + email.

## Postuler
- BSF applied via makesense jobs portal (jobs.makesense.org/.../apply), NOT LinkedIn directly.
- Agent cannot click "Postuler" from mobile — either user applies via link, or agent emails the
  dossier if user provides a Gmail app-password. State this limitation clearly.

## KPMG RDC — Assistant débutant Pré-emploi Audit (concrete, 2026-07-16)
Offer on forms.office.com demanded "CV avec photo" + "lettre de demande d'emploi".
Missions stated: apply audit methodology, control accounts & run audit tests,
champion IFRS, draft synthesis with recommendations. Profile: Bac+5, appetite for
accounting/finance, rigorous + analytical, team player, professional English, IT tools.
Generator: `/root/linkedin_app/generer_cv_kpmg_cible.py` → `CV_KAKESA_MUDIMBA_KPMG.pdf` (2 pages).

Steps that differed from BSF:
1. **Photo REQUIRED** — added header-photo (see SKILL.md §1 photo EXCEPTION recipe),
   H=30mm band, image top-right, text left. User overrode his no-photo default.
2. **Adéquation au poste** mapped to the offer verbatim: DRQC stage (pièces comptables,
   rapports financiers) → base of audit controls; Licence Gestion Financière + OHADA +
   IFRS initiation → référentiels d'audit; MSF reporting → fiabilité d'info; Forex
   rigueur/analyse → atout contrôle; langues (FR/EN/Lingala) → missions Afrique
   Francophone Subsaharienne.
3. **Sections renumbered** to keep Adéquation early: I INFOS, II ADÉQUATION, III PARCOURS
   (chrono order, DRQC last), IV COMPÉTENCES (added IFRS/OHADA), V ÉTUDES, VI FORMATIONS
   (added IFRS), VII LANGUES, VIII RÉFÉRENCES (4 refs, compact lh=5).
4. **2-page fit:** after adding photo + Adéquation the CV hit 3 pages. Fixed orphan-word
   spill (see SKILL.md §5 pitfall) by para lh 6→5.5, ln(1)→ln(0.5), ref lh 6→5.
5. **Signature block** right-aligned: "Fait à Kinshasa…" + "Signature :" + "KAKESA MUDIMBA
   Dieudonné" (serment stays left).

Application specifics captured from the form:
- Email: `CD-Recrutement@kpmg.com`
- Filename MUST be: `CV_Nom&Prénom_AD Audit` → rename output to `CV_KAKESA_MUDIMBA_AD Audit.pdf`
- Deadline: 27/07/2026
- The MS Forms page is NOT the CV submission channel — email the dossier; the form is a
  separate info form to validate ("Suivant" button).
