from HardwareList import HardwareList
from Control_Removal import Control_Removal
from Connection_GUI import Connection_Zmq
from Control_Actors import Control_Actors
from Control_Motor import ControlMotor
from Control_Relais import Control_Relais
from Control_Detection import Control_Detection
from Control_MagDet import Control_MagDet
from Control_LED import Control_LED
from Control_Speaker import Control_Speaker
from Connection_Database import Connection_Database
from Measure_Actual_Output import Measure_Actual_Output
from UDP_Client import UDP_Client
import time
import os
import sys
from datetime import datetime
DEFINE_UDP_Client = True
class Control_Code:
    def __init__(self):
        self.connGUI = Connection_Zmq("127.0.0.1", "5555")
        # initialise everything in here
        self.defaultpins = HardwareList.get_Pins_from_json()
        self.LEDpins = self.defaultpins.get("LED")
        self.DetPins = self.defaultpins.get("Detection")

        self.Motor2 = ControlMotor(motorname='Motor2', motorpins=self.defaultpins.get('Motor2'),
                              dictstepwidth=HardwareList.DRV8825_dictstepwidth, invertrotation=1, enablebitvalue=0,
                              position=0, stepwidth=1, pitchperrotation=2.54,
                              fullstepsperrotation=200, targetrotationspeed=180,
                              kalibreached=0,
                              posmax=150,
                              posmin=0)
        self.Motor1 = ControlMotor(motorname='Motor1', motorpins=self.defaultpins.get('Motor1'),
                              dictstepwidth=HardwareList.DRV8825_dictstepwidth, invertrotation=1, enablebitvalue=0,
                              position=0, stepwidth=1, pitchperrotation=2.54,
                              fullstepsperrotation=200, targetrotationspeed=180,
                              kalibreached=0,
                              posmax=300,
                              posmin=0)
        self.Relais = Control_Relais(relaispin = self.defaultpins.get('Relais') , bit_relaisopen = 1)
        self.Actors = Control_Actors(self.Relais, self.Motor1, self.Motor2)

        self.LED = Control_LED(self.LEDpins)
        
        self.Speaker= Control_Speaker(default_volume=[50])

        self.Det = Control_Detection(self.DetPins, 1)

        self.Mag_Det = Control_MagDet(led_obj=self.LED, det_obj = self.Det, turn_off_time = 5)

        self.connDatabase = Connection_Database()

        self.Removal = Control_Removal(removalPin = self.defaultpins.get('Motion'), connDatabase = self.connDatabase)


        #self.blink_val = False
        
        self.currAlarm = None
        
        self.blinktime = time.monotonic()
        
        #self.blinkCycle=0
        
        self.blink_state = True
        
        self.LEDs_state =  False
        
        self.pwm_counter=0
        
        self.pwm_dutyCycle_default=5
        
        self.pwm_dutyCycle=self.pwm_dutyCycle_default
       
        self.measure_actual_output = Measure_Actual_Output()
        
        self.DEFINE_UDP_Client = True
        if DEFINE_UDP_Client:
           self.udp_client = UDP_Client(serverAddress="192.168.178.45",serverPort=8080,bufferSize=1024)

    def initialise(self):
        self.Motor2.initialise_motor()
        self.Motor1.initialise_motor()
        self.Relais.initialise_relais()
        self.Det.initialise_det()
        self.LED.initialise_LED()
        self.Removal.initialisePinRemoval()



    def main_control(self):
        #this can be seen as a state machine but with default message checking
        switch_entry = {
                        "mag_detection" : self.get_mag_det_status,
                        "login" : self.login,
                        "logout": self.logout,
                        "idle" : self.idle,
                        "show_led" : self.show_led,
                        "get_mag_status" : self.get_mag_det_status,
                        "position_actors": self.position_actor,
                        "open_magazin": self.open_magazin
                        }
        switch_do = {
                        "mag_detection": self.mag_detection,
                        "position_actors": self.wait_for_confirmation
                        }
        while True:
                
            #self.measure_actual_output.get_user_confirmation_time()
            msg = self.connGUI.check_for_message()
            if msg is not None:
                message = msg.get("message", None)
                arguments = msg.get("arguments", None)
                func = switch_entry.get(message, None)
                answer = None
                if func is not None:
                    answer = func(message,arguments)
                    
                else:
                    answer = {"message" : "Error"}
                if answer is None:
                    answer = {"message" : "default_answer"}
                print(answer)
                self.connGUI.answer_message_json(answer)
            else:

                message = self.connGUI.lastMessage.get("message", None)
                arguments = self.connGUI.lastMessage.get("arguments", None)
                func = switch_do.get(message, None)
                if func is not None:
                    func(message, arguments)

    def login(self, message, arguments):
        # reset the Mag Detection status
        self.LED.turn_off_all()
        self.Mag_Det.entry()
        answer = {"message": "answer_login",
                  "arguments": None}
        return answer

    def logout(self, message, arguments):
        self.LED.turn_off_all()
        self.Removal.deactivateCallback()
        answer = {"message": "answer_logout",
                  "arguments": None}
        return answer

    def idle(self, message , arguments):
        self.LED.turn_off_all()
        answer = {"message": "answer_idle",
                  "arguments": None}
        return answer
        

    def mag_detection(self, message , arguments):
        self.Mag_Det.magazin_detection()

    def show_led(self, message , arguments):
        self.LED.turn_off_all()
        self.LED.show_led(arguments)
        answer = {"message": "answer_show_led",
                  "arguments": None}
        return answer

    def wait_for_confirmation(self, message , arguments):
        
        tstamp = time.monotonic()
        blinkCycle = tstamp- self.blinktime
        # print(time.monotonic())
        print("LEDs Brightness: " + str(self.pwm_dutyCycle))
        if (self.currAlarm.get("alarm_light") == 1):
                #LEDs_control= self.LED.extract_control_signal()
                #print(LEDs_control)
                #self.pwm_dutyCycle=LEDs_control
                #print(blinkCycle)
                if blinkCycle>=1:
                   self.blink_state= not self.blink_state
                   #self.blinkCycle=0
                   self.blinktime = time.monotonic()
                   self.LEDs_state = False
                if self.blink_state == True: #ON state
                    #print("Python: ON")
                    self.pwm_counter=self.pwm_counter+1
                    if self.pwm_counter<= self.pwm_dutyCycle and not self.LEDs_state:
                        self.LED.turn_on_blue()
                        self.LEDs_state = True
                    elif self.pwm_counter> self.pwm_dutyCycle and self.LEDs_state:
                        self.LED.turn_off_blue()
                        self.LEDs_state = False
                    if self.pwm_counter==10:
                        self.pwm_counter=0
                        self.LEDs_state= False
                else: #OFF state
                  #print("Python: Off")
                  if not self.LEDs_state :  
                     self.LED.turn_off_blue()
                     self.LEDs_state = True
        else:
             self.LED.turn_off_blue() 
        #we dont nedd an answer here
        # time.sleep(0.01)


    def position_actor(self, message , arguments):
        self.LED.turn_off_all()
        print(str(arguments))
        self.currAlarm = arguments.get("alarm_obj")
        weekday = arguments.get("alarm_obj").get("weekday")
        daytime = arguments.get("alarm_obj").get("daytime")
        print(daytime)
        ret = None
        ret = self.Actors.move_to_magazin_concurrent(weekday, daytime)
        answer = { "message" : "answer_position_actor" ,
                   "arguments" : {"retvalue": ret }}
        self.measure_actual_output.set_alarm_triggered(time.monotonic(),daytime)
        self.blink_val = False;
        self.blinktime = time.monotonic()
        self.LED.turn_off_all()
        if DEFINE_UDP_Client:
           self.udp_client.UDP_Send_Client(command="Get_control_signals",value="None")
           self.udp_client.UDP_Recv_Client(daytime=daytime)
        if (self.currAlarm.get("alarm_tone") == 1):
           Speaker_control= self.Speaker.extract_control_signal(daytime)
           #print(Speaker_control)
           self.Speaker.volumeMasterControl(Speaker_control)
        if (self.currAlarm.get("alarm_light") == 1):
           LEDs_control= self.LED.extract_control_signal(daytime)
           #print(LEDs_control)
           self.pwm_dutyCycle=LEDs_control
        return answer

    def open_magazin(self, message , arguments):
        print("Opening")
        self.measure_actual_output.set_alarm_confirmed(time.monotonic())
        if DEFINE_UDP_Client:
           value= self.measure_actual_output.write_medication_times_csv()
           self.udp_client.UDP_Send_Client(command="Write_actual_output",value=value)
        else:   
           self.measure_actual_output.write_medication_times_csv()
        self.LED.turn_off_all()
        weekday = arguments.get("alarm_obj").get("weekday")
        daytime = arguments.get("alarm_obj").get("daytime")
        extract_id = arguments.get("extraction_id")
        alarm_dict = { "State" : "Opened" , "extractID" : extract_id}
        stamp = time.localtime()
        self.connDatabase.update_extraction_opened(extract_id, stamp, "Opened")
        self.Removal.setlastAlarm(alarm_dict)
        self.Removal.activateCallback()
        self.Actors.open_mag(weekday, daytime)
        print("Opened")
        time.sleep(20)
        self.Actors.close_mag()
        answer = {"message": "answer_open_magazin",
                  "arguments": None}
        return answer

    def get_mag_det_status(self, message , arguments):
        args = self.Det.get_magazines_in_Dispenser()

        answer = {"message": "answer_mag_det_status",
                  "arguments": args}
        return answer

        
if __name__ == "__main__":
    os.chdir(sys.path[0])
    print(str(os.getcwd()))
    control = Control_Code()
    control.initialise()
    control.main_control()
