#-*- coding: utf-8 -*-
import ctypes

class PackedLittleEndianStructure(ctypes.LittleEndianStructure):
    _pack_ = 1


class PacketHeader(PackedLittleEndianStructure):

    _fields_ = [
        ("packetFormat", ctypes.c_uint16),
        ("gameMajorVersion", ctypes.c_uint8),
        ("gameMinorVersion", ctypes.c_uint8),
        ("packetVersion", ctypes.c_uint8),
        ("packetId", ctypes.c_uint8),
        ("sessionUID", ctypes.c_uint64),
        ("sessionTime", ctypes.c_float),
        ("frameIdentifier", ctypes.c_uint32),
        ("playerCarIndex", ctypes.c_uint8),
        ("secondaryPlayerCarIndex", ctypes.c_uint8)
    ]

class LapData(PackedLittleEndianStructure):

    _fields_ = [
        ("lastLapTime", ctypes.c_float),
        ("currentLapTime", ctypes.c_float),
        ("sector1TimeInMS", ctypes.c_uint16),
        ("sector2TimeInMS", ctypes.c_uint16),
        ("bestLapTime", ctypes.c_float),
        ("bestLapNum", ctypes.c_uint8),
        ("bestLapSector1TimeInMS", ctypes.c_uint16),
        ("bestLapSector2TimeInMS", ctypes.c_uint16),
        ("bestLapSector3TimeInMS", ctypes.c_uint16),
        ("bestOverallSector1TimeInMS", ctypes.c_uint16),
        ("bestOverallSector1LapNum", ctypes.c_uint8),
        ("bestOverallSector2TimeInMS", ctypes.c_uint16),
        ("bestOverallSector2LapNum", ctypes.c_uint8),
        ("bestOverallSector3TimeInMS", ctypes.c_uint16),
        ("bestOverallSector3LapNum", ctypes.c_uint8),
        ("lapDistance", ctypes.c_float),
        ("totalDistance", ctypes.c_float),
        ("safetyCarDelta", ctypes.c_float),
        ("carPosition", ctypes.c_uint8),
        ("currentLapNum", ctypes.c_uint8),
        ("pitStatus", ctypes.c_uint8),
        ("sector", ctypes.c_uint8),
        ("currentLapInvalid", ctypes.c_uint8),
        ("penalties", ctypes.c_uint8),
        ("gridPosition", ctypes.c_uint8),
        ("driverStatus", ctypes.c_uint8),
        ("resultStatus", ctypes.c_uint8)
    ]


class PacketLapData(PackedLittleEndianStructure):

    _fields_ = [
        ("header", PacketHeader),  # Header
        ("lapData", LapData * 22)  # Lap data for all cars on track
    ]


class CarTelemetryData(PackedLittleEndianStructure):

    _fields_ = [
        ("speed", ctypes.c_uint16),
        ("throttle", ctypes.c_float),
        ("steer", ctypes.c_float),
        ("brake", ctypes.c_float),
        ("clutch", ctypes.c_uint8),
        ("gear", ctypes.c_int8),
        ("engineRPM", ctypes.c_uint16),
        ("drs", ctypes.c_uint8),
        ("revLightsPercent", ctypes.c_uint8),
        ("brakesTemperature", ctypes.c_uint16 * 4),
        ("tyresSurfaceTemperature", ctypes.c_uint8 * 4),
        ("tyresInnerTemperature", ctypes.c_uint8 * 4),
        ("engineTemperature", ctypes.c_uint16),
        ("tyresPressure", ctypes.c_float * 4),
        ("surfaceType", ctypes.c_uint8 * 4)
    ]

class PacketCarTelemetryData(PackedLittleEndianStructure):

    _fields_ = [
        ("header", PacketHeader),
        ("carTelemetryData", CarTelemetryData * 22),
        ("buttonStatus", ctypes.c_uint32),
        ("mfdPanelIndex", ctypes.c_uint8),
        ("mfdPanelIndexSecondaryPlayer", ctypes.c_uint8),
        ("suggestedGear", ctypes.c_int8)
    ]

class CarStatusData(PackedLittleEndianStructure):

    _fields_ = [
        ("tractionControl", ctypes.c_uint8),
        ("antiLockBrakes", ctypes.c_uint8),
        ("fuelMix", ctypes.c_uint8),
        ("frontBrakeBias", ctypes.c_uint8),
        ("pitLimiterStatus", ctypes.c_uint8),
        ("fuelInTank", ctypes.c_float),
        ("fuelCapacity", ctypes.c_float),
        ("fuelRemainingLaps", ctypes.c_float),
        ("maxRPM", ctypes.c_uint16),
        ("idleRPM", ctypes.c_uint16),
        ("maxGears", ctypes.c_uint8),
        ("drsAllowed", ctypes.c_uint8),
        ("drsActivationDistance", ctypes.c_uint16),
        ("tyresWear", ctypes.c_uint8 * 4),
        ("actualTyreCompound", ctypes.c_uint8),
        ("visualTyreCompound", ctypes.c_uint8),
        ("tyresAgeLaps", ctypes.c_uint8),
        ("tyresDamage", ctypes.c_uint8 * 4),
        ("frontLeftWingDamage", ctypes.c_uint8),
        ("frontRightWingDamage", ctypes.c_uint8),
        ("rearWingDamage", ctypes.c_uint8),
        ("drsFault", ctypes.c_uint8),
        ("engineDamage", ctypes.c_uint8),
        ("gearBoxDamage", ctypes.c_uint8),
        ("vehicleFiaFlags", ctypes.c_int8),
        ("ersStoreEnergy", ctypes.c_float),
        ("ersDeployMode", ctypes.c_uint8),
        ("ersHarvestedThisLapMGUK", ctypes.c_float),
        ("ersHarvestedThisLapMGUH", ctypes.c_float),
        ("ersDeployedThisLap", ctypes.c_float)
    ]


class PacketCarStatusData(PackedLittleEndianStructure):

    _fields_ = [
        ("header", PacketHeader),
        ("carStatusData", CarStatusData * 22)
    ]

PacketType = {
    (2020, 1, 2): PacketLapData,
    (2020, 1, 6): PacketCarTelemetryData,
    (2020, 1, 7): PacketCarStatusData
}


def unpack_udp_packet(packet: bytes):

    header = PacketHeader.from_buffer_copy(packet)
    key = (header.packetFormat, header.packetVersion, header.packetId)
    if key not in PacketType:
        return 0
    else:
        packet_type = PacketType[key]
        return packet_type.from_buffer_copy(packet)

