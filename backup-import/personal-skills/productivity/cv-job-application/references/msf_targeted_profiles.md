# MSF targeted profiles (Cuisinier, Agent d'entretien, support staff)

The user (KAKESA MUDIMBA) has real MSF experience: **Agent d'appui logistique, projet PUC MED de MSF**
(depuis nov. 2023) — suivi de stock, chaîne du froid, hygiène, sécurité, conformité. This is the
strongest asset for MSF support-staff posts and MUST be surfaced even though his degree is in
finance/accounting.

## Reusable angle per post
- **Cuisinier·ère réserviste:** lead with PUC MED → stock alimentaire, chaîne du froid, hygiène;
  add an "Atouts pour le poste" section (hygiène, contrôle stock, ponctualité, FR/Lingala for
  cultural menus, connaissance MSF). Keep DRH MSF reference.
- **Agent d'entretien:** lead with PUC MED → hygiène, entretien des locaux, signalement
  d'incidents; "Compétences clés" = nettoyage/désinfection, déchets, inventaire, manutention,
  sécurité; "Atouts" = connaissance MSF, protocoles, langues, flexibilité réserviste, discrétion.
- MSF offer contact seen on postings: `MSFCH-RDC-DH@dub.geneva.msf.org` (verify per live offer).

## Layout notes
- CV may be 2 pages when the user asks (see SKILL.md 2-page override). Split: p1 = identité +
  parcours + compétences clés; p2 = atouts + études + langues + centres d'intérêt + références +
  signature.
- Letter: official 100mm-block format; addressee "Madame, Monsieur le Responsable (des RH)",
  KINSHASA / GOMBE; closing formula placed per the user's explicit instruction (verify with
  `page.get_text('words')` coordinates, not vision alone).
- This session's generator scripts (in /root/linkedin_app/):
  `generate_cv_cuisinier.py`, `generer_lettre_cuisinier.py`,
  `generate_cv_agent_entretien.py`, `generer_lettre_agent_entretien.py`.
- Outputs: `CV_KAKESA_MUDIMBA_Cuisinier.pdf`, `Lettre_Motivation_Cuisinier.pdf`,
  `CV_KAKESA_MUDIMBA_AgentEntretien.pdf`, `Lettre_Motivation_AgentEntretien.pdf`.
