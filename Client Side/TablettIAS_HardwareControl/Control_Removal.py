from HardwareList import HardwareList
from Connection_Database import Connection_Database as connDB
import RPi.GPIO as GPIO
import time

"""
dictlastAlarm = {"extractID" : , "the extraction id in the database", "Location": , "State" : "A string which represents the state" }
"""

class Control_Removal:
    def __init__(self, removalPin, connDatabase):
        self.removalPin = removalPin;
        self.lastAlarm = None
        self.connDatabase = connDatabase;
        self.counter = 0
        self.lastmotion = time.localtime()

    def initialisePinRemoval(self):
        HardwareList.initialise_pin(self.removalPin)

    def activateCallback(self):
        self.deactivateCallback()
        GPIO.add_event_detect(self.removalPin.get("Pin"), GPIO.RISING, callback = self.callbackRemoval)

    def deactivateCallback(self):
        GPIO.remove_event_detect(self.removalPin.get("Pin"))

    def setlastAlarm(self, lastAlarm):
        self.lastAlarm = lastAlarm


    def callbackRemoval(self, channel):
        self.counter = self.counter+1
        stamp = time.localtime()
        print(" \n Python:There was a motion: "+str(self.counter) +"\n")
        self.lastmotion = stamp
        if self.lastAlarm is not None:
            if self.lastAlarm.get('State') == 'Opened':
                self.lastAlarm['State'] = 'Pills_detected'
                self.connDatabase.update_extraction_pillfall(self.lastAlarm.get('extractID'), stamp, 'Pills_detected')
            elif self.lastAlarm.get('State') == 'Pills_detected':
                la = self.lastAlarm
                la['State'] = 'Removed'
                self.deactivateCallback()
                self.connDatabase.update_extraction_removed(self.lastAlarm.get('extractID'), stamp, 'Pills_removed')
            else:
                self.deactivateCallback()
        else:
            self.deactivateCallback()


if __name__ == "__main__":
    defaultpins = HardwareList.get_Pins_from_json()
    motionpins = defaultpins.get("Motion")

    removal = Control_Removal(motionpins, None)
    removal.initialisePinRemoval()
    removal.activateCallback()
    print('Hallo')

    input("Ende")
    HardwareList.reset_MCPS()
    HardwareList.reset_rpi_pins()
