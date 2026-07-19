KAKESA MUDIMBA Emmanuel-Dieudonné — Congolais basé à Kinshasa (Mont Ngafula, Av. Tungila). Profil : professeur de comptabilité/cours commerciaux (complexe scolaire sagesse2, Minga la Paix), agent d'appui logistique au projet PUC MED de MSF (Médecins sans frontières), ancien analyste Forex. Licencié en Sciences économiques et de gestion, option Gestion Financière, Université de Kinshasa. Contact : kakesamudimba@gmail.com, +243 818 491 601.
§
Templates CV + lettre versionnés GitHub (compte Emma1208, dépôt public Emma1208/cv-lettre-templates, contient skills cv-master-template + lettre-motivation-template + README). Identité KAKESA, palette navy 1F3364, 3 formats (PDF/DOCX/LaTeX). CV base /root/cv_kakesa/, lettre /root/lettre_motivation/. Structure lettre validée : expéditeur (nom gauche + date même ligne droite), destinataire dessous à droite aligné gauche, Concerne (largeur=bloc expéditeur 95mm, retour auto), Salutation SOUS Concerne, signature TOUTE à droite. Toujours corriger accents avant génération.
§
CONVENTION: message 'S' (majuscule seule) = sauvegarde auto GitHub skills+mémoire via /root/.hermes/scripts/backup_skills_memory.py (dépôt Emma1208/hermes-skills, branche main). Exécuter sans redemander. Token via env GITHUB_TOKEN (jamais en clair).
§
Termux PRoot Py3.14 ARM musl: Pillow broken -> reportlab/docx/lxml unusable. PDF via fpdf2+DejaVu TTF; DOCX hand-written OOXML zip. ⮚->► en PDF seulement.
§
User demands one-command-at-a-time on Termux: send a single command, wait for their output, then next. No batched sequential commands to await.
§
Termux: proot-distro 5.4.1 EST l'officiel (réécrit Python, tire images Docker/OCI, plus le script shell 4.x). 'install void' échoue (Unauthorized) car il faut le nom d'image Docker complet. Void OK via: proot-distro install ghcr.io/void-linux/void-glibc-full:latest --name void. Si 'Layer integrity check failed' -> proot-distro clear-cache puis relancer. Void=gestionnaire xbps.