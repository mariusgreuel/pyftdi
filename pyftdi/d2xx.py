# Copyright (C) 2022 Marius Greuel
#
# SPDX-License-Identifier: BSD-3-Clause

"""libusb emulation backend for FTDI D2XX driver."""

from sys import platform
from logging import getLogger
from ctypes import (
    cdll,
    CFUNCTYPE,
    POINTER,
    c_ubyte,
    c_ushort,
    c_uint,
    c_ulong,
    c_void_p,
    c_char_p,
    byref,
    cast,
    create_string_buffer,
)
import usb.backend
from usb.core import Device as USBError
from usb.util import DESC_TYPE_STRING
from pyftdi.ftdi import Ftdi

__author__ = "Marius Greuel"

__all__ = ["get_backend"]

_logger = getLogger("pyftdi.d2xx")

_lib = None
CreateEventW = None
WaitForSingleObject = None
FT_CreateDeviceInfoList = None
FT_GetDeviceInfoDetail = None
FT_OpenEx = None
FT_Close = None
FT_ResetDevice = None
FT_SetDtr = None
FT_ClrDtr = None
FT_SetRts = None
FT_ClrRts = None
FT_Purge = None
FT_SetFlowControl = None
FT_SetBaudRate = None
FT_GetModemStatus = None
FT_SetChars = None
FT_SetLatencyTimer = None
FT_GetLatencyTimer = None
FT_SetBitMode = None
FT_SetTimeouts = None
FT_SetUSBParameters = None
FT_SetEventNotification = None
FT_GetStatus = None
FT_GetQueueStatus = None
FT_Read = None
FT_Write = None
FT_ReadEE = None
FT_WriteEE = None
FT_EraseEE = None

_IN = 1
_OUT = 2

FT_OK = 0

FT_OPEN_BY_SERIAL_NUMBER = 1

FT_EVENT_RXCHAR = 1

FT_PURGE_RX = 1
FT_PURGE_TX = 2

UCHAR = c_ubyte
USHORT = c_ushort
WORD = c_ushort
DWORD = c_uint
FT_STATUS = c_ulong
FT_HANDLE = c_void_p


def _load_library(_):
    try:
        if platform.startswith("win"):
            path = "ftd2xx.dll"
        else:
            path = "ftd2xx.so"
        _logger.info("Loading library: %s", path)
        return cdll.LoadLibrary(path)
    except OSError as ex:
        _logger.error(
            "Failed to load FTDI D2XX driver. You may need to reinstall the FTDI drivers: %s",
            ex,
        )
        raise FileNotFoundError(f"Failed to load FTDI D2XX driver: {ex}")


