from HardwareList import HardwareList
import time
import logging
import RPi.GPIO as GPIO


class Control_Relais:
    def __init__(self, relaispin , bit_relaisopen):
        self.relaispin = relaispin
        self.bit_relaisopen = bit_relaisopen

    def initialise_relais(self):

        default = not self.bit_relaisopen
        self.relaispin.update({"default": default})
        HardwareList.initialise_pin(self.relaispin)

    def open(self):
        HardwareList.setValue(self.relaispin, self.bit_relaisopen)

    def close(self):
        HardwareList.setValue(self.relaispin, not self.bit_relaisopen)
