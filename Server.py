import socket
import threading

from Control import Control

class Server:
    def __init(self):
        self.__HEADER = 64
        self.__PORT = 5050
        self.__HOST = socket.gethostname()
        self.__FORMAT = "utf-8"