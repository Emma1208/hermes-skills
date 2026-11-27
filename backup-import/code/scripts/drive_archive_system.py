#!/usr/bin/env python3
"""
Système d'archivage intelligent pour Google Drive
Organise, nettoie et structure vos documents selon une méthodologie PARA adaptée
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
HOME = Path.home()
TOKEN_PATH = HOME / ".config" / "google-drive-mcp" / "tokens.json"
CREDENTIALS_PATH = HOME / ".config" / "google-drive-mcp" / "gcp-oauth.keys.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
]

# Structure d'archivage PARA adaptée pour votre cas (Finance/Enseignement/Trading)
ARCHIVE_STRUCTURE = {
    "00_ADMINISTRATION": {
        "description": "Documents administratifs, légaux, identité",
        "subfolders": {
            "00_Identité": "Pièces d'identité, passeport, actes de naissance",
            "01_Banque_Assurance": "Relevés, contrats, assurances",
            "02_Impôts_Fiscalité": "Déclarations, avis, correspondance fiscale",
            "03_Juridique_Contrats": "Baux, contrats travail, mandats",
            "04_Santé": "Dossiers médicaux, mutuelle, ordonnances",
            "05_Véhicule_Logement": "Carte grise, assurance auto, factures logement",
        }
    },
    "01_PROJETS": {
        "description": "Projets actifs avec date de fin (cours, trading, développements)",
        "subfolders": {
            "00_Enseignement": "Préparation cours, supports, évaluations",
            "01_Trading_Investissement": "Journaux de trade, analyses, stratégies",
            "02_Bot_Telegram_Finance": "Code, docs, déploiement du bot éducatif",
            "03_Automatisation_MQL5_Python": "Scripts, EAs, backtests",
            "04_Recherche_Marchés": "Analyses sectorielles, veille concurrentielle",
        }
    },
    "02_CLIENTS": {
        "description": "Dossiers clients/étudiants (anonymisés si nécessaire)",
        "subfolders": {
            "00_Étudiants_Comptabilité": "Listes, notes, suivi par classe",
            "01_Clients_Conseil_Financier": "Mandats, rapports, correspondance",
            "02_Administration_Scolaire": "Emplois du temps, programmes, réunions",
        }
    },
    "03_RESSOURCES": {
        "description": "Références, templates, connaissances réutilisables",
        "subfolders": {
            "00_Templates_Documents": "Modèles factures, contrats, rapports, cours",
            "01_Formations_Certifications": "Diplômes, attestations, MOOCs terminés",
            "02_Veille_Finance_Trading": "Articles, PDFs, notes de lecture classées",
            "03_Outils_Scripts_Utiles": "Snippets code, config, raccourcis",
            "04_Références_Réglementation": "CGI, PCG, normes IFRS, loi OHADA RDC",
            "05_Bibliothèque_Personnelle": "Livres, papers, résumés personnels",
        }
    },
    "04_ARCHIVES": {
        "description": "Projets terminés, anciens documents, historique",
        "subfolders": {
            "00_Anciens_Cours": "Supports des années précédentes",
            "01_Anciens_Projets_Trading": "Journaux, analyses closes",
            "02_Candidatures_Emploi": "LM, CV, réponses (archivées par date)",
            "03_Examens_Concours_Passés": "Sujets, copies, corrections",
            "04_Documents_Obsolètes": "Anciens contrats, factures > 7 ans",
            "05_Brouillons_Non_Classés": "Documents sans titre, imports temporaires",
        }
    },
    "05_CORBEILLE_INTELLIGENTE": {
        "description": "Zone de transit avant suppression définitive (30 jours)",
        "subfolders": {
            "À_Trier_Urgemment": "Nouveaux arrivants non classés",
            "Doublons_Suspects": "Fichiers potentiellement dupliqués",
            "Anciens_Non_Ouverts_1an": "Fichiers non modifiés depuis 1 an",
        }
    }
}

# Règles de classification automatique basées sur les noms de fichiers
CLASSIFICATION_RULES = [
    # Examens/Concours (très prioritaire)
    (r"(examen|exam|concours|épreuve|sujet|correction)", "04_ARCHIVES/03_Examens_Concours_Passés"),
    (r"(partiel|session|rattrapage)", "04_ARCHIVES/03_Examens_Concours_Passés"),
    
    # Candidatures
    (r"(LM_|lettre.*motivation|cover.*letter|lettre.*motiv)", "04_ARCHIVES/02_Candidatures_Emploi"),
    (r"(CV_|curriculum|resume|c\.v\.)", "04_ARCHIVES/02_Candidatures_Emploi"),
    
    # Enseignement - cours, exercices, matières
    (r"(comptabilité|gestion|finance|droit|économie|math|statistique|algèbre|géométrie|arithmétique|fiscalité|docom|activité.*complémentaire).*?(cours|examen|exercice|devoir|évaluation|td|tp)", "01_PROJETS/00_Enseignement"),
    (r"(cours|td|tp|exercice|devoir|évaluation|note|préparation).*\d{4}", "01_PROJETS/00_Enseignement"),
    
    # Trading/Finance
    (r"(trade|trading|position|journal|backtest|strategie|stratégie).*\d{4}", "01_PROJETS/01_Trading_Investissement"),
    (r"(analyse|market|marché|forex|crypto|matières.*premières|finance.*marché|analyse.*financière|exercice.*analyse.*financière)", "01_PROJETS/01_Trading_Investissement"),
    (r"(gestion.*financière|finances.*publiques|contrôle.*gestion|audit|prévision|budget|cash.*flow)", "01_PROJETS/01_Trading_Investissement"),
    
    # Bot/Dev
    (r"(bot|telegram|python|mql5|script|automatisation|programmation)", "01_PROJETS/02_Bot_Telegram_Finance"),
    
    # Administratif
    (r"(facture|relevé|banque|assurance|impôt|fiscal|avis.*imposition|fiscalité|prévisions.*fiscal)", "00_ADMINISTRATION/01_Banque_Assurance"),
    (r"(contrat|bail|mandat|procuration|procès-verbal)", "00_ADMINISTRATION/03_Juridique_Contrats"),
    (r"(identité|passeport|carte.*identité|acte.*naissance)", "00_ADMINISTRATION/00_Identité"),
    
    # Ressources
    (r"(template|modèle|modèle.*facture|modèle.*contrat|modèle\s+\d+)", "03_RESSOURCES/00_Templates_Documents"),
    (r"(diplôme|attestation|certificat|formation|MOOC|relevé.*cote|relevé.*note)", "03_RESSOURCES/01_Formations_Certifications"),
    (r"(réglementation|CGI|PCG|IFRS|OHADA|loi|code.*général.*impôts|droit.*travail)", "03_RESSOURCES/04_Références_Réglementation"),
    (r"(mémoire|thèse|rapport|ministère|livre|manuel|encyclopédie| dictionnaire)", "03_RESSOURCES/05_Bibliothèque_Personnelle"),
    
    # Doublons/Untitled/Autres
    (r"^(document sans titre|untitled|nouveau document|copy of|copie de|feuille de calcul sans titre)", "05_CORBEILLE_INTELLIGENTE/À_Trier_Urgemment"),
    (r"^\d+$", "05_CORBEILLE_INTELLIGENTE/À_Trier_Urgemment"),  # Noms numériques uniquement
    (r"^(Z\.|AC[0-9]|IMG_|DOC-|AUD-|mot secret|Listing|où est|en prenant|Classe moi|Cartographie|Partager)", "05_CORBEILLE_INTELLIGENTE/À_Trier_Urgemment"),
    
    # Fichiers Google Keep, images anciennes
    (r"(Google\s*Keep|IMG_\d{8})", "05_CORBEILLE_INTELLIGENTE/Anciens_Non_Ouverts_1an"),
    
    # Derniers cas spécifiques non classés
    (r"(mémoire|thèse).*(kakese|mudimba)", "03_RESSOURCES/05_Bibliothèque_Personnelle"),
    (r"(fiche|préparation)", "01_PROJETS/00_Enseignement"),
    (r"(annuaire|églises|partis|hôpitaux|cartographie)", "03_RESSOURCES/02_Veille_Finance_Trading"),
    (r"(déontologie|éthique)", "03_RESSOURCES/04_Références_Réglementation"),
    (r"(prévision|prevision).*(ecodev|entreprenariat|math\.fin|math appli)", "01_PROJETS/00_Enseignement"),
    (r"(financement.*pme|pme)", "01_PROJETS/01_Trading_Investissement"),
    (r"(math.*appliq|ecopol|exercice.*analyse)", "01_PROJETS/01_Trading_Investissement"),
    (r"(dunod|toute la fonction finance)", "03_RESSOURCES/05_Bibliothèque_Personnelle"),
    (r"(partager|comptabilité.*kakese)", "01_PROJETS/00_Enseignement"),
    
    # Derniers cas résiduels
    (r"mémoire.*kakese.*mudimba", "03_RESSOURCES/05_Bibliothèque_Personnelle"),
    (r"prévision.*entreprenariat", "01_PROJETS/00_Enseignement"),
    (r"gestion.*financière.*prof.*nsuami", "01_PROJETS/00_Enseignement"),
]


class DriveArchiver:
    def __init__(self):
        self.service = None
        self.folder_ids = {}  # Cache des IDs de dossiers créés
        self.stats = {
            "files_moved": 0,
            "folders_created": 0,
            "errors": 0,
            "classified": {},
            "unclassified": []
        }
    
    def authenticate(self):
        """Authentifie avec les tokens existants"""
        with open(TOKEN_PATH) as f:
            token_data = json.load(f)
        
        with open(CREDENTIALS_PATH) as f:
            cred_data = json.load(f)["installed"]
        
        creds = Credentials(
            token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cred_data["client_id"],
            client_secret=cred_data["client_secret"],
            scopes=SCOPES
        )
        
        self.service = build("drive", "v3", credentials=creds)
        print("✅ Authentifié sur Google Drive API")
        return True
    
    def get_folder_id(self, name, parent_id=None):
        """Récupère ou crée un dossier, retourne son ID"""
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name)"
        ).execute()
        
        folders = results.get("files", [])
        if folders:
            return folders[0]["id"]
        
        # Créer le dossier
        folder_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_id:
            folder_metadata["parents"] = [parent_id]
        
        folder = self.service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()
        
        self.stats["folders_created"] += 1
        print(f"  📁 Créé: {name} (ID: {folder['id']})")
        return folder["id"]
    
    def setup_structure(self):
        """Crée toute la structure d'archivage"""
        print("\n🏗️  Création de la structure d'archivage...")
        
        # Dossiers principaux à la racine
        for main_folder, config in ARCHIVE_STRUCTURE.items():
            main_id = self.get_folder_id(main_folder)
            self.folder_ids[main_folder] = main_id
            
            # Sous-dossiers
            for sub_name, sub_desc in config["subfolders"].items():
                sub_id = self.get_folder_id(sub_name, main_id)
                self.folder_ids[f"{main_folder}/{sub_name}"] = sub_id
        
        print(f"✅ Structure créée ({self.stats['folders_created']} dossiers)")
    
    def list_root_files(self):
        """Liste tous les fichiers à la racine (non dans un dossier)"""
        query = "'root' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
        results = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, mimeType, modifiedTime, size, parents)",
            pageSize=1000
        ).execute()
        return results.get("files", [])
    
    def classify_file(self, file_name):
        """Détermine le dossier cible basé sur le nom du fichier"""
        name_lower = file_name.lower()
        
        for pattern, target_path in CLASSIFICATION_RULES:
            if re.search(pattern, name_lower, re.IGNORECASE):
                return target_path
        
        # Par extension
        if name_lower.endswith((".pdf", ".doc", ".docx")):
            if any(kw in name_lower for kw in ["cv", "curriculum", "resume", "lettre", "motivation"]):
                return "04_ARCHIVES/02_Candidatures_Emploi"
            if any(kw in name_lower for kw in ["mémoire", "thèse", "rapport", "ministère"]):
                return "03_RESSOURCES/05_Bibliothèque_Personnelle"
        
        return None
    
    def move_file(self, file_id, file_name, target_folder_path):
        """Déplace un fichier vers le dossier cible"""
        target_id = self.folder_ids.get(target_folder_path)
        if not target_id:
            print(f"  ⚠️  Dossier cible introuvable: {target_folder_path}")
            self.stats["errors"] += 1
            return False
        
        try:
            # Récupérer les parents actuels
            file_info = self.service.files().get(
                fileId=file_id,
                fields="parents"
            ).execute()
            
            previous_parents = ",".join(file_info.get("parents", []))
            
            # Déplacer
            self.service.files().update(
                fileId=file_id,
                addParents=target_id,
                removeParents=previous_parents,
                fields="id, parents"
            ).execute()
            
            self.stats["files_moved"] += 1
            category = target_folder_path.split("/")[0]
            self.stats["classified"][category] = self.stats["classified"].get(category, 0) + 1
            print(f"  ✅ {file_name} → {target_folder_path}")
            return True
            
        except HttpError as e:
            print(f"  ❌ Erreur déplacement {file_name}: {e}")
            self.stats["errors"] += 1
            return False
    
    def find_duplicates(self, files):
        """Détecte les doublons potentiels par nom/taille"""
        seen = {}
        duplicates = []
        
        for f in files:
            key = (f["name"].lower(), f.get("size", 0))
            if key in seen:
                duplicates.append((f, seen[key]))
            else:
                seen[key] = f
        
        return duplicates
    
    def run_archive(self, dry_run=False):
        """Lance le processus d'archivage complet"""
        print("=" * 60)
        print("🚀 DÉMARRAGE DU SYSTÈME D'ARCHIVAGE GOOGLE DRIVE")
        print("=" * 60)
        
        if not self.authenticate():
            return
        
        # 1. Créer la structure
        self.setup_structure()
        
        # 2. Lister fichiers racine
        print("\n📋 Scan des fichiers à la racine...")
        root_files = self.list_root_files()
        print(f"   {len(root_files)} fichiers trouvés à la racine")
        
        # 3. Détecter doublons
        duplicates = self.find_duplicates(root_files)
        if duplicates:
            print(f"\n🔍 {len(duplicates)} paires de doublons détectées")
            for dup, orig in duplicates[:5]:
                print(f"   - {dup['name']} (ID: {dup['id']}) ← doublon de {orig['name']}")
                if not dry_run:
                    self.move_file(dup["id"], dup["name"], "05_CORBEILLE_INTELLIGENTE/Doublons_Suspects")
        
        # 4. Classifier et déplacer
        print("\n📦 Classification et archivage...")
        for file in root_files:
            target = self.classify_file(file["name"])
            
            if target:
                if not dry_run:
                    self.move_file(file["id"], file["name"], target)
                else:
                    print(f"  [DRY-RUN] {file['name']} → {target}")
                    self.stats["classified"][target.split("/")[0]] = self.stats["classified"].get(target.split("/")[0], 0) + 1
            else:
                self.stats["unclassified"].append(file["name"])
                if not dry_run:
                    # Déplacer vers zone de tri
                    self.move_file(file["id"], file["name"], "05_CORBEILLE_INTELLIGENTE/À_Trier_Urgemment")
                else:
                    print(f"  [DRY-RUN] {file['name']} → 05_CORBEILLE_INTELLIGENTE/À_Trier_Urgemment (non classé)")
        
        # 5. Rapport final
        self.print_report()
    
    def print_report(self):
        print("\n" + "=" * 60)
        print("📊 RAPPORT D'ARCHIVAGE")
        print("=" * 60)
        print(f"📁 Dossiers créés: {self.stats['folders_created']}")
        print(f"📄 Fichiers déplacés: {self.stats['files_moved']}")
        print(f"❌ Erreurs: {self.stats['errors']}")
        print(f"\n📂 Répartition par catégorie:")
        for cat, count in sorted(self.stats["classified"].items()):
            print(f"   {cat}: {count} fichiers")
        print(f"\n❓ Non classés (dans À_Trier_Urgemment): {len(self.stats['unclassified'])}")
        if self.stats["unclassified"][:10]:
            for f in self.stats["unclassified"][:10]:
                print(f"   - {f}")
            if len(self.stats["unclassified"]) > 10:
                print(f"   ... et {len(self.stats['unclassified']) - 10} autres")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Système d'archivage Google Drive")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans modifications")
    parser.add_argument("--setup-only", action="store_true", help="Crée seulement la structure")
    args = parser.parse_args()
    
    archiver = DriveArchiver()
    
    if args.setup_only:
        archiver.authenticate()
        archiver.setup_structure()
        print("✅ Structure créée. Lancez sans --setup-only pour archiver.")
    else:
        archiver.run_archive(dry_run=args.dry_run)

if __name__ == "__main__":
    main()