def _load_imports():
    global CreateEventW
    global WaitForSingleObject
    global FT_CreateDeviceInfoList
    global FT_GetDeviceInfoDetail
    global FT_OpenEx
    global FT_Close
    global FT_ResetDevice
    global FT_SetDtr
    global FT_ClrDtr
    global FT_SetRts
    global FT_ClrRts
    global FT_Purge
    global FT_SetFlowControl
    global FT_SetBaudRate
    global FT_GetModemStatus
    global FT_SetChars
    global FT_SetLatencyTimer
    global FT_GetLatencyTimer
    global FT_SetBitMode
    global FT_SetTimeouts
    global FT_SetUSBParameters
    global FT_SetEventNotification
    global FT_GetStatus
    global FT_GetQueueStatus
    global FT_Read
    global FT_Write
    global FT_ReadEE
    global FT_WriteEE
    global FT_EraseEE

    CreateEventW = cdll.kernel32.CreateEventW
    WaitForSingleObject = cdll.kernel32.WaitForSingleObject

    FT_CreateDeviceInfoList = _ft_function(
        "FT_CreateDeviceInfoList", (_OUT, POINTER(DWORD), "lpdwNumDevs")
    )
    FT_GetDeviceInfoDetail = _ft_function(
        "FT_GetDeviceInfoDetail",
        (_IN, DWORD, "dwIndex"),
        (_OUT, POINTER(DWORD), "lpdwFlags"),
        (_OUT, POINTER(DWORD), "lpdwType"),
        (_OUT, POINTER(DWORD), "lpdwID"),
        (_OUT, POINTER(DWORD), "lpdwLocId"),
        (_IN, c_char_p, "pszSerialNumber"),
        (_IN, c_char_p, "pszDescription"),
        (_OUT, POINTER(FT_HANDLE), "pftHandle"),
    )
    FT_OpenEx = _ft_function(
        "FT_OpenEx",
        (_IN, c_char_p, "lpSerialNumber"),
        (_IN, DWORD, "dwFlags"),
        (_OUT, POINTER(FT_HANDLE), "pHandle"),
    )
    FT_Close = _ft_function("FT_Close", (_IN, FT_HANDLE, "ftHandle"))
    FT_ResetDevice = _ft_function("FT_ResetDevice", (_IN, FT_HANDLE, "ftHandle"))
    FT_SetDtr = _ft_function("FT_SetDtr", (_IN, FT_HANDLE, "ftHandle"))
    FT_ClrDtr = _ft_function("FT_ClrDtr", (_IN, FT_HANDLE, "ftHandle"))
    FT_SetRts = _ft_function("FT_SetRts", (_IN, FT_HANDLE, "ftHandle"))
    FT_ClrRts = _ft_function("FT_ClrRts", (_IN, FT_HANDLE, "ftHandle"))
    FT_Purge = _ft_function(
        "FT_Purge",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwMask"),
    )
    FT_SetFlowControl = _ft_function(
        "FT_SetFlowControl",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, USHORT, "usFlowControl"),
        (_IN, UCHAR, "uXon"),
        (_IN, UCHAR, "uXoff"),
    )
    FT_SetBaudRate = _ft_function(
        "FT_SetBaudRate",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwBaudRate"),
    )
    FT_GetModemStatus = _ft_function(
        "FT_GetModemStatus",
        (_IN, FT_HANDLE, "ftHandle"),
        (_OUT, POINTER(DWORD), "lpdwModemStatus"),
    )
    FT_SetChars = _ft_function(
        "FT_SetChars",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, UCHAR, "ucEventChar"),
        (_IN, UCHAR, "ucEventCharEnabled"),
        (_IN, UCHAR, "ucErrorChar"),
        (_IN, UCHAR, "ucErrorCharEnabled"),
    )
    FT_SetLatencyTimer = _ft_function(
        "FT_SetLatencyTimer",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, UCHAR, "ucTimer"),
    )
    FT_GetLatencyTimer = _ft_function(
        "FT_GetLatencyTimer",
        (_IN, FT_HANDLE, "ftHandle"),
        (_OUT, POINTER(UCHAR), "pucTimer"),
    )
    FT_SetBitMode = _ft_function(
        "FT_SetBitMode",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, UCHAR, "ucMask"),
        (_IN, UCHAR, "ucEnable"),
    )
    FT_SetTimeouts = _ft_function(
        "FT_SetTimeouts",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwReadTimeout"),
        (_IN, DWORD, "dwWriteTimeout"),
    )
    FT_SetUSBParameters = _ft_function(
        "FT_SetUSBParameters",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwInTransferSize"),
        (_IN, DWORD, "dwOutTransferSize"),
    )
    FT_SetEventNotification = _ft_function(
        "FT_SetEventNotification",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwEventMask"),
        (_IN, c_void_p, "pvArg"),
    )
    FT_GetStatus = _ft_function(
        "FT_GetStatus",
        (_IN, FT_HANDLE, "ftHandle"),
        (_OUT, POINTER(DWORD), "dwRxBytes"),
        (_OUT, POINTER(DWORD), "dwTxBytes"),
        (_OUT, POINTER(DWORD), "dwEventDWord"),
    )
    FT_GetQueueStatus = _ft_function(
        "FT_GetQueueStatus",
        (_IN, FT_HANDLE, "ftHandle"),
        (_OUT, POINTER(DWORD), "dwRxBytes"),
    )
    FT_Read = _ft_function(
        "FT_Read",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, POINTER(c_ubyte), "lpBuffer"),
        (_IN, DWORD, "dwBytesToRead"),
        (_OUT, POINTER(DWORD), "lpdwBytesReturned"),
    )
    FT_Write = _ft_function(
        "FT_Write",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, POINTER(c_ubyte), "lpBuffer"),
        (_IN, DWORD, "dwBytesToWrite"),
        (_OUT, POINTER(DWORD), "lpdwBytesWritten"),
    )
    FT_ReadEE = _ft_function(
        "FT_ReadEE",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwWordOffset"),
        (_OUT, POINTER(WORD), "lpwValue"),
    )
    FT_WriteEE = _ft_function(
        "FT_WriteEE",
        (_IN, FT_HANDLE, "ftHandle"),
        (_IN, DWORD, "dwWordOffset"),
        (_IN, WORD, "wValue"),
    )
    FT_EraseEE = _ft_function(
        "FT_EraseEE",
        (_IN, FT_HANDLE, "ftHandle"),
    )


