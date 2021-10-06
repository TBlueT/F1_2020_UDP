#-*- coding: utf-8 -*-

import socket, time, datetime
import numpy as np
from PyQt5 import QtCore, QtGui

from packets import *

class UDP_pack(QtCore.QThread):
    def __init__(self, parent=None):
        super(UDP_pack, self).__init__(parent)
        self.Working = True
        self.mainWindow = parent
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 20777))

        self.Packet_LapData = []
        self.Packet_CarTelemetryData = []
        self.Packet_CarStatusData = []

        self.Packet_LapData_in = False
        self.Packet_CarTelemetryData_in = False
        self.Packet_CarStatusData_in = False
    def run(self):
        while self.Working:
            data, addr = self.sock.recvfrom(10000)
            buf = unpack_udp_packet(data)
            if buf:
                if buf.header.packetId == 2:
                    self.Packet_LapData = buf
                    self.Packet_LapData_in = True
                elif buf.header.packetId == 6:
                    self.Packet_CarTelemetryData = buf
                    self.Packet_CarTelemetryData_in = True
                elif buf.header.packetId == 7:
                    self.Packet_CarStatusData = buf
                    self.Packet_CarStatusData_in = True