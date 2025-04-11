import mysql.connector
import socket

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",      # Adresse du serveur MySQL
            user="root",          # Utilisateur local
            password="",          # Pas de mot de passe en local
            database="bdoor"      # Base de données cible
        )
        return conn
    except mysql.connector.Error as err:
        print("❌ Erreur de connexion à la base de données :", err)
        return None

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connexion pour récupérer l'IP locale
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print("❌ Erreur lors de la récupération de l'adresse IP :", e)
        return "0.0.0.0"

def upsert_device(conn, ip, hostname):
    try:
        cursor = conn.cursor()

        # Vérifier si le nom existe déjà
        check_query = "SELECT id FROM devices WHERE nom = %s"
        cursor.execute(check_query, (hostname,))
        existing_device = cursor.fetchone()

        if existing_device:
            # Mettre à jour l'adresse IP si le nom existe
            update_query = "UPDATE devices SET ip = %s WHERE nom = %s"
            cursor.execute(update_query, (ip, hostname))
            print(f"✅ Adresse IP mise à jour : Nom = {hostname}, IP = {ip}")
        else:
            # Insérer un nouvel enregistrement si le nom n'existe pas
            insert_query = "INSERT INTO devices (nom, ip) VALUES (%s, %s)"
            cursor.execute(insert_query, (hostname, ip))
            print(f"✅ Nouvelle entrée ajoutée : Nom = {hostname}, IP = {ip}")

        conn.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print("❌ Erreur lors de l'upsert des données :", err)

def main():
    conn = connect_to_database()
    if not conn:
        return

    # Récupération des informations
    hostname = socket.gethostname()  # Nom de la machine
    local_ip = get_local_ip()        # Adresse IP locale

    # Mise à jour ou insertion des informations dans la table devices
    upsert_device(conn, local_ip, hostname)

    # Fermeture de la connexion
    close_connection(conn)

def close_connection(conn):
    if conn:
        conn.close()
        print("✅ Connexion fermée.")

if __name__ == "__main__":
    main()