def _ft_function(name, *args):
    def errcheck(result, _, args):
        _logger.debug("%s%s=%s", function.name, args, result)
        if result != FT_OK:
            raise SystemError()

        return args

    if isinstance(_lib, Exception):
        raise _lib

    argtypes = (arg[1] for arg in args)
    paramflags = tuple((arg[0], arg[2]) for arg in args)
    prototype = CFUNCTYPE(FT_STATUS, *argtypes)
    function = prototype((name, _lib), paramflags)
    function.name = name
    function.errcheck = errcheck
    return function


class _Handle:
    def __init__(self, dev, handle, rx_event):
        self.dev = dev
        self.handle = handle
        self.event_char = 0
        self.event_char_enabled = 0
        self.error_char = 0
        self.error_char_enabled = 0
        self.rx_event = rx_event


class _Device:
    def __init__(self, flags, type, dev_id, loc_id, handle, serial_number, description):
        self.flags = flags
        self.type = type
        self.dev_id = dev_id
        self.loc_id = loc_id
        self.handle = handle
        self.serial_number = serial_number
        self.description = description


class _DeviceDescriptor:
    def __init__(self, dev):
        self.bLength = 0x12
        self.bDescriptorType = 0x01
        self.bcdUSB = 0x200
        self.bDeviceClass = 0
        self.bDeviceSubClass = 0
        self.bDeviceProtocol = 0
        self.bMaxPacketSize0 = 0x40
        self.idVendor = (dev.dev_id >> 16) & 0xFFFF
        self.idProduct = dev.dev_id & 0xFFFF
        self.bcdDevice = 0x0900
        self.iManufacturer = 0x01
        self.iProduct = 0x02
        self.iSerialNumber = 0x03
        self.bNumConfigurations = 0x01

        self.address = dev.loc_id & 0xF
        self.bus = (dev.loc_id >> 4) & 0xF
        self.port_number = None
        self.port_numbers = None
        self.speed = None


class _ConfigurationDescriptor:
    def __init__(self, _):
        self.bLength = 0x09
        self.bDescriptorType = 0x02
        self.wTotalLength = 0x0020
        self.bNumInterfaces = 0x01
        self.bConfigurationValue = 0x01
        self.iConfiguration = 0x00
        self.bmAttributes = 0xA0
        self.bMaxPower = 0x2D

        self.interface = None
        self.extra = None
        self.extralen = 0
        self.extra_descriptors = None


