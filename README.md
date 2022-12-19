[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://vshymanskyy.github.io/StandWithUkraine)

# PyFtdiWin

![Python package](https://github.com/eblot/pyftdi/workflows/Python%20package/badge.svg)
![Mock tests](https://github.com/eblot/pyftdi/workflows/Python%20mock%20tests/badge.svg)
![Syntax tests](https://github.com/eblot/pyftdi/workflows/Python%20syntax%20tests/badge.svg)
[![StandWithUkraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://vshymanskyy.github.io/StandWithUkraine)

[![PyPI](https://img.shields.io/pypi/v/pyftdi.svg?maxAge=2592000)](https://pypi.org/project/pyftdi/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyftdi.svg)](https://pypi.org/project/pyftdi/)
[![Downloads](https://img.shields.io/pypi/dm/pyftdi.svg)](https://pypi.org/project/pyftdi/)

## PyFtdiWin vs. PyFtdi

PyFtdiWin is a fork of PyFtdi. The design objective of the PyFtdiWin fork
is to support the default Windows plug-and-play drivers provided by FTDI.

PyFtdi only supports libusb-compatible drivers, which requires you to swap
the official drivers for a libusb-compatible driver using Zadig.
As Windows serial ports and many other tools expect the default
FTDI drivers, you will find yourself swapping drivers back-and-forth when
using PyFtdi with your FTDI devices.

## Overview

PyFtdi aims at providing a user-space driver for popular FTDI devices,
implemented in pure Python language.

Suported FTDI devices include:

* UART and GPIO bridges

  * FT232R (single port, 3Mbps)
  * FT230X/FT231X/FT234X (single port, 3Mbps)

* UART, GPIO and multi-serial protocols (SPI, I2C, JTAG) bridges

  * FT2232C/D (dual port, clock up to 6 MHz)
  * FT232H (single port, clock up to 30 MHz)
  * FT2232H (dual port, clock up to 30 MHz)
  * FT4232H (quad port, clock up to 30 MHz)

## Features

PyFtdi currently supports the following features:

* UART/Serial USB converter, up to 12Mbps (depending on the FTDI device
  capability)
* GPIO/Bitbang support, with 8-bit asynchronous, 8-bit synchronous and
  8-/16-bit MPSSE variants
* SPI master, with simultanous GPIO support, up to 12 pins per port,
  with support for non-byte sized transfer
* I2C master, with simultanous GPIO support, up to 14 pins per port
* Basic JTAG master capabilities
* EEPROM support (some parameters cannot yet be modified, only retrieved)
* Experimental CBUS support on selected devices, 4 pins per port

## Supported host OSes

* macOS
* Linux
* FreeBSD
* Windows

## License

`SPDX-License-Identifier: BSD-3-Clause`

## Warnings

### Python support

PyFtdi requires Python 3.7+.

See `pyftdi/doc/requirements.rst` for more details.
