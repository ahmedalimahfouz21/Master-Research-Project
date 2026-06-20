from HardwareList import HardwareList
from Control_Motor import ControlMotor
from Control_Relais import Control_Relais
import time
import json
import logging
import RPi.GPIO as GPIO

class Control_Actors():

    dict_bool_prefix = {0: -1, 1: 1}

    dict_weekday_number = {
                "Monday": 6,
                "Tuesday": 5,
                "Wednesday": 4,
                "Thursday": 3,
                "Friday": 2,
                "Saturday": 1,
                "Sunday": 0 ,
              }

    dict_daytime_number = {
                "morning": 57.5,
                "noon": 37.5,
                "evening": 17.5,
                "night": 0,
              }


    
    
    
    filename_position = 'position.json'
    filename_calibratetocopy = 'calibrate_tocopy.json'
    filename_calibrate = 'calibrate.json'
    filename_distance = 'distance.json'


    def __init__(self , relais_obj: Control_Relais, motor_vert_obj: ControlMotor , motor_horz_obj: ControlMotor ):
        self.relais = relais_obj
        self.motor_vert = motor_vert_obj
        self.motor_horz = motor_horz_obj
        self.steps_first_mag = {"Vertical" : 0 , "Horizontal" : 0}
        self.calibrated = False
        self.inposition = False

    def load_pos_first_mag(self):
        with open(self.filename_calibrate) as json_file:
            data = json.load(json_file)
            steps_first = data.get("Distance_to_first_Magazin")
            print(str(data))
            self.steps_first_mag.update(steps_first)
            print(str(self.steps_first_mag))

    
    def enable_motors(self):
        self.motor_vert.enable()
        self.motor_horz.enable()
        
    def disable_motors(self):
        self.motor_vert.disable()
        self.motor_horz.disable()
        
    

    def load_position(self , dict_position):
            self.motor_vert.position = dict_position.get("Vertical")
            self.motor_horz.position = dict_position.get("Horizontal")
            
    def startup(self):
        self.enable_motors()
        time.sleep(0.1)
        self.calibrate(save= False)
        self.load_pos_first_mag()
        self.motor_vert.position = self.motor_vert.get_posmin_in_steps()
        self.motor_horz.position = self.motor_horz.get_posmin_in_steps()
        time.sleep(0.1)
        self.inposition = False
        self.disable_motors()
        """
        with open(self.filename_position) as json_file:
            data = json.load(json_file)
            if data.get("Valid") == 1:
                self.load_position(data)
            else:
                self.calibrate_concurrent()
        """
                
    def position_setvalid(self , value):
        with open(self.filename_position) as json_file:
                data = json.load(json_file)
                data.update({"Valid" : value})
                json.dump(data, json_file)

    def open_mag(self,weekday, daytime):
        if self.inposition:
            self.enable_motors()
            time.sleep(0.2)
            #wait a bit till motor is stable
            self.relais.open()
        else:
            print("Python: Cannot open magazine, Magnet is not correct positioned")

    def close_mag(self):
        self.relais.close()
        # wait a bit after closing
        time.sleep(1)
        self.disable_motors()



    def move_to_magazin_concurrent(self, weekday, daytime):
        self.enable_motors()
        time.sleep(0.1)
        print(str(weekday))
        print(str(daytime))

        if (not self.calibrated):
            self.startup()
            self.calibrated = True


        pos_h = self.motor_horz.position
        pos_v = self.motor_vert.position

        first_mag_add_v = self.steps_first_mag.get("Vertical")
        first_mag_add_h = self.steps_first_mag.get("Horizontal")

        mult_vert = self.dict_weekday_number.get(weekday)
        add_horz = self.dict_daytime_number.get(daytime)
        
        print("Python : mult_vert: "+str(mult_vert)+" add_horz: "+ str(add_horz) )

        if (mult_vert is not None and add_horz is not None):
            vert_add = self.motor_vert.get_distance_in_steps(mult_vert*42)
            horz_add = self.motor_horz.get_distance_in_steps(add_horz)

            pos_to_move_v = self.motor_vert.posmin + first_mag_add_v + vert_add
            pos_to_move_h = self.motor_horz.posmin + first_mag_add_h + horz_add

            steps_vert = pos_to_move_v - pos_v
            steps_horz = pos_to_move_h - pos_h
            print("Python: old pos ver : " +str(self.motor_vert.position)+ " horz :"+str(self.motor_horz.position))
            print("Python: old pos ver : " +str(self.motor_vert.get_distance_in_mm(self.motor_vert.position)) + " horz :"+str(self.motor_horz.get_distance_in_mm(self.motor_horz.position)))
            print("Python: posmin vert: " +str(self.motor_vert.get_posmin_in_steps()) + " horz :"+str(self.motor_horz.get_posmin_in_steps()))
            print("Python: posmax vert: " +str(self.motor_vert.get_posmax_in_steps()) + " horz :"+str(self.motor_horz.get_posmax_in_steps()))
            print("Python: pos_to_move vert: " +str(pos_to_move_v) + " horz :"+str(pos_to_move_h))
            print("Python: steps vert : " +str(steps_vert) + " horz :"+str(steps_horz))

            vert_in_range = (self.motor_vert.get_posmin_in_steps() <= pos_to_move_v <= self.motor_vert.get_posmax_in_steps())
            horz_in_range = (self.motor_horz.get_posmin_in_steps() <= pos_to_move_h <= self.motor_horz.get_posmax_in_steps())
            print("Python: vert: " +str(vert_in_range) + " horz :"+str(horz_in_range))
            
            if (vert_in_range and horz_in_range):
                self.enable_motors()
                dict_moved_steps = self.move_steps_concurrent(steps_vert=steps_vert, steps_horz=steps_horz)
                self.motor_vert.position = self.motor_vert.position + dict_moved_steps.get("Vertical")
                self.motor_horz.position = self.motor_horz.position + dict_moved_steps.get("Horizontal")
                self.inposition = True
                print(str(dict_moved_steps))
                print("Python: new pos ver : " +str(self.motor_vert.position)+ " horz :"+str(self.motor_horz.position))
                print("Python: new pos ver : " +str(self.motor_vert.get_distance_in_mm(self.motor_vert.position)) + " horz :"+str(self.motor_horz.get_distance_in_mm(self.motor_horz.position)))
                
            else:
                print("Python: Positions where not in range of linear axis! Vertical: "+str(pos_to_move_v)+ "  Horizontal: "+str(pos_to_move_h))
                self.inposition = False

        time.sleep(0.1)
        self.disable_motors()

        
    def move_steps_concurrent(self, steps_vert, steps_horz):
        
        self.motor_vert.set_direction_out_of_steps(steps_vert)
        self.motor_horz.set_direction_out_of_steps(steps_horz)
        dir_vert = self.motor_vert.get_direction()
        dir_horz = self.motor_horz.get_direction()
        step_vert = abs(steps_vert)
        step_horz = abs(steps_horz)
        add_vert = round(32/self.motor_vert.stepwidth)
        add_horz = round(32/self.motor_horz.stepwidth)


        loop_vert = True
        loop_horz = True
        error = False
        pin_vert = 0
        pin_horz = 0
        kalibreached_vert = self.motor_vert.kalibreached
        kalibreached_horz = self.motor_horz.kalibreached
        lasttime_vert = time.monotonic()
        lasttime_horz = lasttime_vert
        waittime_vert = self.motor_vert.minwaittime
        waittime_horz = self.motor_horz.minwaittime
        steppin_vert = self.motor_vert.steppinnumber
        kaibpin_vert = self.motor_vert.kalibpinnumber
        steppin_horz = self.motor_horz.steppinnumber
        kaibpin_horz = self.motor_horz.kalibpinnumber
        pin_vert = GPIO.input(steppin_vert)
        pin_horz = GPIO.input(steppin_horz)
        steps_horz_moved = 0
        steps_vert_moved = 0
        
                

        while loop_vert or loop_horz:
            looptime = time.monotonic()
            difftime_vert = looptime-lasttime_vert
            difftime_horz = looptime-lasttime_horz
            
            if loop_vert and waittime_vert < difftime_vert:
                if pin_vert == 0:
                    GPIO.output(steppin_vert, 1)
                    lasttime_vert = time.monotonic()
                    pin_vert = 1
                    steps_vert_moved = steps_vert_moved + add_vert
                else:
                    GPIO.output(steppin_vert, 0)
                    pin_vert = 0
                    lasttime_vert = time.monotonic()
                    if dir_vert == 0 and GPIO.input(kaibpin_vert) == kalibreached_vert: 
                        loop_vert = False
                        error = True
                    elif step_vert <= steps_vert_moved :
                        loop_vert = False

                        
            if loop_horz and waittime_horz < difftime_horz:
                if pin_horz == 0:
                    GPIO.output(steppin_horz, 1)
                    lasttime_horz = time.monotonic()
                    pin_horz = 1
                    steps_horz_moved = steps_horz_moved + add_horz
                else:
                    GPIO.output(steppin_horz, 0)
                    pin_horz = 0
                    lasttime_horz = time.monotonic()
                    if dir_horz == 0 and GPIO.input(kaibpin_horz) == kalibreached_horz: 
                        loop_horz = False
                        error = True
                    elif step_horz <= steps_horz_moved:
                        loop_horz = False

        mult_vert = self.dict_bool_prefix.get(dir_vert, 1)
        mult_horz = self.dict_bool_prefix.get(dir_horz, 1)
        dict_pos = {"Vertical": steps_vert_moved*mult_vert , "Horizontal" : steps_horz_moved*mult_horz ,"Error": error}
        return dict_pos


        
    def calibrate(self, save = False ):
        step_vert = 0
        step_horz = 0
        dict_pos = self.calibrate_concurrent(invertkalib = 0, save = False)
        step_vert = step_vert + dict_pos.get("Vertical")
        step_horz = step_horz + dict_pos.get("Horizontal")
        dict_pos = self.calibrate_concurrent(invertkalib = 1, save = False)
        step_vert = step_vert - dict_pos.get("Vertical")
        step_horz = step_horz - dict_pos.get("Horizontal")
        time.sleep(0.001)
        dict_pos = self.calibrate_concurrent(invertkalib = 0, save = False)
        step_vert = step_vert + dict_pos.get("Vertical")
        step_horz = step_horz + dict_pos.get("Horizontal")
        print(str(step_vert) + ' : ' + str(step_horz))
        dict_pos = {"Vertical": step_vert , "Horizontal" : step_horz}
        if save == True:
            with open(self.filename_calibratetocopy, 'w') as outfile:
                json.dump(dict_pos, outfile)

        return dict_pos

    def calibrate_concurrent(self , invertkalib = 0, save = False):
        step_vert = 0
        step_horz = 0
        add_vert = round(32/self.motor_vert.stepwidth)
        add_horz = round(32/self.motor_horz.stepwidth)
        loop_vert = True
        loop_horz = True
        kalibreached_vert = self.motor_vert.kalibreached^invertkalib
        kalibreached_horz = self.motor_horz.kalibreached^invertkalib
        lasttime_vert = time.monotonic()
        lasttime_horz = lasttime_vert
        waittime_vert = self.motor_vert.minwaittime
        waittime_horz = self.motor_horz.minwaittime
        steppin_vert = self.motor_vert.steppinnumber
        kaibpin_vert = self.motor_vert.kalibpinnumber
        steppin_horz = self.motor_horz.steppinnumber
        kaibpin_horz = self.motor_horz.kalibpinnumber
        pin_vert = GPIO.input(steppin_vert)
        pin_horz = GPIO.input(steppin_horz)
        

        self.motor_vert.set_direction(invertkalib)
        self.motor_horz.set_direction(invertkalib)

        while loop_vert or loop_horz:
            looptime = time.monotonic()
            difftime_vert = looptime-lasttime_vert
            difftime_horz = looptime-lasttime_horz
            
            if loop_vert and waittime_vert < difftime_vert:
                if pin_vert == 0:
                    GPIO.output(steppin_vert, 1)
                    lasttime_vert = time.monotonic()
                    pin_vert = 1
                    step_vert = step_vert + add_vert
                else:
                    GPIO.output(steppin_vert, 0)
                    pin_vert = 0
                    lasttime_vert = time.monotonic()
                    if GPIO.input(kaibpin_vert) == kalibreached_vert: 
                        loop_vert = False
                        
            if loop_horz and waittime_horz < difftime_horz:
                if pin_horz == 0:
                    GPIO.output(steppin_horz, 1)
                    lasttime_horz = time.monotonic()
                    pin_horz = 1
                    step_horz = step_horz + add_horz
                else:
                    GPIO.output(steppin_horz, 0)
                    pin_horz = 0
                    lasttime_horz = time.monotonic()
                    if GPIO.input(kaibpin_horz) == kalibreached_horz: 
                        loop_horz = False

        print(str(step_vert) + ' : ' + str(step_horz))

        dict_pos = {"Vertical": step_vert , "Horizontal" : step_horz}
        if save == True:
            with open(self.filename_calibratetocopy, 'w') as outfile:
                json.dump(dict_pos, outfile)
        return dict_pos

        
    

