# Standard library imports
import socket
import sys

# Local imports
from lib.Control import Control
from lib.console import error

socket.setdefaulttimeout(20)

HEADER = 64
PORT = 5050
HOST = "0.0.0.0"
FORMAT = "utf-8"
WALK_MSG = "!WALK"
BALANCE_MSG = "!BALANCE"
RELAX_MSG = "!RELAX"
DISCONNECT_MSG = "!DISCONNECT"


class Server:
    def __init__(self):
        self.__CONTROL = Control()

        try:
            self.__socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
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

        connected = False
        while not connected:
            try:
                conn, addr = self.__socket.accept()
                print("[CONNECTION] Client connected! :)")

                connected = True
            except socket.error as e:
                print(error(f"[ERROR] Error connecting to Client. {e}"))
                sys.exit(1)

        self.__handler(conn)

    def __handler(self, conn):
        connected = True
        while connected:
            try:
                msg_length = conn.recv(HEADER).decode(FORMAT)

                if msg_length:
                    msg_length = int(msg_length)

                    try:
                        msg = conn.recv(msg_length).decode(FORMAT)
                        instruction = msg.split("#")
                    except socket.error as e:
                        print(error(f"[ERROR] Error recieving data: {e}"))
                        sys.exit(1)

                    if WALK_MSG in instruction:
                        self.__send(
                            conn, f"Walking {instruction[1]} pace(s)...")
                        self.__CONTROL.walk(
                            int(instruction[1]), int(instruction[2]))
                    elif BALANCE_MSG in instruction:
                        self.__send(conn, "Balancing..")
                        self.__CONTROL.__balance()
                    elif RELAX_MSG in instruction:
                        self.__send(conn, "Relaxing...")
                        self.__CONTROL.relax()
                    elif DISCONNECT_MSG in instruction:
                        self.__send(conn, "Disconnecting...")
                        self.__send(conn, "!DISCONNECT")
                        connected = False

                    self.__send(conn, "!COMPLETED")
            except socket.timeout:
                self.__send(conn, "Disconnecting...")
                self.__send(conn, "!DISCONNECT")
                connected = False

        conn.close()
        print(f"[DISCONNECTED] Client disconnected :(")

        self.__CONTROL.relax()

    def __send(self, conn, msg):
        try:
            conn.send(msg.encode(FORMAT))
        except socket.error as e:
            print(error(f"[ERROR] Error sending message: {e}"))
            sys.exit(1)
