# -*- coding: utf-8 -*-
"""
Created on November 2020

@author: laichinger

updated by: mahfouz Mon Nov 17 17:46:12 2022

Discription: This software component is responsible for controlling the LEDs brightness.

Updates: 
    - Adding extract_control_signal method to the existing Control_LEDs class to control the LEDs
      output brightness based on the control signal coming from the server.            
"""

from HardwareList import HardwareList
from Control_Detection import Control_Detection
import time
import csv
import os
import math
class Control_LED:
    """
        Class to control the LEDs on the Portexpander
        """
    """
    be careful if you change Pins, if you set them to output and a switch is connected to it, you can destroy the RaspberryPi,
    because it may be connected to ground and take to much current    
    """


    def __init__(self, dictLEDPins):
        self.dictLEDPins = dictLEDPins
        self.control_signals_path='control_signals_'

    def initialise_LED(self):

        HardwareList.initialise_i2c()
        HardwareList.initialise_mcp()

        for x in self.dictLEDPins:
            for y in self.dictLEDPins.get(x):
                HardwareList.initialise_pin(self.dictLEDPins.get(x).get(y))

    def turn_on_all(self):
        for x in self.dictLEDPins:
            print(x)
            for y in self.dictLEDPins.get(x):
                HardwareList.setValue(self.dictLEDPins.get(x).get(y), 1)

    def turn_off_all(self):
        for x in self.dictLEDPins:
            for y in self.dictLEDPins.get(x):
                HardwareList.setValue(self.dictLEDPins.get(x).get(y), 0)

    def setLED(self , weekday , color , value):
        HardwareList.setValue(self.dictLEDPins.get(weekday).get(color), value)

    def turn_off_weekday(self, weekday):
        self.setLED(weekday , "Red" , 0)
        self.setLED(weekday ,"Green" , 0)
        self.setLED(weekday , "Blue", 0 )

    def show_detection_status_weekday(self , weekday , value):
        #print("Python: LED  weekday: "+ str(weekday)+ " val: "+str(value))
        self.setLED(weekday , "Red" , not value)
        self.setLED(weekday ,"Green" , value)
        self.setLED(weekday , "Blue", 0 )

    def show_detection_status(self, dictDetect):
        for x in dictDetect:
            value = dictDetect.get(x)
            self.setLED(x , "Red" , not value)
            self.setLED(x ,"Green" , value)
            self.setLED(x , "Blue", 0 )

    def show_led(self, dictShow):
        allowed_values = [0 , 1]
        for weekday in dictShow:
            pinsweekday = self.dictLEDPins.get(weekday)
            # check if pin dictionary exists
            if pinsweekday is not None:
                colours = dictShow.get(weekday)
                for colour in colours:
                    ledpin = pinsweekday.get(colour)
                    value = colours.get(colour)
                    # check if value is allowd and if the pin exists
                    if (value in allowed_values) and ledpin is not None:
                        HardwareList.setValue(ledpin, value)

    def turn_on_blue(self):
        for x in self.dictLEDPins:
            #self.setLED(x , "Red" , 0)
            #self.setLED(x ,"Green" , 0)
            self.setLED(x , "Blue", 1 )
    def turn_off_blue(self):
        for x in self.dictLEDPins:
            #self.setLED(x , "Red" , 0)
            #self.setLED(x ,"Green" , 0)
            self.setLED(x , "Blue", 0 )
    def extract_control_signal(self,daytime):
          """LEDs Control"""
          path=self.control_signals_path + daytime + '.csv'
          isExist=os.path.exists(path)
          # print(isExist)
          LEDs_signal=0
          if (isExist):
            with open(path, 'r') as file:
                 csvreader = csv.reader(file) 
                 i=0
                 for row in csvreader:
                   if (i==0):
                     header=row
                   else:
                     data=row
                   i=i+1
                 i=0
            #print(header)
            #print(data)
            for element in header:
                if str(element)=="LEDs_control":
                    #print ("Debug")
                    #print (data[i])
                    LEDs_signal= int(math.ceil(float(str(data[i]))))
                i=i=1
            return 5+LEDs_signal
          else:
              return 0
if __name__ == '__main__':

    defaultpins = HardwareList.get_Pins_from_json()

    LEDpins = defaultpins.get("LED")
    DetPins = defaultpins.get("Detection")

    LED = Control_LED(LEDpins)
    Det = Control_Detection(DetPins, 1)
    
    Det.initialise_det()
    LED.initialise_LED()
    LED.turn_on_all()
    time.sleep(5)
    LED.turn_off_all()

    for x in range(0,10):
        dictdet = Det.get_magazines_in_Dispenser()
        print(str(dictdet))
        LED.show_detection_status(dictdet.get("status" , None))
        time.sleep(5)

    input("Test")
    HardwareList.reset_MCPS()
    HardwareList.reset_rpi_pins()

    
