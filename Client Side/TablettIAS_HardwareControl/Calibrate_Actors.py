from HardwareList import HardwareList
from Control_Motor import ControlMotor
from Control_Relais import Control_Relais
from Control_Actors import Control_Actors
import time
import json
import logging
import RPi.GPIO as GPIO

if __name__ == '__main__':
    print('Hello')

    defaultpins = HardwareList.get_Pins_from_json()
    print(defaultpins.get('Motor2'))
    print(defaultpins.get('Motor1'))
    Motor_horz = ControlMotor(motorname='Motor2', motorpins=defaultpins.get('Motor2'),
                          dictstepwidth=HardwareList.DRV8825_dictstepwidth, invertrotation=1, enablebitvalue=0,
                          position=0, stepwidth=1, pitchperrotation=2.54,
                          fullstepsperrotation=200, targetrotationspeed=180,
                          kalibreached=0,
                          posmax=150,
                          posmin=0)
    Motor_vert = ControlMotor(motorname='Motor1', motorpins=defaultpins.get('Motor1'),
                          dictstepwidth=HardwareList.DRV8825_dictstepwidth, invertrotation=1, enablebitvalue=0,
                          position=0, stepwidth=1, pitchperrotation=2.54,
                          fullstepsperrotation=200, targetrotationspeed=180,
                          kalibreached=0,
                          posmax=150,
                          posmin=0)
    Relais = Control_Relais(relaispin = defaultpins.get('Relais') , bit_relaisopen = 1)
    Actors = Control_Actors(Relais, Motor_vert, Motor_horz)
    Motor_vert.initialise_motor()
    Motor_horz.initialise_motor()
    Relais.initialise_relais()

    input()
    Actors.startup()
    Actors.enable_motors()
    Actors.move_steps_concurrent(Motor_vert.get_distance_in_steps(8), Motor_horz.get_distance_in_steps(8))
    Actors.disable_motors()
    print("Bringen sie den Hubmagnet nun zum ersten Öffnungspunkt")
    input()
    Actors.enable_motors()
    dict_pos = Actors.calibrate(save = True)
    Actors.move_steps_concurrent(dict_pos.get("Vertical",0), dict_pos.get("Horizontal",0))
    input()
    Relais.open()
    time.sleep(20)
    Relais.close()
    Actors.disable_motors()
    print("Kopieren sie nun den korrekten Teil der erstellten Datei")
    HardwareList.reset_MCPS()
    HardwareList.reset_rpi_pins()
