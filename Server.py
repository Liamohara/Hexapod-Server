# Standard library imports
import socket
import sys

# Local imports
from Control import Control
from lib.console import error, cyan


class Server:
    def __init__(self):
        self.__HEADER = 64
        self.__PORT = 5050
        self.__HOST = "0.0.0.0"
        self.__FORMAT = "utf-8"
        self.__DISCONNECT_MSG = "!DISCONNECT"

        self.__CONTROL = Control()

        try:
            self.__socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(error(f"Error creating socket: {e}"))
            sys.exit(1)

        try:
            self.__socket.bind((self.__HOST, self.__PORT))
        except socket.gaierror as e:
            print(error(f"Address-related error connecting to server: {e}"))
            sys.exit(1)
        except socket.error as e:
            print(error(f"Connection error: {e}"))
            sys.exit(1)

    def start(self):
        print("[STARTING] Server is starting...")
        self.__socket.listen()
        print(f"[LISTENING] Server is listening on {self.__HOST}")

        connected = False
        while not connected:
            try:
                conn, addr = self.__socket.accept()
                print("[CONNECTION] Client connected! :)")

                connected = True
            except socket.error as e:
                print(e)

        self.__handler(conn)

    def __handler(self, conn):
        connected = True
        while connected:
            msg_length = conn.recv(self.__HEADER).decode(self.__FORMAT)

            if msg_length:
                msg_length = int(msg_length)

                try:
                    msg = conn.recv(msg_length).decode(self.__FORMAT)
                    instruction = msg.split("#")
                except socket.error as e:
                    print(error(f"Error recieving data: {e}"))
                    sys.exit(1)

                if self.__DISCONNECT_MSG in instruction:
                    connected = False
                elif "WALK" in instruction:
                    self.__CONTROL.walk(
                        int(instruction[1]), int(instruction[2]))
                elif "RELAX" in instruction:
                    self.__CONTROL.relax()
                else:
                    print(cyan(msg))  # Needed?

                conn.send("Msg received".encode(self.__FORMAT))

        conn.close()
        print(f"[DISCONNECTED] Client disconnected :(")

        self.__CONTROL.relax()

    def __send(self, conn, msg):
        try:
            conn.send(msg.encode(self.__FORMAT))
        except socket.error as e:
            print(error(f"Error sending data: {e}"))
            sys.exit(1)
