
import logging
import board
import busio
import digitalio
import time
import json
from adafruit_mcp230xx.mcp23017 import MCP23017
import RPi.GPIO as GPIO
import os
import sys



class HardwareList:
    """
    Class to access the GPIOS and get a Pinmapping to the function,
    """
    """
    be careful if you change Pins, if you set them to output and a switch is connected to it, you can destroy the RaspberryPi,
    because it may be connected to ground and take to much current    
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d:%(funcName)s] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.WARNING)


    # after initialisation_i2c the i2c object is stored in this dict
    i2c = None

    # after initialisation_mcp both mcp objects are stored in this dict
    dictMCP = None

    dictMCPReset =  {'mcp1': {'Pin': 4, 'device': 'rpi', 'direction': 'INPUT', 'default': 'PULLUP'},
                     'mcp2': {'Pin': 18, 'device': 'rpi', 'direction': 'INPUT', 'default': 'PULLUP'}}

    DRV8825_dictstepwidth = {1: {'M2': 0, 'M1': 0, 'M0': 0},
                             2: {'M2': 0, 'M1': 0, 'M0': 1},
                             4: {'M2': 0, 'M1': 1, 'M0': 0},
                             8: {'M2': 0, 'M1': 1, 'M0': 1},
                             16: {'M2': 1, 'M1': 0, 'M0': 0},
                             32: {'M2': 1, 'M1': 0, 'M0': 1}}



    #mapping of the values used here to the libraries so we can handle the MCPs as normal gpios
    dict_Direction_MCP = {'INPUT': digitalio.Direction.INPUT , 'OUTPUT' : digitalio.Direction.OUTPUT}
    dict_Direction_MCP_back = {digitalio.Direction.INPUT : 'INPUT' , digitalio.Direction.OUTPUT : 'OUTPUT' }

    #just there to check given logic level in a method exists
    dict_Level = {1 : 1 , 0: 0}

    # do not use Pulldown for the MCP23017 because it is not possible
    dict_PULL_MCP = {'PULLUP' : digitalio.Pull.UP , 'UNDEF': None}
    dict_Direction_RPI = {'INPUT': GPIO.IN , 'OUTPUT' : GPIO.OUT}
    dict_PULL_RPI = {'PULLUP' : GPIO.PUD_UP , 'PULLDOWN':  GPIO.PUD_DOWN , 'UNDEF' : GPIO.PUD_OFF}
    dict_Direction_RPI_back = {GPIO.IN: 'INPUT', GPIO.OUT: 'OUTPUT', GPIO.HARD_PWM: 'HARD_PWM'}


    def __init__(self):
        """ 

        Parameters:
        __________
       
        __________
        

        """


    @classmethod
    def initialise_i2c(cls):
        if cls.i2c is None:
            cls.i2c = busio.I2C(board.SCL, board.SDA)

    @classmethod
    def initialise_mcp(cls):
        if cls.dictMCP is None:
            cls.dictMCP = {}
            cls.reset_MCPS()
            cls.dictMCP.update({'mcp1':  MCP23017(cls.i2c, address = 0x20)})
            cls.dictMCP.update({'mcp2':  MCP23017(cls.i2c, address = 0x24)})
            




    @classmethod
    def pinnumberinrange_mcp(cls, number):
        return number in range(0, 16, 1)

    @classmethod
    def pinnumberinrange_rpi(cls, number):
        return number in range(4, 28, 1)

    @classmethod
    def initialise_pin(cls, pin):
        device = pin.get('device')
        # switch case calling the function dependend on the device
        switch = { 'rpi' : cls.initialise_pin_rpi , 'mcp1' : cls.initialise_pin_mcp, 'mcp2' : cls.initialise_pin_mcp}
        func = switch.get(device)
        func(pin)



    @classmethod
    def initialise_pin_rpi(cls,pin):
        pinnumber = pin.get('Pin')
        direction = pin.get('direction')
        default = pin.get('default')
        if direction == 'INPUT':
            GPIO.setup(pinnumber, cls.dict_Direction_RPI.get(direction), cls.dict_PULL_RPI.get(default) )
        elif direction == 'OUTPUT':
            GPIO.setup(pinnumber, cls.dict_Direction_RPI.get(direction), initial = default)

    @classmethod
    def initialise_pin_mcp(cls,pin):
        pinnumber = pin.get('Pin')
        device = pin.get('device')
        direction = pin.get('direction')
        default = pin.get('default')
        mcp = cls.dictMCP.get(device)
        mcp_pin = mcp.get_pin(pinnumber);
        pin.update({'object' : mcp_pin})
        if direction == 'INPUT' :
            mcp_pin.direction = cls.dict_Direction_MCP.get(direction)
            mcp_pin.pull = cls.dict_PULL_MCP(default)
        elif direction == 'OUTPUT':
            mcp_pin.direction = cls.dict_Direction_MCP.get(direction)
            mcp_pin.value = default



    @classmethod
    def setDirection(cls, pin , direction, default = None):
        if default is None:
            if direction == 'INPUT':
                default = 'UNDEF'
            elif direction == 'OUTPUT':
                default = 0
        device = pin.get('device')
        # switch case calling the function dependend on the device
        switch = {'rpi': cls.setDirection_rpi, 'mcp1': cls.setDirection_mcp, 'mcp2': cls.setDirection_mcp}
        func = switch.get(device)
        # this should call e.g if device = 'rpi' --> cls.setDirection(...) function
        func(pin,direction,default)



    def setDirection_mcp(cls, pin, direction ,default):
        pinnumber = pin.get('Pin')
        mcp_pin = pin.get('object')
        if direction == 'INPUT':
            pin.direction = cls.dict_Direction_MCP.get(direction)
            pin.pull = cls.dict_PULL_MCP(default)

        elif direction == 'OUTPUT':
            pin.direction = cls.dict_Direction_MCP.get(direction)
            pin.value = default




    @classmethod
    def setDirection_rpi(cls, pin, direction, default):
        pinnumber = pin.get('Pin')
        if direction == 'INPUT':
            GPIO.setup(pinnumber, cls.dict_Direction_RPI.get(direction), cls.dict_PULL_RPI.get(default))
        elif direction == 'OUTPUT':
            GPIO.setup(pinnumber, cls.dict_Direction_RPI.get(direction), default)



    @classmethod
    def getDirection(cls, pin):
        device = pin.get('device')
        # switch case calling the function dependend on the device
        switch = {'rpi': cls.getDirection_rpi, 'mcp1': cls.getDirection_mcp, 'mcp2': cls.getDirection_mcp}
        func = switch.get(device)
        return func(pin)


    @classmethod
    def getDirection_rpi(cls, pin):
        pinnumber = pin.get('Pin')
        direction = GPIO.gpio_function(pinnumber)
        return cls.dict_Direction_RPI_back.get(direction,'UNKNOWN')


    @classmethod
    def getDirection_mcp(cls, pin):
        mcp_pin = pin.get('objective')
        direction = mcp_pin.direction
        return cls.dict_Direction_MCP_back.get(direction, 'UNKNOWN')


    @classmethod
    def setValue(cls, pin, value):
        device = pin.get('device')
        # switch case calling the function dependend on the device
        switch = {'rpi': cls.setValue_rpi, 'mcp1': cls.setValue_mcp, 'mcp2': cls.setValue_mcp}
        func = switch.get(device)
        func(pin, value)



    @classmethod
    def setValue_rpi(cls, pin, value):
        pinnumber = pin.get('Pin')
        GPIO.output(pinnumber, value)


    @classmethod
    def setValue_mcp(cls, pin, value):
        mcp_pin = pin.get('object')
        mcp_pin.value = value



    @classmethod
    def getValue(cls, pin):
        device = pin.get('device')
        # switch case calling the function dependent on the device
        switch = {'rpi': cls.getValue_rpi, 'mcp1': cls.getValue_mcp, 'mcp2': cls.getValue_mcp}
        func = switch.get(device)
        # this should call e.g if device = 'rpi' --> cls.setDirection(...) function
        return func(pin)



    @classmethod
    def getValue_mcp(cls, pin):
        mcp_pin = pin.get('object')
        return mcp_pin.value


    @classmethod
    def getValue_rpi(cls, pin):
            pinnumber = pin.get('Pin')
            return GPIO.input(pinnumber)

    @classmethod
    def get_Pins_from_json(cls):
        with open('defaultPins_init.json') as json_file:
            data = json.load(json_file)
            return data

    @classmethod
    def reset_MCPS(cls):
        for x in cls.dictMCPReset:
            resetPin = cls.dictMCPReset.get(x)
            resetPin.update({'default': 'PULLDOWN'})
            cls.initialise_pin_rpi(resetPin)
            resetPin.update({'default': 'PULLUP'})
        time.sleep(0.0000001)
        for x in cls.dictMCPReset:
            resetPin = cls.dictMCPReset.get(x)
            cls.initialise_pin_rpi(resetPin)

    @classmethod
    def reset_rpi_pins(cls):
        with open('defaultPins_reset.json') as json_file:
            data = json.load(json_file)
            for x in data:
                for y in data.get(x):
                    cls.initialise_pin_rpi(data.get(x).get(y))

if __name__ == "__main__":
    os.chdir(sys.path[0])
    print(str(os.getcwd()))
    HardwareList.reset_MCPS()
    HardwareList.reset_rpi_pins()
    data = HardwareList.get_Pins_from_json()
    print('resetted all pins')