if __name__ == '__main__':
    print('Hello')

    defaultpins = HardwareList.get_Pins_from_json()
    print(defaultpins.get('Motor2'))
    print(defaultpins.get('Motor1'))
    Relais = Control_Relais(relaispin = defaultpins.get('Relais') , bit_relaisopen = 1)
    Motor2 = ControlMotor(motorname='Motor2', motorpins=defaultpins.get('Motor2'),
                          dictstepwidth=HardwareList.DRV8825_dictstepwidth, invertrotation=1, enablebitvalue=0,
                          position=0, stepwidth=8, pitchperrotation=2.54,
                          fullstepsperrotation=200, targetrotationspeed=200,
                          kalibreached=0,
                          posmax=150,
                          posmin=0)
    Motor1 = ControlMotor(motorname='Motor1', motorpins=defaultpins.get('Motor1'),
                          dictstepwidth=HardwareList.DRV8825_dictstepwidth, invertrotation=1, enablebitvalue=0,
                          position=0, stepwidth=8, pitchperrotation=2.54,
                          fullstepsperrotation=200, targetrotationspeed=200,
                          kalibreached=0,
                          posmax=150,
                          posmin=0)

    Actor = Control_Actors(Relais, Motor1 , Motor2)
    Motor2.initialise_motor()
    Motor1.initialise_motor()
    Relais.initialise_relais()
    Actor.enable_motors()

    Motor2.set_direction(0)
    Motor1.set_direction(0)
    input()
    Actor.calibrate(save = False)
    input()
    Actor.move_steps_concurrent(Motor1.get_distance_in_steps(250) , Motor2.get_distance_in_steps(5))
    Actor.disable_motors()
    input()
    Actor.enable_motors()
    Relais.open()
    time.sleep(20)
    Relais.close()
    Actor.disable_motors()
    HardwareList.reset_MCPS()
    HardwareList.reset_rpi_pins()
    



