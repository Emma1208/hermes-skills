---
name: github-skills-backup
description: Back up ALL Hermes Agent skills (or a specific skill/template) to a GitHub repo for inter-session persistence. Covers clone-vs-API-push choice, default branch 'main' pitfall, clone-approval gate, token hygiene, and excluding caches. Use when the user asks to "save my skills/competences between sessions on GitHub" or wants durable persistence of skills/templates.
---

# GitHub Skills Backup (persistance inter-session)

Sauvegarde les skills Hermes Agent sur GitHub pour qu'ils survivent entre les
sessions. Classe de travail récurrente : l'utilisateur (compte `Emma1208`) a
explicitement demandé que « toutes les compétences soient sauvegardées entre
session sur GitHub ».

## Quand utiliser
- « sauvegarde tout mes skills / compétences sur GitHub »
- « mets à jour le template sur le repository GitHub »
- Persistance durable de skills/templates (cv, lettre, etc.)

## Recette (méthode git classique — PRÉFÉRÉE par l'utilisateur)
1. `export GITHUB_TOKEN='ghp_...'` (token classic, scope `repo`). JAMAIS écrit
   dans un fichier commité/relu, JAMAIS en mémoire Hermes.
2. `rm -rf /root/<repo>-push && git clone "https://Emma1208:${GITHUB_TOKEN}@github.com/Emma1208/<repo>.git" /root/<repo>-push`
3. Copier le contenu : `cp -r /root/.hermes/skills/. /root/<repo>-push/` (ou
   juste les skills visés). Nettoyer : `find /root/<repo>-push -name __pycache__ -type d -exec rm -rf {} + ; find ... -name '*.pyc' -delete`.
4. `cd /root/<repo>-push && git add -A && git commit -m "..." && git push -u origin main`
5. `unset GITHUB_TOKEN` (purge obligatoire).

## Alternative : push via API (sans clone)
Si le clone est bloqué/refusé, on peut PUT chaque fichier via l'API
(`PUT /repos/Emma1208/<repo>/contents/<path>` avec `content` = base64,
`sha` si existe déjà). Plus léger, pas de git local. Réservé au blocage du clone.

## PITFALLS (rencontrés en session réelle)
- ❌ `git push origin master` échoue (« src refspec master does not match ») :
  l'API GitHub crée la branche **`main`** par défaut, PAS `master`. Toujours
  `git push -u origin main` (ou `git branch` pour vérifier avant).
- ❌ `git clone` peut être BLOQUÉ (gate d'approbation du runtime) → timeout.
  Ne PAS relancer tel quel. Proposer l'alternative API, ou redemander le feu
  vert. Un clone précédent ayant expiré, la 2e tentative avec accord a réussi.
- ❌ Token dans un fichier du dépôt (ex. `.env`, script commité) → fuite.
  Passer uniquement via variable d'environnement shell, `unset` après push.
- ❌ Pousser le skill local `~/.hermes/skills/*` SANS resync depuis
  `/root/...` : le skill est une COPIE souvent périmée. Avant push, copier les
  fichiers de vérité (`/root/cv_kakesa/`, `/root/lettre_motivation/`) vers le
  dossier du dépôt. Voir skills `cv-master-template` / `lettre-motivation-template`
  (section Sauvegarde/GitHub).
- ⚠️ Vérifier CÔTÉ DÉPÔT après push (API raw ou `curl .../contents`) que les
  corrections sont bien présentes (ex. `grep` sur le fichier brut) — ne pas se
  fier au seul `push OK` local.

## Dépôts de référence (compte Emma1208)
- `cv-lettre-templates` : templates CV + lettre (+ variante-enseignant).
- `hermes-skills` : backup complet de tous les skills Hermes Agent (76 skills).
Détail des commandes et vérifications dans `references/workflow.md`.
