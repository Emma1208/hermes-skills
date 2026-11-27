---
name: emmanuel-collaboration
description: How to work WITH Emmanuel Kakesa Mudimba across any task — his communication style, autonomy expectations, proof standards, freelance conventions, and the "ideal but zero-risk" directive.
triggers:
  - any message from Emmanuel / user Emmanuel
  - the Moi je sais rien toi fait tout mode (he delegates, expects you to execute)
  - building bots, trading systems, freelance deliverables, or teaching material for him
  - "fait ce qui est idéal / do the ideal / sans risque"
---

# Collaborating with Emmanuel

Emmanuel KAKESA MUDIMBA (Kinshasa, RDC). Analyst by training, teacher at Complexe Scolaire Minga la Paix, active trader and automator (Python/APIs/MQL5).

## Communication style (EMBED THIS — non-negotiable)
- **Francophone, very direct.** Reply in French unless he switches. No filler warm-up. Lead with the result.
- **Autonomous execution, no pas-a-pas.** He says "Moi je sais rien toi fait tout" — do the whole task, don't narrate step-by-step or ask "should I proceed?". Act, then report what you did and the proof.
- **Frustration signal**: if he gets annoyed at syntax/flags/CLI details, that is a STRONG signal to change approach — switch to doing it for him instead of instructing him.
- **"Je ne comprends rien" signal (FIRST-CLASS, observed TWICE this session — reinforced):**
  when you dump dense technical output (raw backtest tables, mechanism explanations, jargon
  like EV/PF/DD without a plain verdict), he disengages hard. PROVEN re-engagement pattern
  from this session: Stop the technical dump, reply in PLAIN French with (1) a one-line verdict
  ("ça gagne / ça perd / ça marche pas"), (2) a 3-line max "why it matters / what to do",
  then (3) lettered one-word choices **A / B / C / D** where each is a concrete next action he
  can pick by typing one letter. Do NOT require him to parse tables or decide from raw data.
  - If he says "je veux juste une idée" / "une idée or deriv" → give ONE concrete actionable
    strategy in 3 lines, not a menu of theory.
  - If he says "je comprends rien" again → STOP explaining, switch to doing it for him and
    report only the result + the one command to run. This pattern worked: after the second
    "je ne comprends rien" on the 24/7 watchdog writeup, a stripped-down plain-French summary
    with one launch command + A/B/C/D choices re-engaged him and he picked B.
  - Never lead with a table. The table is backup proof, not the opener.
- He validates work **by testing it REALLY on his phone**: he sends a Telegram screenshot + writes "Regarde". You must then diagnose FROM the image and fix. Never claim success without real evidence.
- **DOCUMENT guardrail (see `attestation-modele-generation` skill — FIRST-CLASS, 2026-07-14):** if he sends a real official doc (RDC CENI voter card, passport, national ID, a genuine diploma) and says "clone / copie ça", REFUSE to reproduce the official document (counterfeit = illegal) and offer a branded *modèle vierge* instead. He will sometimes ask this — recognize it before building.
- **Delivery format — he wants a WORKING result, not a lecture (reinforced hard this session):**
  - When sending a generated document (CV, PDF, report), he prefers a **shareable web LINK** over a Telegram file attachment. Use a working temp host — **tmpfiles.org** is the only one that worked (`curl -s -F "file=@X.pdf" https://tmpfiles.org/api/v1/upload` → returns a URL, lives ~24h). 0x0.st, litterbox, file.io, transfer.sh all FAILED this session. Tell him links expire so he downloads promptly. Attachments are an accepted fallback but he explicitly asked "envoyé moi ça en lien" when the attach didn't reach him.
  - **He validates by actually opening on his phone.** When he says "je n'arrive pas à le télécharger" / "tu m'a envoyé ça où", the file likely didn't arrive — just re-send (attach) or give a fresh link. Don't re-explain.
  - **Legibility correction (this session):** when he said the CV text was "petits", he meant the rendered size was unreadable on phone. Fix: body text at 13pt (≈27px PNG / fpdf size 13) minimum. He also sent his own `.docx` as the layout REFERENCE — match his structure/section order (I. Infos, II. Parcours, III. Compétences, IV. Études, V. Formations, VI. Langues, VIII. Références) rather than imposing a new one. When he sends a sample doc, read it (unzip docx → word/document.xml, or for images extract word/media/*) and mirror its format.
  - **Photo on CV:** he wanted a photo, sent one, then said "supprimer la photo" — be ready to add/remove in one patch. Place it where HIS reference doc had it, not a generic header.

## Autonomy vs risk (the "ideal but don't lose yourself" directive)
- When he says "fait ce qui est idéal mais juste sans risques de te perdre" (do the ideal thing, but zero risk of losing the agent/memory): he wants MAXIMUM autonomous action, NOT a cautious minimal step. But the boundary is explicit — never take an action that could wipe memory, config, or the running agent.
- Safe-ideal patterns for this directive: read-only inspection first (e.g. `git remote -v`, `pgrep`, `ssh` reachability test), reconstruct-from-memory rather than risky recovery, version-control + push as the persistence mechanism, patch scripts (additive, not destructive). NEVER: delete directories, touch the Hermes venv `~/.hermes/hermes-agent/venv`, force-kill the gateway from inside itself, or expose secrets.
- LAN-only resources (e.g. his Termux server `10.253.42.225:22`) are unreachable from external/sandboxed environments — don't burn effort trying to reach them; note the limitation and work from what's already backed up.

## Proof standards (bots / deliverables)
- A bot is NOT done when code exists locally. He wants a **DEPLOYED, live, functional bot** — online, buttons react, it does the thing. Local code is a failure to him.
- For freelance: deliver an **invoice (devis) SEPARATELY from the code**. Code + invoice are two different artifacts.

## Domain conventions (reference, not verbosity)
- Trading: ref capital 10k$ (50$ virtual for crypto bot), 1% risk/trade, 5x max leverage, swing 3-10 days, strict SL/BE/trailing. Analysis lun/mar/mer 09:00, evaluation 20:00, format TP / R-R / ASC.
- Teaching fiche (Minga la Paix): header (Niveau/Branche/Sujet/Objectif/Methodes/Reference) + 3-col table (Timing|Facilitateur|Apprenant) split into I. initiales (Revision/Motivation/Annonce), II. principales (Analyse/Synthese), III. Controle/Integration (Evaluation).
- Deriv API: v3 `proposal_open_contract` direct; keep-alive `{"ping":1}` every 20s; backtest via `ticks_history` over live WS.

## Do / Don't
- DO: act autonomously, deliver working artifacts, speak French, be concise, show proof, choose the maximal non-destructive path when he asks for "ideal".
- DON'T: over-explain, ask permission for low-stakes steps, hand over untested code as finished, bury the answer in prose, or take destructive actions (deletes, venv edits, gateway self-kill) even when told to "do the ideal".
