import socket                   # Import socket module

s = socket.socket()             # Create a socket object
s.connect(('192.168.1.102', 30000))
with open('received_file.mp4', 'wb') as f:
    print ('file opened')
    while True:
        print('receiving data...')
        data = s.recv(1024)
        if not data:
            break
        # write data to a file
        f.write(data)

f.close()
print('Successfully get the file')
s.close()
print('connection closed')