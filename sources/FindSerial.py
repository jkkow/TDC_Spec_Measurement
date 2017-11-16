# This module searches available serial ports and find the target port by name of the device.
# Created on 2017-06-01
# author: jkkow

import sys
import serial
import win32com.client


def serialport_info():
    """
    Returns list of available serial ports in the Windows system.
    Each list element is name of 'Win32_SerialPort'
    """
    wmi = win32com.client.GetObject("winmgmts:")
    port_list = []

    for serial in wmi.InstancesOf("Win32_SerialPort"):
        port_list.append(serial.Name)

    return port_list


def COMports_available():
    """
    Returns COM ports number list that is available in the Windows system.
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(100)]
    else:
        raise EnvironmentError('Unsupported platform')

    port_avail = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            port_avail.append(port)
        except (OSError, serial.SerialException):
            pass

    return port_avail


def find_device_index(Name):
    """
    Retruns index of an element that includes argument 'Name'
    among the device list of connected serial ports.
    """
    port_list = serialport_info()
    num_of_ports = len(port_list)

    check = 0
    for device in port_list:
        if device.find(Name) >= 0:
            break
        check += 1
    if check == num_of_ports:
        return None
    else:
        return check


class my_serial(serial.Serial):

    def __init__(self, name, boudrate):
        self.name = name
        self.boudrate = boudrate

        self.port_list = serialport_info()
        self.COM_list = COMports_available()
        print("\n\tAvailable COM ports: ", self.COM_list)

        self.dvice_idx = find_device_index(self.name)

        try:
            self.Target_COM = self.COM_list[self.dvice_idx]
            print("\n\tThe port for the '%s': " % self.name, self.Target_COM)
            port_exist = True
        except (TypeError, AttributeError):
            print("\nNo serial port related to device name '%s'." % self.name)
            port_exist = False

        if port_exist:
            self.serialport = serial.Serial(self.Target_COM, self.boudrate)
            print("\n\tThe Device connected? ", self.serialport.isOpen())
