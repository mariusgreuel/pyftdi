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
    c_int,
    c_uint,
    c_ulong,
    c_void_p,
    c_char_p,
    create_string_buffer
)
import usb.backend
from usb.core import Device as USBError
from usb.util import DESC_TYPE_STRING

__author__ = "Marius Greuel"

__all__ = ["get_backend"]

_logger = getLogger("pyftdi.d2xx")

_lib = None
FT_CreateDeviceInfoList = None
FT_GetDeviceInfoDetail = None
FT_OpenEx = None
FT_Close = None

_IN = 1
_OUT = 2

FT_OK = 0

FT_OPEN_BY_SERIAL_NUMBER = 1

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
        return FileNotFoundError(f"Failed to load FTDI D2XX driver: {ex}")


def _load_imports():
    global FT_CreateDeviceInfoList
    global FT_GetDeviceInfoDetail
    global FT_OpenEx
    global FT_Close

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
        (_IN, c_char_p, "lpSerialNumber"),
        (_IN, c_char_p, "lpDescription"),
        (_OUT, POINTER(FT_HANDLE), "pftHandle"),
    )
    FT_OpenEx = _ft_function(
        "FT_OpenEx", (_IN, c_char_p, "lpSerialNumber"), (_IN, DWORD, "dwFlags"), (_OUT, POINTER(FT_HANDLE), "pHandle")
    )
    FT_Close = _ft_function(
        "FT_Close", (_IN, FT_HANDLE, "ftHandle")
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
    def __init__(self, dev, handle):
        self.dev = dev
        self.handle = handle

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
        dwNumDevs = FT_CreateDeviceInfoList()
        for index in range(dwNumDevs):
            lpSerialNumber = create_string_buffer(16)
            lpDescription = create_string_buffer(64)
            flags, type, dev_id, loc_id, handle = FT_GetDeviceInfoDetail(index, lpSerialNumber, lpDescription)
            serial_number = lpSerialNumber.value.decode("ascii")
            description = lpDescription.value.decode("ascii")
            _logger.info("Found device 0x%08X (%s), '%s'", dev_id, serial_number, description)
            yield _Device(flags, type, dev_id, loc_id, handle, serial_number, description)

    def get_device_descriptor(self, dev):
        _logger.info("get_device_descriptor")
        return _DeviceDescriptor(dev)

    def get_configuration_descriptor(self, dev, config):
        _logger.info("get_configuration_descriptor: config=%s", config)

        if config >= 1:
            raise IndexError('Invalid configuration index ' + str(config))

        return _ConfigurationDescriptor(dev)

    def get_interface_descriptor(self, dev, intf, alt, config):
        _logger.info("get_interface_descriptor: intf=%s, alt=%s, config=%s", intf, alt, config)

        if config >= 1:
            raise IndexError('Invalid configuration index ' + str(config))
        if intf >= 1:
            raise IndexError('Invalid interface index ' + str(intf))
        if alt >= 1:
            raise IndexError('Invalid alternate setting index ' + str(alt))

        return _InterfaceDescriptor(dev)

    def get_endpoint_descriptor(self, dev, ep, intf, alt, config):
        _logger.info("get_endpoint_descriptor: ep=%s, intf=%s, alt=%s, config=%s", ep, intf, alt, config)

        if ep >= 2:
            raise IndexError('Invalid endpoint index ' + str(ep))
        if config >= 1:
            raise IndexError('Invalid configuration index ' + str(config))
        if intf >= 1:
            raise IndexError('Invalid interface index ' + str(intf))
        if alt >= 1:
            raise IndexError('Invalid alternate setting index ' + str(alt))

        if ep == 0:
            return _EndpointDescriptor(dev, 0x81)
        else:
            return _EndpointDescriptor(dev, 0x02)

    def open_device(self, dev):
        _logger.info("open_device")
        return _Handle(dev, FT_OpenEx(dev.serial_number.encode("ascii"), FT_OPEN_BY_SERIAL_NUMBER))

    def close_device(self, dev_handle):
        _logger.info("close_device")
        FT_Close(dev_handle.handle)

    def set_configuration(self, dev_handle, config_value):
        _logger.info("set_configuration: config_value=%s", config_value)

    def get_configuration(self, dev_handle):
        _logger.info("get_configuration")
        return 1

    def claim_interface(self, dev_handle, intf):
        _logger.info("claim_interface: intf=%s", intf)

    def release_interface(self, dev_handle, intf):
        _logger.info("release_interface: intf=%s", intf)

    def bulk_write(self, dev_handle, ep, intf, data, timeout):
        _logger.info("bulk_write: ep=%s, intf=%s, len=%s", ep, intf, len(data))

    def bulk_read(self, dev_handle, ep, intf, data, timeout):
        _logger.info("bulk_read: ep=%s, intf=%s, len=%s", ep, intf, len(data))

    def ctrl_transfer(self,
                      dev_handle,
                      bmRequestType,
                      bRequest,
                      wValue,
                      wIndex,
                      data,
                      timeout):
        _logger.info("ctrl_transfer: bmRequestType=0x%02X, bRequest=0x%02X, wValue=0x%04X, wIndex=0x%04X", bmRequestType, bRequest, wValue, wIndex)

        if bmRequestType == 0x80 and bRequest == 6: # get_descriptor
            desc_index = wValue & 0xFF
            desc_type = (wValue >> 8) & 0xFF
            if desc_type == DESC_TYPE_STRING:
                if desc_index == 0: # Language IDs
                    data[0] = 0x04
                    data[1] = 0x03
                    data[2] = 0x09
                    data[3] = 0x04
                    return 4
                elif desc_index == 1: # iManufacturer
                    s = "FTDI"
                elif desc_index == 2: # iProduct
                    s = dev_handle.dev.description
                elif desc_index == 3: # iSerialNumber
                    s = dev_handle.dev.serial_number
                else:
                    s = None

                if not s is None:
                    data[0] = 2 * (len(s) + 1)
                    data[1] = 0x03
                    for i, c in enumerate(s.encode("utf-16-le")):
                        data[i + 2] = c
                    return data[0]
        elif bmRequestType == 0x40 and bRequest == 0: # get_status
            return 0
        elif bmRequestType == 0x40 and bRequest == 11: # xxx
            return 0
        elif bmRequestType == 0x40 and bRequest == 9: # xxx
            return 0
        elif bmRequestType == 0x40 and bRequest == 6: # xxx
            return 0
        elif bmRequestType == 0x40 and bRequest == 7: # xxx
            return 0

        raise USBError('Not implemented')


def get_backend(find_library=None):
    global _lib
    try:
        if _lib is None:
            _lib = _load_library(find_library)
            _load_imports()

        return _D2xx()
    except Exception:
        _logger.error('Error loading pyftdi.d2xx backend', exc_info=True)
        return None
