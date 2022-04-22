# Standard library imports
import select
import socket
import sys
import threading

# Local imports
from lib.Control import Control
from lib.console import error

HEADER = 64
PORT = 5050
HOST = "0.0.0.0"
FORMAT = "utf-8"
WALK_MSG = "!WALK"
SET_LEG_POS_MSG = "!SET_LEG_POS"
BALANCE_MSG = "!BALANCE"
RELAX_MSG = "!RELAX"
COMPLETED_MSG = "!COMPLETED"
DISCONNECT_MSG = "!DISCONNECT"


class Server:
    def __init__(self):
        self.__CONTROL = Control()

        try:
            self.__socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            # Enable reusing host address and port.
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            # Disable blocking so that recv() will never block indefinitely.
            # self.__socket.setblocking(0)
        except socket.error as e:
            print(error(f"[ERROR] Error creating socket: {e}"))
            sys.exit(1)

        try:
            self.__socket.bind((HOST, PORT))
        except socket.gaierror as e:
            print(
                error(f"[ERROR] Address-related error connecting to server: {e}"))
            sys.exit(1)
        except socket.error as e:
            print(error(f"[ERROR] Connection error: {e}"))
            sys.exit(1)

    def start(self):
        print("[STARTING] Server is starting...")
        self.__socket.listen()
        print(f"[LISTENING] Server is listening on {HOST}")

        while True:
            try:
                conn, addr = self.__socket.accept()
                print("[CONNECTION] Client connected!")

                threading.Thread(target=self.__handler, args=(conn,)).start()
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
            except socket.error as e:
                print(error(f"[ERROR] Error connecting to Client. {e}"))

    def __handler(self, conn):
        connected = True
        while connected:
            try:
                # Disconnect if no message received after 30 seconds.
                ready = select.select([conn], [], [], 30)
                if not ready[0]:
                    self.__disconnect(conn)
                    connected = False

                msg_length = conn.recv(HEADER).decode(FORMAT)

                # Guard clause
                if not msg_length:
                    continue

                msg_length = int(msg_length)

                try:
                    msg = conn.recv(msg_length).decode(FORMAT)
                except socket.error as e:
                    print(error(f"[ERROR] Error recieving data: {e}"))
                    sys.exit(1)

                if not msg:
                    continue

                instruction = msg.split("#")

                if WALK_MSG in instruction:
                    self.__send(
                        conn, f"Walking {instruction[1]} pace(s)...")
                    self.__CONTROL.walk(
                        int(instruction[1]), int(instruction[2]))

                elif SET_LEG_POS_MSG in instruction:
                    self.__send(conn, "Setting leg position")
                    self.__CONTROL.setLegPosition(int(instruction[1]), int(
                        instruction[2]), int(instruction[3]), int(instruction[4]))

                elif BALANCE_MSG in instruction:
                    self.__send(conn, "Balancing..")
                    self.__CONTROL.balance()

                elif RELAX_MSG in instruction:
                    self.__send(conn, "Relaxing...")
                    self.__CONTROL.relax()

                elif DISCONNECT_MSG in instruction:
                    self.__disconnect(conn)
                    connected = False

                self.__send(conn, COMPLETED_MSG)
            except socket.timeout:
                self.__disconnect(conn)
                connected = False

        conn.close()
        print(f"[DISCONNECT] Client disconnected :(")
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")

        self.__CONTROL.relax()

    def __send(self, conn, msg):
        msg = msg.encode(FORMAT)

        msg_len = len(msg)
        send_len = str(msg_len).encode(FORMAT)
        send_len += b" " * (HEADER - len(send_len))

        try:
            conn.send(send_len)
            conn.send(msg)
        except socket.error as e:
            print(error(f"[ERROR] Error sending message: {e}"))
            sys.exit(1)

    def __disconnect(self, conn):
        self.__send(conn, "Disconnecting...")
        self.__send(conn, "!DISCONNECT")
