# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 17:03:10 2022

@author: mahfouz

Discription: This software component is responsible for measuring the system’s actual output.
"""
#############################################################################################################
from datetime import timedelta
from datetime import date
import time
import csv
import os
from UDP_Client import UDP_Client
#############################################################################################################
class Measure_Actual_Output:
    def __init__(self):
        self.alarm_triggered = time.monotonic()
        
        self.alarm_daytime = "morning"
        
        self.alarm_confirmed = self.alarm_triggered
        
        self.alarm_opened = False
        
        self.path_sink= 'medication_times.csv'
        
    def get_user_confirmation_time(self):
        delay = timedelta(hours=0,minutes=0,seconds=self.alarm_confirmed-self.alarm_triggered)
        dict_confirmation_time = {"Daytime":  self.alarm_daytime, "Delay": delay }
        print("Daytime: "+ str(dict_confirmation_time["Daytime"]) + " Delay: " + str(dict_confirmation_time["Delay"]))
        return   dict_confirmation_time 
    
    def set_alarm_triggered(self,current_time,daytime):
        self.alarm_triggered = current_time
        self.alarm_daytime = daytime
        self.alarm_opened = False
        
    def get_alarm_triggered(self):
        return self.alarm_triggered

    
    def set_alarm_confirmed(self,current_time):
        self.alarm_confirmed = current_time
        self.alarm_opened = True
        

    def write_medication_times_csv(self):
         data_dict = self.get_user_confirmation_time()
         header = ['date', 'daytime', 'triggered_times', 'opened_times']
         today  = str(date.today())
         daytime= str(data_dict["Daytime"])
         delay  = data_dict["Delay"]
         if str(delay) != "not_opened":
              opened_times= today + " " 
         if   daytime=="morning":
              triggered_times='08:00'
              opened_times = opened_times+ str(timedelta(hours=8,minutes=0)  + delay)
         elif daytime=="noon":
              triggered_times='13:00'
              opened_times = opened_times+ str(timedelta(hours=13,minutes=0) + delay)
         elif daytime=="evening":
              triggered_times='17:00'
              opened_times = opened_times+ str(timedelta(hours=17,minutes=0) + delay)
         else:
              triggered_times='21:00'
              opened_times = opened_times+ str(timedelta(hours=21,minutes=0) + delay)
         data = [today,daytime, triggered_times, opened_times]
         path = self.path_sink      
         print(data)
         isExist=os.path.exists(path)
         print(isExist)
         if (isExist)==False:
            f = open(path, 'a+', newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)
            print("Exist 1st time")
         else:
            f = open(path, 'a+', newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(data)
            print("Exist 2nd time")
         f.close()
         return data
            
         
if __name__ == "__main__":
    measure_actual_output = Measure_Actual_Output()
    value= measure_actual_output.write_medication_times_csv()
    client = UDP_Client(serverAddress="127.0.0.1",serverPort=8080,bufferSize=1024)
    client.UDP_Send_Client(command="Write_actual_output",value=value)
    # client.UDP_Recv_Client()  
