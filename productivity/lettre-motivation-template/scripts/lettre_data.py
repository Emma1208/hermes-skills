# -*- coding: utf-8 -*-
"""Donnees d'une LETTRE DE MOTIVATION (template reutilisable).
Structure inspiree du modele RDC classique : expediteur (gauche),
date + destinataire (droite), Objet, corps, formule de politesse, signature.
>> Pour une nouvelle candidature, remplis les champs ci-dessous puis lance
   make_lettre_pdf.py et make_lettre_docx.py (le .tex est pret a compiler).
Les valeurs ci-dessous sont un EXEMPLE (identite KAKESA) a remplacer.
"""
LETTRE = {
    # ---- Expéditeur (haut gauche) = identité KAKESA ----
    "expediteur": {
        "nom": "KAKESA MUDIMBA Emmanuel-Dieudonné",
        "adresse": "N° 3, AV. TUNGILA, Q/ BIANDA, C/ MONT NGAFULA",
        "tel": "Tel : +243 81 849 16 01",
        "email": "Email : kakesamudimba@gmail.com",
    },
    # ---- Date / Lieu (haut droite) ----
    "date_lieu": "Kinshasa, 06 / 09 / 2025",
    # ---- Destinataire (haut droite) ----
    "destinataire": {
        "ligne1": "A Monsieur le Directeur des Ressources",
        "ligne2": "Humaines de DELOITTE RDC",
        "ligne3": "KINSHASA / GOMBE",
    },
    # ---- Salutation ----
    "salutation": "Monsieur le Directeur,",
    # ---- Objet ----
    "objet": "Candidature au poste de Stagiaire ADVISORY / CONSEIL",
    # ---- Corps (liste de paragraphes) ----
    "corps": [
        "Par la présente, j'ai l'honneur de soumettre ma candidature au poste "
        "susmentionné au sein de votre honorable structure.",
        "Titulaire d'une Licence en Sciences économiques et de gestion, option "
        "Gestion Financière, de l'Université de Kinshasa, je nourris un vif "
        "intérêt pour les domaines du Conseil, de la Finance et de la Comptabilité.",
        "Mon parcours académique ainsi qu'un stage effectué à la Direction de "
        "l'Audit et du Contrôle de Gestion du ministère des Finances m'ont permis "
        "d'appréhender les notions d'Audit, de Finance et de Comptabilité. Je suis "
        "confiant quant à la maîtrise des compétences requises pour le poste.",
        "Travailleur acharné, déterminé et esprit d'équipe, je suis en mesure "
        "d'apporter une contribution significative en tant que stagiaire ADVISORY. "
        "L'esprit d'innovation et de dynamisme qui caractérise DELOITTE m'attire "
        "tout particulièrement.",
        "Je vous remercie de l'attention accordée à ma candidature et me tiens à "
        "votre entière disposition pour tout complément d'information. Vous trouverez "
        "ci-joint mon curriculum vitae.",
    ],
    # ---- Formule de politesse (1 ligne : suite directe après la virgule) ----
    "formule": [
        "Je vous prie d'agréer, Monsieur le Directeur, l'assurance de ma considération distinguée.",
    ],
    # ---- Signature (nom dactylographié) ----
    "signature_nom": "KAKESA MUDIMBA Emmanuel-Dieudonné",
    # ---- Signature manuscrite (image optionnelle, None pour désactiver) ----
    "signature_image": None,   # ex: "/root/lettre_motivation/signature.png"
    # ---- Photo d'identité (optionnelle, None pour désactiver ; pour assortir au CV) ----
    "photo": None,             # ex: "/root/cv_kakesa/photo_kakesa.jpg"
}
