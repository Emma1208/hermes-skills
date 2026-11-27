import os
import shutil
import time
import subprocess
import tarfile
from datetime import datetime

def envoyer_notification(titre, message):
    subprocess.run(["termux-notification", "--title", titre, "--content", message])

def organiser_et_nettoyer():
    base_path = "/data/data/com.termux/files/home"
    compteur = 0
    # Dossiers cibles
    extensions = {
        'Scripts': ['.py', '.sh', '.js'],
        'Documents': ['.txt', '.pdf'],
        'Images': ['.jpg', '.png']
    }
    
    # On scanne les fichiers
    for f in os.listdir(base_path):
        chemin_f = os.path.join(base_path, f)
        # On ignore les dossiers et le script lui-même
        if os.path.isfile(chemin_f) and f != 'organizer_v2.py' and f != 'app.py':
            _, ext = os.path.splitext(f)
            for dossier, ext_list in extensions.items():
                if ext.lower() in ext_list:
                    dest = os.path.join(base_path, dossier)
                    if not os.path.exists(dest): os.makedirs(dest)
                    shutil.move(chemin_f, os.path.join(dest, f))
                    compteur += 1
                    break
    return compteur

def executer_sauvegarde():
    base_path = "/data/data/com.termux/files/home"
    source = os.path.join(base_path, "Scripts")
    dest_folder = os.path.join(base_path, "Archives")
    
    if not os.path.exists(dest_folder): os.makedirs(dest_folder)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    nom_archive = f"backup_scripts_{date_str}.tar.gz"
    chemin_final = os.path.join(dest_folder, nom_archive)

    if os.path.exists(source) and os.listdir(source):
        with tarfile.open(chemin_final, "w:gz") as tar:
            tar.add(source, arcname="Scripts")
        return nom_archive
    return None

if __name__ == "__main__":
    try:
        nb = organiser_et_nettoyer()
        bkp = executer_sauvegarde()
        
        resultat = f"{nb} fichiers rangés."
        if bkp:
            resultat += f" Backup créé : {bkp}"
            
        envoyer_notification("✅ Robot Termux", resultat)
        print(f"✨ Terminé : {resultat}")
    except Exception as e:
        envoyer_notification("❌ Erreur Robot", str(e))
        print(f"Erreur : {e}")

