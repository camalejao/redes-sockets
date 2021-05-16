import socket

client_socket = socket.socket()
host = '127.0.0.1'
port = 5050

print('Iniciando cliente')
try:
    client_socket.connect((host, port))
    print('Conectado ao servidor')
except socket.error as e:
    print(str(e))

res = client_socket.recv(2048)
print(res.decode('utf-8'))

msg = ''
while msg != 'sair':
    msg = input('Envie uma mensagem, ou digite sair para encerrar: ')
    client_socket.send(str.encode(msg))
    res = client_socket.recv(2048)
    print(res.decode('utf-8'))

client_socket.close()