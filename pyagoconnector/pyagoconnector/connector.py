import socket
import threading
import time
import json
import pkg_resources
import logging


class AgoPgn:
    """ PGN message from AGOpenGPS:
        PGN message has a always a HeaderHi and a HeaderLo which are the first two bytes of the message.
        Then a variable data part follows
        """

    def __init__(self, header_low: int, header_hi: int = 127, data_def: list = None):
        # Instance attributes
        self.h_hi: int = header_hi
        self.h_low: int = header_low
        self.pgn_number: int = 0
        self.descr: str = "Description"
        self.header: tuple = (self.h_hi, self.h_low)
        self.data_def: list = data_def
        self.data: dict = {}

    def __repr__(self):
        return str(self.data)


def get_pgndef_file():
    path = 'pgn_definition.json'  # always use slash
    return pkg_resources.resource_filename(__name__, path)


class AgoUdpServer:
    """ UDP Server which receives data from AGOpenGPS via UDP """

    def __init__(self, ip: str = "", port: int = 8888):
        """ Initalize server """
        # Instance attributes
        self.thread: threading.Thread = None
        self.ip_address: str = ip
        self.port: int = port
        self.serverSock: socket = None
        self.pgndef: list = []        # storage for PGN definitions (JSON)
        self.pgndata: dict = {}       # storage for data read per PGN (AgoPgn objects)

        # get IP address of host if not given
        if ip == "":
            ip = socket.gethostbyname(socket.gethostname())
        self.ip_address = ip

        # load PGN data definition
        self.load_pgndef()

    def load_pgndef(self):
        """ Load PGN definition """
        with open(get_pgndef_file(), "r") as f:
            self.pgndef = json.load(f)

        # prepare a PGN object for each definition in the list
        for d in self.pgndef:
            pgn = AgoPgn(header_low=d["Header_Lo"], header_hi=d["Header_Hi"], data_def=d["Data"])
            pgn.pgn_number = d["PGN"]
            pgn.descr = d["Description"]
            self.pgndata[pgn.header] = pgn      # add PGN to data dict with header tuple as key

    def run(self):
        """ Startup and run server"""
        # start Server
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind((self.ip_address, self.port))

        logging.info("Server startet: " + self.ip_address + ":" + str(self.port))
        while True:
            data = self.serverSock.recvfrom(1024)
            # print(f"Message received: ${str(data)}")
            try:
                # get message part
                bdata: bytes = data[0]

                # get first 2 bytes which should contain the header, as int
                hd_hi = int(bdata[0])
                hd_lo = int(bdata[1])
                # construct the tuple / key for the definition
                hd = (hd_hi, hd_lo)
                # get definition
                try:
                    pgn = self.pgndata[hd]
                    # definition found, we want the data
                    datapart = bdata[2:]
                    AgoUdpServer.parse_data(pgn=pgn, data=datapart)
                except KeyError:
                    # Nothing found for his PGN message key, we are not interested in this message
                    pass

            except BaseException as ex:
                logging.exception(f"Exception while receiving message ${str(data)}", ex)
                raise ex

    def get_unique_param_value(self, param_id: str):
        """ Get parameter value via ID; assumes the ID is unique (otherwise returns first value)"""
        for pgn in self.pgndata.values():  # loop pgns
            for cur_par_id in pgn.data:  # loop parameters
                if cur_par_id == param_id:
                    return pgn.data[cur_par_id]

    def get_param_value(self, param_id: str, pgn_header: tuple):
        """ Get parameter value via ID & PGM message header"""
        pgn = self.pgndata[pgn_header]
        return pgn.data[param_id]

    @staticmethod
    def parse_data(pgn: AgoPgn, data: bytes):
        i = 0
        data_def_len = len(pgn.data_def)
        for b in data:
            # get corresponding data def
            if not i < (data_def_len - 1):
                # more data than defined!
                pgnid = "Undefined" + str(i)
                pgn.data[pgnid] = b
            else:
                # definition available
                pgn_def = pgn.data_def[i]
                # set data based on type
                pgntype = pgn_def["Type"]
                if pgntype == "int":
                    pgn.data[pgn_def["Id"]] = int(b)
                elif pgntype == "float":
                    pgn.data[pgn_def["Id"]] = float(b)
                elif pgntype == "str":
                    pgn.data[pgn_def["Id"]] = str(b)
                elif pgntype == "bool":
                    pgn.data[pgn_def["Id"]] = bool(b)
                else:
                    pgn.data[pgn_def["Id"]] = b

            i += 1

    @staticmethod
    def start_server_thread(ip: str = "", port: int = 8888, name: str = "AgUDPServer"):
        """ Start UDP server as separate thread """

        ago: AgoUdpServer = AgoUdpServer(ip, port)
        ago.thread = threading.Thread(name=name, target=ago.run, daemon=True)
        ago.thread.start()
        return ago

    def stop_server(self):
        """ Stop UDP server """
        self.serverSock.close()


if __name__ == "__main__":
    """ Start server """
    a = AgoUdpServer.start_server_thread()
    while True:
        print("Current Data:")
        for d in a.pgndata.items():
            print(d)
        time.sleep(1)
