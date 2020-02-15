from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys


host = 'localhost'
port = 1459
buffer_size = 1500

# Create the client socket. Connect to the server.
socket = socket(AF_INET, SOCK_STREAM)

done = False

while not done:
    
    try:
        socket.connect((host, port))
        done = True
    except Exception:
        print('No connection could be made because the target machine is either offline or is refusing the connection.')
        print('Here is the current network configuration:')
        print(' - Host: ' + str(host))
        print(' - Port: ' + str(port) + '\n')
        answer = input('Would you want to change those parameters? [Yes|No] ')
        if answer[:3] == 'Yes':
            host = input('Host: ')
            Port = int(input('Port: '))
        else:
            exit()

def recv():
    '''Receive messages'''
    
    while True:

        # If the connection is lost, properly stop the program.
        try: data = socket.recv(buffer_size).decode('utf8')
        except Exception:
            socket.close()
            print('The connection with the server has been lost')
            print('Press ENTER to quit the program.')
            exit()

        # If the connection has been ended properly,
        # just display this message and exit
        if data == '':
            print('Press ENTER to quit the program.')
            exit()

        # When receiving a message, uses this 'experimental' method to undisplay
        # what the user was writing and display the message instead.
        sys.stdout.write("\n") #Go to next line
        sys.stdout.write("\033[A") #Cursor up
        sys.stdout.write("\033[2K") #clear line
        sys.stdout.write(data)
        

thread = Thread(target=recv).start()

sys.stdout.write("\033[2J\n") #Clear the screen

while True:

    try:
        data = sys.stdin.readline()[:-1]
    except Exception:
        exit()
        
    if data[:1] == '/':
        data = '[COMMAND] ' + data[1:]

    try:
        socket.send(bytes(data, 'utf8'))
    except Exception:
        exit()

    sys.stdout.write("\033[F") #back to previous line
    sys.stdout.write("\033[K") #clear line
