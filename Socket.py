import sys
import socket
from time import sleep

class Client:
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def start(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(self.socket_path)
        message = "Hello"
        size = len(message.encode('utf-8'))
        sys.stdout.write("{} \n".format(str(size)))
        if(s.send(str(size).encode('utf-8'))):
            sleep(0.01)
            s.send(message.encode('utf-8'))
        s.close()

def main():
    client = Client('/tmp/unix-socket')
    client.start()

if __name__ == '__main__':
    main()
