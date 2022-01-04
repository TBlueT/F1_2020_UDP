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
        self.sock.bind(('0.0.0.0', 20777))

        self.Packet_MotionData = []
        self.Packet_SessionData = []
        self.Packet_LapData = []
        self.Packet_CarTelemetryData = []
        self.Packet_CarStatusData = []

        self.test = {1: 0}

    def run(self):
        while self.Working:
            data, addr = self.sock.recvfrom(10000)
            buf = unpack_udp_packet(data)
            if buf:
                if buf.header.packetId == 0:
                    self.Packet_MotionData = buf

                elif buf.header.packetId == 1:
                    self.Packet_SessionData = buf

                elif buf.header.packetId == 2:
                    self.Packet_LapData = buf

                elif buf.header.packetId == 6:
                    self.Packet_CarTelemetryData = buf

                elif buf.header.packetId == 7:
                    self.Packet_CarStatusData = buf