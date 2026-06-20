from HardwareList import HardwareList
import time
import logging
import RPi.GPIO as GPIO

class ControlMotor:


    def __init__(self, motorname : str , motorpins: dict , dictstepwidth : dict, invertrotation : bool, enablebitvalue : bool, \
                 position : int  , stepwidth : int,  pitchperrotation :float, fullstepsperrotation : int, targetrotationspeed : float, \
                 kalibreached : bool, posmax : int, posmin: int = 0  ):
        self.motorname = motorname
        self.motorpins = motorpins
        self.dictstepwidth = dictstepwidth
        self.invertrotation = invertrotation
        self.enablebitvalue = enablebitvalue
        self.stepwidth = stepwidth
        self.position = position
        self.pitchperrotation = pitchperrotation
        self.fullstepsperrotation = fullstepsperrotation
        self.targetrotationspeed = targetrotationspeed
        self.minwaittime = self.wait_period_outof_roationspeed(targetrotationspeed, stepwidth, fullstepsperrotation)
        self.movingallowed = False
        self.stepstomove = 0
        self.posmax = posmax
        self.posmin = posmin
        self.steppinnumber = motorpins.get("Step").get("Pin")
        self.kalibpinnumber = motorpins.get("Kalibration").get("Pin")
        self.kalibreached = kalibreached

    def initialise_motor(self):
        HardwareList.initialise_i2c()
        HardwareList.initialise_mcp()

        for x in self.motorpins:
            HardwareList.initialise_pin(self.motorpins.get(x))
        self.set_stepwidth(self.stepwidth)
        self.disable()

    @staticmethod
    def wait_period_outof_roationspeed(rotationspeed: float , stepwidth : int , fullstepsperrotation: float):
        return (60 / (rotationspeed*stepwidth*fullstepsperrotation*2))


    def get_posmin_in_steps(self):
        return self.get_distance_in_steps(self.posmin)

    def get_posmax_in_steps(self):
        return self.get_distance_in_steps(self.posmax)

    def set_stepwidth(self, stepwidth: int):
        return_val = True
        dict_step = self.dictstepwidth.get(stepwidth)
        for x in dict_step:
            pin = self.motorpins.get(x)
            value = dict_step.get(x)
            logging.debug('Set '+str(x)+' for '+str(self.motorname)+' to '+str(value)+' on pin '+str(pin)+'')
            HardwareList.setValue(pin, value)
            self.stepwidth = stepwidth
            self.minwaittime = self.wait_period_outof_roationspeed(self.targetrotationspeed, self.stepwidth, self.fullstepsperrotation)
            time.sleep(0.0001)
            
    def set_targetrotationspeed(self, targetrotationspeed):
        self.targetrotationspeed = targetrotationspeed
        self.minwaittime = self.wait_period_outof_roationspeed(self.targetrotationspeed, self.stepwidth, self.fullstepsperrotation)



    def set_direction(self, direction : bool):
        pin = self.motorpins.get('Direction')
        HardwareList.setValue(pin, direction ^ self.invertrotation)
        
    def get_direction(self):
        pin = self.motorpins.get('Direction')
        logging.debug('Get direction for ' + str(self.motorname) + '  on pin ' + str(pin) + '')
        direction = HardwareList.getValue(pin)
        direction = direction ^ self.invertrotation
        return direction


    def isenabled(self):
        pin = self.motorpins.get('Enable')
        if HardwareList.getValue(pin) == self.enablebitvalue:
            return True

        return False

    def enable(self):
        pin = self.motorpins.get('Enable')
        HardwareList.setValue(pin, self.enablebitvalue)
        time.sleep(0.000001)



    def disable(self):
        pin = self.motorpins.get('Enable')
        HardwareList.setValue(pin, not self.enablebitvalue)
        time.sleep(0.000001)


    def direction_out_of_steps(self, steps):
        return steps > 0
    
    def set_direction_out_of_steps(self,steps):
        self.set_direction(self.direction_out_of_steps(steps))
                
    def get_distance_in_mm(self, distance_steps):
        return (distance_steps * self.pitchperrotation / (self.fullstepsperrotation * 32))
        
    def get_distance_in_steps(self, distance_mm):
        return round((distance_mm * self.fullstepsperrotation * 32) / self.pitchperrotation)
        
    def set_step_pin(self, value):
        GPIO.output(self.steppinnumber, value)
    def get_step_pin(self, value):
        GPIO.input(self.steppinnumber)

    def get_kalibration(self):
        return GPIO.input(self.kalibpinnumber)
        
    def calibrate_sub(self , invertkalib = 0):
        step = 0
        add = round(32/self.stepwidth)
        loop = True
        pin = 0
        kalibreached = self.kalibreached^invertkalib
        lasttime = time.monotonic()
        waittime = self.minwaittime
        steppin = self.steppinnumber
        kaibpin = self.kalibpinnumber
        pin = GPIO.input(steppin)


        self.set_direction(invertkalib)

        while loop:
            looptime = time.monotonic()
            difftime = looptime-lasttime
            
            if loop and waittime< difftime:
                if pin == 0:
                    GPIO.output(steppin, 1)
                    lasttime = time.monotonic()
                    pin = 1
                    step = step + add
                else:
                    GPIO.output(steppin, 0)
                    pin = 0
                    lasttime = time.monotonic()
                    if GPIO.input(kaibpin) == kalibreached: 
                        loop = False
        return step
        
    def calibrate(self):
        step = 0
        step = step+ self.calibrate_sub(0)
        step = step- self.calibrate_sub(1)
        time.sleep(0.001)
        step = step+ self.calibrate_sub(0)
        return step
        











if __name__ == '__main__':
    print('Hello')

    defaultpins = HardwareList.get_Pins_from_json()
    print(defaultpins.get('Motor2'))
    print(defaultpins.get('Motor1'))
    Motor2 = ControlMotor(motorname = 'Motor2',  motorpins = defaultpins.get('Motor2'),
                          dictstepwidth = HardwareList.DRV8825_dictstepwidth, invertrotation = 0, enablebitvalue = 0,
                          position = 0  , stepwidth = 32 , pitchperrotation = 10,
                          fullstepsperrotation = 200, targetrotationspeed = 200,
                          kalibreached = 0,
                          posmax = 150,
                          posmin = 0 )
    Motor1 = ControlMotor(motorname = 'Motor1',  motorpins = defaultpins.get('Motor1'),
                          dictstepwidth = HardwareList.DRV8825_dictstepwidth, invertrotation = 0, enablebitvalue = 0,
                          position = 0  , stepwidth = 32 , pitchperrotation = 10,
                          fullstepsperrotation = 200, targetrotationspeed = 200,
                          kalibreached = 0,
                          posmax = 150,
                          posmin = 0 )
    Motor2.initialise_motor()
    Motor1.initialise_motor()
    
    