class _InterfaceDescriptor:
    def __init__(self, _):
        self.bLength = 0x09
        self.bDescriptorType = 0x04
        self.bInterfaceNumber = 0x00
        self.bAlternateSetting = 0x00
        self.bNumEndpoints = 0x02
        self.bInterfaceClass = 0xFF
        self.bInterfaceSubClass = 0xFF
        self.bInterfaceProtocol = 0xFF
        self.iInterface = 0x02

        self.endpoint = None
        self.extra = None
        self.extralen = 0
        self.extra_descriptors = None


class _EndpointDescriptor:
    def __init__(self, _, bEndpointAddress):
        self.bLength = 0x07
        self.bDescriptorType = 0x05
        self.bEndpointAddress = bEndpointAddress
        self.bmAttributes = 0x02
        self.wMaxPacketSize = 0x0040
        self.bInterval = 0x00
        self.bRefresh = 0x00
        self.bSynchAddress = 0x00

        self.extra = None
        self.extralen = 0
        self.extra_descriptors = None


class _D2xx(usb.backend.IBackend):
    def enumerate_devices(self):
        num_devs = FT_CreateDeviceInfoList()
        for index in range(num_devs):
            lpSerialNumber = create_string_buffer(16)
            lpDescription = create_string_buffer(64)
            flags, type, dev_id, loc_id, handle = FT_GetDeviceInfoDetail(
                index, lpSerialNumber, lpDescription
            )
            serial_number = lpSerialNumber.value.decode("ascii")
            description = lpDescription.value.decode("ascii")
            _logger.info(
                "Found device: ID=%04X:%04X, serial_number='%s', description='%s'",
                dev_id & 0xFFFF,
                (dev_id >> 16) & 0xFFFF,
                serial_number,
                description,
            )
            yield _Device(
                flags, type, dev_id, loc_id, handle, serial_number, description
            )

    def get_device_descriptor(self, dev):
        _logger.debug("get_device_descriptor")
        return _DeviceDescriptor(dev)

    def get_configuration_descriptor(self, dev, config):
        _logger.debug("get_configuration_descriptor: config=%s", config)

        if config >= 1:
            raise IndexError("Invalid configuration index " + str(config))

        return _ConfigurationDescriptor(dev)

    def get_interface_descriptor(self, dev, intf, alt, config):
        _logger.debug(
            "get_interface_descriptor: intf=%s, alt=%s, config=%s", intf, alt, config
        )

        if config >= 1:
            raise IndexError("Invalid configuration index " + str(config))
        if intf >= 1:
            raise IndexError("Invalid interface index " + str(intf))
        if alt >= 1:
            raise IndexError("Invalid alternate setting index " + str(alt))

        return _InterfaceDescriptor(dev)

    def get_endpoint_descriptor(self, dev, ep, intf, alt, config):
        _logger.debug(
            "get_endpoint_descriptor: ep=%s, intf=%s, alt=%s, config=%s",
            ep,
            intf,
            alt,
            config,
        )

        if ep >= 2:
            raise IndexError("Invalid endpoint index " + str(ep))
        if config >= 1:
            raise IndexError("Invalid configuration index " + str(config))
        if intf >= 1:
            raise IndexError("Invalid interface index " + str(intf))
        if alt >= 1:
            raise IndexError("Invalid alternate setting index " + str(alt))

        if ep == 0:
            return _EndpointDescriptor(dev, 0x81)
        else:
            return _EndpointDescriptor(dev, 0x02)

    def open_device(self, dev):
        _logger.debug("open_device")
        handle = FT_OpenEx(dev.serial_number.encode("ascii"), FT_OPEN_BY_SERIAL_NUMBER)
        rx_event = CreateEventW(None, 0, 0, None)
        FT_SetTimeouts(handle, 5000, 1000)
        FT_SetEventNotification(handle, FT_EVENT_RXCHAR, rx_event)
        return _Handle(dev, handle, rx_event)

    def close_device(self, dev_handle):
        _logger.debug("close_device")
        FT_Close(dev_handle.handle)

    def set_configuration(self, dev_handle, config_value):
        _logger.debug("set_configuration: config_value=%s", config_value)

    def get_configuration(self, dev_handle):
        _logger.debug("get_configuration")
        return 1

    def claim_interface(self, dev_handle, intf):
        _logger.debug("claim_interface: intf=%s", intf)

    def release_interface(self, dev_handle, intf):
        _logger.debug("release_interface: intf=%s", intf)

    def bulk_write(self, dev_handle, ep, intf, data, timeout):
        _logger.debug("bulk_write: ep=%s, intf=%s, len=%s", ep, intf, len(data))
        c_data = (c_ubyte * len(data)).from_buffer(data)
        return FT_Write(dev_handle.handle, c_data, len(data))

    def bulk_read(self, dev_handle, ep, intf, data, timeout):
        _logger.debug("bulk_read: ep=%s, intf=%s, len=%s", ep, intf, len(data))
        if len(data) < 2:
            return 0

        status = WaitForSingleObject(dev_handle.rx_event, 10)
        if status != 0:
            return 0

        rx_bytes = FT_GetQueueStatus(dev_handle.handle)
        if rx_bytes == 0:
            return 0

        data[0] = 0
        data[1] = 0

        if rx_bytes > len(data) - 2:
            rx_bytes = len(data) - 2

        # rx_bytes = len(data) - 2

        c_data = (c_ubyte * len(data)).from_buffer(data)
        bytes_returned = FT_Read(
            dev_handle.handle, cast(byref(c_data, 2), POINTER(c_ubyte)), rx_bytes
        )
        return bytes_returned + 2

    def ctrl_transfer(
        self, dev_handle, bmRequestType, bRequest, wValue, wIndex, data, timeout
    ):
        _logger.debug(
            "ctrl_transfer: bmRequestType=0x%02X, bRequest=0x%02X, wValue=0x%04X, wIndex=0x%04X",
            bmRequestType,
            bRequest,
            wValue,
            wIndex,
        )

        if bmRequestType == 0x80:
            self._ctrl_transfer_standard(
                dev_handle, bmRequestType, bRequest, wValue, wIndex, data
            )
        elif bmRequestType == 0xC0 or bmRequestType == 0x40:
            self._ctrl_transfer_vendor(
                dev_handle, bmRequestType, bRequest, wValue, wIndex, data
            )
        else:
            raise USBError("Not implemented")

    def _ctrl_transfer_standard(
        self, dev_handle, bmRequestType, bRequest, wValue, wIndex, data
    ):
        if bRequest == 6:  # get_descriptor
            desc_index = wValue & 0xFF
            desc_type = (wValue >> 8) & 0xFF
            if desc_type == DESC_TYPE_STRING:
                if desc_index == 0:  # Language IDs
                    data[0] = 0x04
                    data[1] = 0x03
                    # 0x0409 English(US)
                    data[2] = 0x09
                    data[3] = 0x04
                    return 4
                elif desc_index == 1:  # iManufacturer
                    s = "FTDI"
                elif desc_index == 2:  # iProduct
                    s = dev_handle.dev.description
                elif desc_index == 3:  # iSerialNumber
                    s = dev_handle.dev.serial_number
                else:
                    s = None

                if not s is None:
                    data[0] = 2 * (len(s) + 1)
                    data[1] = 0x03
                    for i, c in enumerate(s.encode("utf-16-le")):
                        data[i + 2] = c
                    return data[0]

        raise USBError("Not implemented")

    def _ctrl_transfer_vendor(
        self, dev_handle, bmRequestType, bRequest, wValue, wIndex, data
    ):
        if bRequest == Ftdi.SIO_REQ_RESET:
            if wValue == Ftdi.SIO_RESET_SIO:
                FT_ResetDevice(dev_handle.handle)
                return 0
            elif wValue == Ftdi.SIO_RESET_PURGE_RX:
                FT_Purge(dev_handle.handle, FT_PURGE_RX)
                return 0
            elif wValue == Ftdi.SIO_RESET_PURGE_TX:
                FT_Purge(dev_handle.handle, FT_PURGE_TX)
                return 0
        elif bRequest == Ftdi.SIO_REQ_SET_MODEM_CTRL:
            if wValue & 0x0100:
                if wValue & 0x01:
                    FT_SetDtr(dev_handle.handle)
                else:
                    FT_ClrDtr(dev_handle.handle)
            if wValue & 0x0200:
                if wValue & 0x02:
                    FT_SetRts(dev_handle.handle)
                else:
                    FT_ClrRts(dev_handle.handle)
            return 0
        elif bRequest == Ftdi.SIO_REQ_SET_FLOW_CTRL:
            FT_SetFlowControl(dev_handle.handle, wIndex & 0xFF00, 0x11, 0x13)
            return 0
        elif bRequest == Ftdi.SIO_REQ_SET_BAUDRATE:
            FT_SetBaudRate(dev_handle.handle, 0)
            return 0
        elif bRequest == Ftdi.SIO_REQ_SET_DATA:
            pass
        elif bRequest == Ftdi.SIO_REQ_POLL_MODEM_STATUS:
            status = FT_GetModemStatus(dev_handle.handle)
            data[0] = status & 0xFF
            data[1] = (status >> 8) & 0xFF
            return 0
        elif bRequest == Ftdi.SIO_REQ_SET_EVENT_CHAR:
            dev_handle.event_char = wValue & 0xFF
            dev_handle.event_char_enabled = (wValue >> 8) & 0xFF
            FT_SetChars(
                dev_handle.handle,
                dev_handle.event_char,
                dev_handle.event_char_enabled,
                dev_handle.error_char,
                dev_handle.error_char_enabled,
            )
            return 0
        elif bRequest == Ftdi.SIO_REQ_SET_ERROR_CHAR:
            dev_handle.error_char = wValue & 0xFF
            dev_handle.error_char_enabled = (wValue >> 8) & 0xFF
            FT_SetChars(
                dev_handle.handle,
                dev_handle.event_char,
                dev_handle.event_char_enabled,
                dev_handle.error_char,
                dev_handle.error_char_enabled,
            )
            return 0
        elif bRequest == Ftdi.SIO_REQ_SET_LATENCY_TIMER:
            FT_SetLatencyTimer(dev_handle.handle, wValue)
            return 0
        elif bRequest == Ftdi.SIO_REQ_GET_LATENCY_TIMER:
            return FT_GetLatencyTimer(dev_handle.handle)
        elif bRequest == Ftdi.SIO_REQ_SET_BITMODE:
            mode = (wValue >> 8) & 0xFF
            mask = wValue & 0xFF
            FT_SetBitMode(dev_handle.handle, mask, mode)
            return 0
        elif bRequest == Ftdi.SIO_REQ_READ_PINS:
            return 0
        elif bRequest == Ftdi.SIO_REQ_READ_EEPROM:
            return FT_ReadEE(dev_handle.handle)
        elif bRequest == Ftdi.SIO_REQ_WRITE_EEPROM:
            return FT_WriteEE(dev_handle.handle)
        elif bRequest == Ftdi.SIO_REQ_ERASE_EEPROM:
            return FT_EraseEE(dev_handle.handle)

        raise USBError("Not implemented")


def get_backend(find_library=None):
    global _lib
    try:
        if _lib is None:
            _lib = _load_library(find_library)
            _load_imports()

        num_devs = FT_CreateDeviceInfoList()
        if num_devs == 0:
            return None

        return _D2xx()
    except Exception:
        _logger.error("Error loading pyftdi.d2xx backend", exc_info=True)
        return None
