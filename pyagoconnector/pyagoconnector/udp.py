import socket
import threading
import time


class AgoUdpServer:
    """ UDP Server which receives data from AGOpenGPS via UDP """

    def __init__(self, ip: str = "", port: int = 8888):
        """ Initalize server """
        # get IP address of host if not given
        if ip == "":
            self.ip_address = ip = socket.gethostbyname(socket.gethostname())

        # Instance attributes
        self.ip_address = ip
        self.port = port

    def run(self):
        """ Startup and run server"""
        # start Server
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((self.ip_address, self.port))

        print("Server startet: " + self.ip_address + ":" + str(self.port))

        while True:
            data = self.serverSock.recvfrom(1024)
            # print(f"Message received: ${str(data)}")
            try:
                # get message part
                bdata: bytes = data[0]

                # get data
                text = str(self.ip_address) + ": "
                for b in bdata:
                    text += str(b) + ";"

                print(text)

            except BaseException as ex:
                print(f"Exception happened! {ex}")
                print(f"Received Message ${str(data)}")



def start_server_thread(ip: str = "", port: int = 8888, name: str = "AgUDPServer"):
    """ Start UDP server as separate thread """

    ago: AgoUdpServer = AgoUdpServer(ip, port)
    t = threading.Thread(name=name, target=ago.run, daemon=1)
    t.start()

if __name__ == "__main__":
    """ Start server """
    start_server_thread()
    while True:
        print(".")
        time.sleep(10)
