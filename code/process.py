#-*- coding: utf-8 -*-

import socket, time, datetime
import numpy as np
from PyQt5 import QtCore, QtGui, QtTest
from PyQt5.QtWidgets import *
from packets import *

class Process(QtCore.QThread):
    def __init__(self, parent=None):
        super(Process, self).__init__(parent)
        self.Working = True
        self.mainWindow = parent
        self.udp_pack = self.mainWindow.udp_pack

        self.ersStoreEnergy_bar = QtGui.QPixmap("1.png")

        self.LED_bar = 0
        self.LED_bar_old = 0

        self.my_ersStoreEnergy = 0
        self.my_ersStoreEnergy_old = 0
        self.my_ersDeployMode = 0
        self.my_my_ersDeployMode_old = 0

    def run(self):
        while self.Working:
            if self.udp_pack.Packet_LapData_in:
                DataPack = self.udp_pack.Packet_LapData
                self.LapDataPart(DataPack)
                self.udp_pack.Packet_LapData_in = False

            elif self.udp_pack.Packet_CarTelemetryData_in:
                DataPack = self.udp_pack.Packet_CarTelemetryData
                self.CarTelemetryDataPart(DataPack)
                self.udp_pack.Packet_CarTelemetryData_in = False

            elif self.udp_pack.Packet_CarStatusData_in:
                DataPack = self.udp_pack.Packet_CarStatusData
                self.CarStatusDataPart(DataPack)

                self.udp_pack.Packet_CarStatusData_in = False
            else:
                QtTest.QTest.qWait(1)


    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


    def LapDataPart(self, DataPack):
        my_currentLapTime = datetime.datetime.utcfromtimestamp(
            DataPack.lapData[DataPack.header.playerCarIndex].currentLapTime)

        my_currentLapTime_hour = F"{my_currentLapTime.hour}:" if my_currentLapTime.hour >= 10 else F"0{my_currentLapTime.hour}:" if my_currentLapTime.hour != 0 else ""
        my_currentLapTime_minute = F"{my_currentLapTime.minute}:" if my_currentLapTime.minute >= 10 else F"0{my_currentLapTime.minute}:" if my_currentLapTime.minute != 0 or my_currentLapTime.hour != 0 else ""
        my_currentLapTime_second = F"{my_currentLapTime.second}." if my_currentLapTime.second >= 10 else F"0{my_currentLapTime.second}."
        my_currentLapTime_microsecond = F"{str(my_currentLapTime.microsecond)[0:3]}"

        self.mainWindow.lapData_ui("CurrentLapTime",
                                   F"{my_currentLapTime_hour}{my_currentLapTime_minute}{my_currentLapTime_second}{my_currentLapTime_microsecond}")

    def CarTelemetryDataPart(self, DataPack):
        my_gear = DataPack.carTelemetryData[DataPack.header.playerCarIndex].gear
        my_gear = F"{my_gear}" if DataPack.carTelemetryData[
                                      DataPack.header.playerCarIndex].gear > 0 else "N" if my_gear != -1 else "R"
        self.mainWindow.carTelemetryData_ui("Gear", my_gear)

        self.mainWindow.carTelemetryData_ui("Soeed",
                                            F"{DataPack.carTelemetryData[DataPack.header.playerCarIndex].speed} KPH")

        for i in range(0, 4):
            self.mainWindow.carTelemetryData_ui(F"TyresSurfaceTemperature_{i + 1}",
                                                F"{DataPack.carTelemetryData[DataPack.header.playerCarIndex].tyresInnerTemperature[i]}'C")

        self.LED_bar = int(DataPack.carTelemetryData[DataPack.header.playerCarIndex].revLightsPercent / 7.14)
        if self.LED_bar != self.LED_bar_old:
            if self.LED_bar != 0:
                for i in range(0, self.LED_bar):
                    self.mainWindow.carTelemetryData_ui(F"LED_{i + 1}", "■")
            if self.LED_bar != 14:
                for i in range(self.LED_bar, 14):
                    if i != 14:
                        self.mainWindow.carTelemetryData_ui(F"LED_{i + 1}", " ")
            self.LED_bar_old = self.LED_bar


    def CarStatusDataPart(self, DataPack):
        self.my_ersDeployMode = DataPack.carStatusData[DataPack.header.playerCarIndex].ersDeployMode
        if self.my_ersDeployMode != self.my_my_ersDeployMode_old:
            if self.my_ersDeployMode == 0:
                self.mainWindow.carStatusData_ui("setStyleSheet", "OVERTAKE",
                                                 "background-color: rgb(0,0,0); color: rgb(255,255,255);")
                self.mainWindow.carStatusData_ui("setText", "ersDeployMode_num", F"0")
            elif self.my_ersDeployMode == 1:
                self.mainWindow.carStatusData_ui("setStyleSheet", "OVERTAKE",
                                                 "background-color: rgb(230,230,0); color: rgb(255,255,255);")
                self.mainWindow.carStatusData_ui("setText", "ersDeployMode_num", F"1")
            elif self.my_ersDeployMode == 2:
                self.mainWindow.carStatusData_ui("setStyleSheet", "OVERTAKE",
                                                 "background-color: rgb(0,220,0); color: rgb(255,255,255);")
                self.mainWindow.carStatusData_ui("setText", "ersDeployMode_num", F"3")
            self.my_my_ersDeployMode_old = self.my_ersDeployMode

        self.my_ersStoreEnergy = int(
            self.map(DataPack.carStatusData[DataPack.header.playerCarIndex].ersStoreEnergy, 0, 4000000, 0, 100))
        if self.my_ersStoreEnergy != self.my_ersStoreEnergy_old:

            ersStoreEnergy_img = self.ersStoreEnergy_bar.scaled(int(
            self.map(self.my_ersStoreEnergy, 0, 100, 0, 803)), 70)
            #ersStoreEnergy_img.fill(QtGui.QColor('red'))

            self.mainWindow.carStatusData_ui("setPixmap", "ersStoreEnergy_Bar", ersStoreEnergy_img)
            self.mainWindow.carStatusData_ui("setText", "ersStoreEnergy_percent", F"{self.my_ersStoreEnergy}")
            self.my_ersStoreEnergy_old = self.my_ersStoreEnergy