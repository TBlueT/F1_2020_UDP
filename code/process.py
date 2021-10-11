#-*- coding: utf-8 -*-

import socket, time, datetime
import numpy as np
from PyQt5 import QtCore, QtGui, QtTest
from PyQt5.QtWidgets import *
from part import *

class Process(QtCore.QThread):
    Set_Text = QtCore.pyqtSignal(str, str)
    Set_Pixmap = QtCore.pyqtSignal(str, QtGui.QPixmap)
    Set_StyleSheet = QtCore.pyqtSignal(str, str)
    def __init__(self, parent=None):
        super(Process, self).__init__(parent)
        self.Working = True
        self.mainWindow = parent
        self.udp_pack = self.mainWindow.udp_pack

        self.Standby = False
        self.Standby_time = datetime.datetime.now()

        self.LED_bar = 0

        self.FuelMix = comparison()
        self.FuelRemainingLaps = comparison()
        self.ErsStoreEnergy = comparison()
        self.ErsDeployMode = comparison()

        self.Drs_onoff = 0
        self.Drs_drsAllowed = 0

    def img_init(self):
        ersStoreEnergy_bar_img = np.full((10, 10, 3), (255, 255, 0), dtype=np.uint8)
        ersStoreEnergy_bar_img = QtGui.QImage(ersStoreEnergy_bar_img, 10, 10, 10 * 3, QtGui.QImage.Format_RGB888)

        self.ersStoreEnergy_bar = QtGui.QPixmap.fromImage(ersStoreEnergy_bar_img)

        ersStoreEnergy_img = self.ersStoreEnergy_bar.scaled(self.mainWindow.ersStoreEnergy_Bar.width(), 20)
        self.Set_Pixmap.emit("ersStoreEnergy_Bar", ersStoreEnergy_img)

        ersStoreEnergy_img.fill(QtGui.QColor(255, 255, 255))
        ersStoreEnergy_img = ersStoreEnergy_img.scaled(self.mainWindow.ErsDeployedThisLap.width(), 20)
        self.Set_Pixmap.emit("ErsDeployedThisLap", ersStoreEnergy_img)
        self.Set_Pixmap.emit("label_3", ersStoreEnergy_img)
        self.loading_img = QtGui.QPixmap("loading2.png")

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
                if self.Standby == False:
                    self.Set_Pixmap.emit("Gear", self.loading_img)
                    self.Set_Text.emit("OVERTAKE", "Standby")
                    self.Standby = True
            else:
                self.Standby = False
                self.Set_Text.emit("OVERTAKE", "OVERTAKE")




    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


    def LapDataPart(self, DataPack):

        self.CurrentLapTime(DataPack)

        self.Set_Text.emit("CurrentLapNum", F"L{DataPack.lapData[DataPack.header.playerCarIndex].currentLapNum}")
        self.Set_Text.emit("CarPosition", F"P{DataPack.lapData[DataPack.header.playerCarIndex].carPosition}")

    def CurrentLapTime(self, DataPack):
        CurrentLapTime = datetime.datetime.utcfromtimestamp(
            DataPack.lapData[DataPack.header.playerCarIndex].currentLapTime)

        CurrentLapTime_hour = F"{CurrentLapTime.hour}:" if CurrentLapTime.hour >= 10 else F"0{CurrentLapTime.hour}:" if CurrentLapTime.hour != 0 else ""
        CurrentLapTime_minute = F"{CurrentLapTime.minute}:" if CurrentLapTime.minute >= 10 else F"0{CurrentLapTime.minute}:" if CurrentLapTime.minute != 0 or CurrentLapTime.hour != 0 else ""
        CurrentLapTime_second = F"{CurrentLapTime.second}." if CurrentLapTime.second >= 10 else F"0{CurrentLapTime.second}."
        CurrentLapTime_microsecond = F"{str(CurrentLapTime.microsecond)[0:3]}"

        self.Set_Text.emit("CurrentLapTime",
                           F"{CurrentLapTime_hour}{CurrentLapTime_minute}{CurrentLapTime_second}{CurrentLapTime_microsecond}")


    def CarTelemetryDataPart(self, DataPack):

        self.Gear_Process(DataPack)

        self.Set_Text.emit("Soeed",F"{DataPack.carTelemetryData[DataPack.header.playerCarIndex].speed} KPH")

        for i in range(0, 4):
            self.Set_Text.emit(F"TyresSurfaceTemperature_{i + 1}",
                               F"{DataPack.carTelemetryData[DataPack.header.playerCarIndex].tyresInnerTemperature[i]}'C")

        if DataPack.carTelemetryData[DataPack.header.playerCarIndex].drs:
            if self.Drs_onoff == False:
                self.Set_Text.emit(F"LED_{14}", "■")
                self.Drs_onoff = True
        else:
            self.Drs_onoff = False

        self.LED_bar_Process(DataPack)

    def Gear_Process(self, DataPack):
        Gear = DataPack.carTelemetryData[DataPack.header.playerCarIndex].gear
        Gear = F"{Gear}" if DataPack.carTelemetryData[
                                      DataPack.header.playerCarIndex].gear > 0 else "N" if Gear != -1 else "R"
        self.Set_Text.emit("Gear", Gear)

    def LED_bar_Process(self, DataPack):
        self.LED_bar = int(DataPack.carTelemetryData[DataPack.header.playerCarIndex].revLightsPercent / 6.65)

        if self.LED_bar != 0:
                for i in range(1, 1 if self.LED_bar == 0 else self.LED_bar+1):
                    LED_count = i if not self.Drs_drsAllowed else i if i < 15 else 14
                    LED_count = LED_count if not self.Drs_onoff else LED_count if LED_count < 14 else 13
                    self.Set_Text.emit(F"LED_{LED_count}", "■")

        if self.LED_bar != 15:
                for i in range(1 if self.LED_bar == 0 else self.LED_bar, 16):
                    LED_count = i if not self.Drs_drsAllowed else i if i < 15 else 14
                    LED_count = LED_count if not self.Drs_onoff else LED_count if LED_count < 14 else 13
                    self.Set_Text.emit(F"LED_{LED_count}", " ")


    def CarStatusDataPart(self, DataPack):
        self.FuelMix.add_new(DataPack.carStatusData[DataPack.header.playerCarIndex].fuelMix)
        if self.FuelMix.different():
            FuelMix_key = {
                (0): "[1] Lean",
                (1): "[2] Standard",
                (2): "[3] Roch",
                (3): "[4] Max"
            }
            self.Set_Text.emit("FuelMix", F"{FuelMix_key[self.FuelMix.new]}")
            self.FuelMix.add_old(self.FuelMix.new)

        self.FuelRemainingLaps.add_new(round(DataPack.carStatusData[DataPack.header.playerCarIndex].fuelRemainingLaps, 2))
        if self.FuelRemainingLaps.different():

            if self.FuelRemainingLaps.new > 0:
                self.Set_Text.emit("FuelRemainingLaps", F"[+{self.FuelRemainingLaps.new}]")
                self.Set_StyleSheet.emit("FuelRemainingLaps", F"color: rgb(0,255,0);")
            else:
                self.Set_Text.emit("FuelRemainingLaps", F"[{self.FuelRemainingLaps.new}]")
                self.Set_StyleSheet.emit("FuelRemainingLaps", F"color: rgb(255,0,0);")
            self.FuelRemainingLaps.add_old(self.FuelRemainingLaps.new)

        if DataPack.carStatusData[DataPack.header.playerCarIndex].drsAllowed or self.Drs_onoff:
            if self.Drs_drsAllowed == False:
                self.Set_Text.emit(F"LED_{15}", "■")
                self.Drs_drsAllowed = True
        else:
            self.Drs_drsAllowed = False

        self.ErsDeployMode.add_new(DataPack.carStatusData[DataPack.header.playerCarIndex].ersDeployMode)
        if self.ErsDeployMode.different():
            ErsDeployMode_key ={
                (0): "background-color: rgb(0,0,0); color: rgb(255,255,255);",
                (1): "background-color: rgb(230,230,0); color: rgb(255,255,255);",
                (2): "background-color: rgb(0,220,0); color: rgb(255,255,255);",
                (3): "background-color: rgb(0,0,0); color: rgb(255,255,255);"
            }
            self.Set_StyleSheet.emit("OVERTAKE",F"{ErsDeployMode_key[self.ErsDeployMode.new]}")
            ersDeployMode_num_text = self.ErsDeployMode.new if self.ErsDeployMode.new < 2 else 5-self.ErsDeployMode.new
            self.Set_Text.emit("ersDeployMode_num", F"{ersDeployMode_num_text}")

            self.ErsDeployMode.add_old(self.ErsDeployMode.new)

        self.ErsStoreEnergy.add_new(int(
            self.map(DataPack.carStatusData[DataPack.header.playerCarIndex].ersStoreEnergy, 0, 4000000, 0, 100)))
        if self.ErsStoreEnergy.different():
            ersStoreEnergy_img = self.ersStoreEnergy_bar.scaled(int(
            self.map(self.ErsStoreEnergy.new, 0, 100, 0, self.mainWindow.ersStoreEnergy_Bar.width())), 20)
            if self.ErsStoreEnergy.new < 10:
                ersStoreEnergy_img.fill(QtGui.QColor(255,int(self.map(self.ErsStoreEnergy.new,0,10,0,255)),0))
                self.Set_StyleSheet.emit("ersStoreEnergy_percent",
                                         F"color: rgb(255,{int(self.map(self.ErsStoreEnergy.new, 0, 10, 0, 255))},0);")

            self.Set_Pixmap.emit("ersStoreEnergy_Bar", ersStoreEnergy_img)
            self.Set_Text.emit("ersStoreEnergy_percent", F"{self.ErsStoreEnergy.new}%")
            self.ErsStoreEnergy.add_old(self.ErsStoreEnergy.new)

class comparison:
    def __init__(self):
        self.new = 0
        self.old = 0

    def add_new(self, data):
        self.new = data
    def add_old(self, data):
        self.old = data
    def different(self):
        return True if self.new != self.old else False
    def same(self):
        return True if self.new == self.old else False