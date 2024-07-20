import socket

PORT = 2367
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', PORT)) #binding the port
print('waiting...')

while True:   #receiving data
  data,addr=s.recvfrom(1024)

print('received:',data,'from',addr)