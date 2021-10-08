#-*- coding: utf-8 -*-

import socket, time, datetime
import numpy as np
from PyQt5 import QtCore, QtGui, QtTest
from PyQt5.QtWidgets import *
from part import *

class Process(QtCore.QThread):
    Set_Text = QtCore.pyqtSignal(str, str)
    Set_Pixmap = QtCore.pyqtSignal(str, QtGui.QImage)
    Set_StyleSheet = QtCore.pyqtSignal(str, str)
    def __init__(self, parent=None):
        super(Process, self).__init__(parent)
        self.Working = True
        self.mainWindow = parent
        self.udp_pack = self.mainWindow.udp_pack

        self.Standby = False
        self.Standby_time = datetime.datetime.now()

        ersStoreEnergy_bar_img = np.full((10, 10, 3), (255, 255, 0), dtype=np.uint8)
        ersStoreEnergy_bar_img = QtGui.QImage(ersStoreEnergy_bar_img, 10, 10, 10 * 3, QtGui.QImage.Format_RGB888)
        ersStoreEnergy_bar_img = QtGui.QPixmap.fromImage(ersStoreEnergy_bar_img)

        self.ersStoreEnergy_bar = QtGui.QPixmap(ersStoreEnergy_bar_img)
        self.loading_img = QtGui.QPixmap("loading2.png")

        self.LED_bar = 0

        self.FuelRemainingLaps = 0
        self.FuelRemainingLaps_old = 0
        self.my_ersStoreEnergy = 0
        self.my_ersStoreEnergy_old = 0
        self.my_ersDeployMode = 0
        self.my_my_ersDeployMode_old = 0

        self.drs_onoff = 0
        self.drs_drsAllowed = 0

    def run(self):
        while self.Working:

            if self.udp_pack.Packet_SessionData_in:
                DataPack = self.udp_pack.Packet_SessionData
                self.udp_pack.Packet_SessionData_in = False

            elif self.udp_pack.Packet_LapData_in:
                DataPack = self.udp_pack.Packet_LapData
                self.LapDataPart(DataPack)
                self.Standby_time = datetime.datetime.now()
                self.udp_pack.Packet_LapData_in = False

            elif self.udp_pack.Packet_CarTelemetryData_in:
                DataPack = self.udp_pack.Packet_CarTelemetryData
                self.CarTelemetryDataPart(DataPack)
                self.Standby_time = datetime.datetime.now()
                self.udp_pack.Packet_CarTelemetryData_in = False

            elif self.udp_pack.Packet_CarStatusData_in:
                DataPack = self.udp_pack.Packet_CarStatusData
                self.CarStatusDataPart(DataPack)
                self.Standby_time = datetime.datetime.now()
                self.udp_pack.Packet_CarStatusData_in = False

            else:
                QtTest.QTest.qWait(1)   #stabilization?

            if (datetime.datetime.now() - self.Standby_time) > datetime.timedelta(microseconds=300000):
                self.Standby = True
                self.mainWindow.carStatusData_ui("setPixmap", "Gear", self.loading_img)

                self.Set_Text.emit("OVERTAKE", "Standby")
            else:
                self.Standby = False
                self.Set_Text.emit("OVERTAKE", "OVERTAKE")



    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


    def LapDataPart(self, DataPack):

        self.my_currentLapTime(DataPack)

        self.Set_Text.emit("CurrentLapNum", F"L{DataPack.lapData[DataPack.header.playerCarIndex].currentLapNum}")
        self.Set_Text.emit("CarPosition", F"P{DataPack.lapData[DataPack.header.playerCarIndex].carPosition}")

    def my_currentLapTime(self, DataPack):
        my_currentLapTime = datetime.datetime.utcfromtimestamp(
            DataPack.lapData[DataPack.header.playerCarIndex].currentLapTime)

        my_currentLapTime_hour = F"{my_currentLapTime.hour}:" if my_currentLapTime.hour >= 10 else F"0{my_currentLapTime.hour}:" if my_currentLapTime.hour != 0 else ""
        my_currentLapTime_minute = F"{my_currentLapTime.minute}:" if my_currentLapTime.minute >= 10 else F"0{my_currentLapTime.minute}:" if my_currentLapTime.minute != 0 or my_currentLapTime.hour != 0 else ""
        my_currentLapTime_second = F"{my_currentLapTime.second}." if my_currentLapTime.second >= 10 else F"0{my_currentLapTime.second}."
        my_currentLapTime_microsecond = F"{str(my_currentLapTime.microsecond)[0:3]}"

        self.Set_Text.emit("CurrentLapTime",
                           F"{my_currentLapTime_hour}{my_currentLapTime_minute}{my_currentLapTime_second}{my_currentLapTime_microsecond}")


    def CarTelemetryDataPart(self, DataPack):

        self.gear_Process(DataPack)

        self.Set_Text.emit("Soeed",F"{DataPack.carTelemetryData[DataPack.header.playerCarIndex].speed} KPH")

        for i in range(0, 4):
            self.Set_Text.emit(F"TyresSurfaceTemperature_{i + 1}",
                               F"{DataPack.carTelemetryData[DataPack.header.playerCarIndex].tyresInnerTemperature[i]}'C")

        if DataPack.carTelemetryData[DataPack.header.playerCarIndex].drs:
            if self.drs_onoff == False:
                self.Set_Text.emit(F"LED_{14}", "■")
                self.drs_onoff = True
        else:
            self.drs_onoff = False

        self.LED_bar_Process(DataPack)

    def gear_Process(self, DataPack):
        my_gear = DataPack.carTelemetryData[DataPack.header.playerCarIndex].gear
        my_gear = F"{my_gear}" if DataPack.carTelemetryData[
                                      DataPack.header.playerCarIndex].gear > 0 else "N" if my_gear != -1 else "R"
        self.Set_Text.emit("Gear", my_gear)

    def LED_bar_Process(self, DataPack):
        self.LED_bar = int(DataPack.carTelemetryData[DataPack.header.playerCarIndex].revLightsPercent / 6.65)

        if self.LED_bar != 0:
                for i in range(1, 1 if self.LED_bar == 0 else self.LED_bar+1):
                    LED_count = i if not self.drs_drsAllowed else i if i < 15 else 14
                    LED_count = LED_count if not self.drs_onoff else LED_count if LED_count < 14 else 13
                    self.Set_Text.emit(F"LED_{LED_count}", "■")

        if self.LED_bar != 15:
                for i in range(1 if self.LED_bar == 0 else self.LED_bar, 16):
                    LED_count = i if not self.drs_drsAllowed else i if i < 15 else 14
                    LED_count = LED_count if not self.drs_onoff else LED_count if LED_count < 14 else 13
                    self.Set_Text.emit(F"LED_{LED_count}", " ")


    def CarStatusDataPart(self, DataPack):
        self.FuelRemainingLaps = round(DataPack.carStatusData[DataPack.header.playerCarIndex].fuelRemainingLaps, 1)
        if self.FuelRemainingLaps != self.FuelRemainingLaps_old:
            self.Set_Text.emit("FuelRemainingLaps", F"{self.FuelRemainingLaps}")
            self.FuelRemainingLaps_old = self.FuelRemainingLaps

        self.my_ersDeployMode = DataPack.carStatusData[DataPack.header.playerCarIndex].ersDeployMode
        if self.my_ersDeployMode != self.my_my_ersDeployMode_old:
            if self.my_ersDeployMode == 0:
                self.Set_StyleSheet.emit("OVERTAKE",
                                         "background-color: rgb(0,0,0); color: rgb(255,255,255);")
                self.Set_Text.emit("ersDeployMode_num", F"0")
            elif self.my_ersDeployMode == 1:
                self.Set_StyleSheet.emit("OVERTAKE",
                                         "background-color: rgb(230,230,0); color: rgb(255,255,255);")
                self.Set_Text.emit("ersDeployMode_num", F"1")
            elif self.my_ersDeployMode == 2:
                self.Set_StyleSheet.emit("OVERTAKE",
                                         "background-color: rgb(0,220,0); color: rgb(255,255,255);")
                self.Set_Text.emit("ersDeployMode_num", F"3")
            elif self.my_ersDeployMode == 3:
                self.Set_StyleSheet.emit("OVERTAKE",
                                         "background-color: rgb(0,0,0); color: rgb(255,255,255);")
                self.Set_Text.emit("ersDeployMode_num", F"2")
            self.my_my_ersDeployMode_old = self.my_ersDeployMode

        self.my_ersStoreEnergy = int(
            self.map(DataPack.carStatusData[DataPack.header.playerCarIndex].ersStoreEnergy, 0, 4000000, 0, 100))
        if self.my_ersStoreEnergy != self.my_ersStoreEnergy_old:

            ersStoreEnergy_img = self.ersStoreEnergy_bar.scaled(int(
            self.map(self.my_ersStoreEnergy, 0, 100, 0, 803)), 20)
            if self.my_ersStoreEnergy < 10:
                ersStoreEnergy_img.fill(QtGui.QColor(255,int(self.map(self.my_ersStoreEnergy,0,10,0,255)),0))
                self.Set_StyleSheet.emit("ersStoreEnergy_percent",
                                         F"color: rgb(255,{int(self.map(self.my_ersStoreEnergy, 0, 10, 0, 255))},0);")

            self.mainWindow.carStatusData_ui("setPixmap", "ersStoreEnergy_Bar", ersStoreEnergy_img)
            self.Set_Text.emit("ersStoreEnergy_percent", F"{self.my_ersStoreEnergy}")
            self.my_ersStoreEnergy_old = self.my_ersStoreEnergy

        if DataPack.carStatusData[DataPack.header.playerCarIndex].drsAllowed or self.drs_onoff:
            if self.drs_drsAllowed == False:
                self.Set_Text.emit(F"LED_{15}", "■")
                self.drs_drsAllowed = True
        else:
            self.drs_drsAllowed = False
