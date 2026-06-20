# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 14:27:59 2022

@author: mahfouz

Discription: This software component is responsible for handling the requests coming from the client side
             which in this case the hardware control code of the pill dispenser. 
"""
import socket
import json
import ast
from Control_Output import Control_PillDispenser_AlarmOutput
import pandas as pd
import time
import os
import csv
################################################################
path_source="xdk_data.csv"
path_sink= 'actual_output/medication_times_actual.csv'
################################################################
"""Server Socket address it can should be changed to the ip adress assigned by 
   the router to which the server side is connected.
   In this code its the local ip address"""
localIP     = "192.168.178.45"

localPort   = 8080

bufferSize  = 1024

""" Create a datagram socket """

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

""" Bind to address and ip """

UDPServerSocket.bind((localIP, localPort))
 
print("UDP server up and listening")

loop=True
# Listen for incoming datagrams

while(loop):
      """Recieve Commands from the client side"""
      bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
      message = bytesAddressPair[0]
      address = bytesAddressPair[1]
      # clientMsg = "Message from Client:{}".format(message)
      # clientIP  = "Client IP Address:{}".format(address)
      # print(clientMsg)
      # print(clientIP)
      dict_str = message.decode("UTF-8")
      mydata = ast.literal_eval(dict_str)
      """Extract Command and Value from the client side"""
      Command = mydata["Command"]
      Value = mydata["Value"]
      if  Command=="Get_control_signals":
          """Calculate control signals based on context values and send it back"""
          xdk_data = pd.read_csv(path_source)
          Noise=xdk_data["Noise"]
          Light=xdk_data["Light"]
          noise=Noise[len(Noise)-1]
          light=Light[len(Light)-1]
          Context={"noise":noise,"light":light}
          print(Context)
          Control_Signals =  Control_PillDispenser_AlarmOutput(Context) 
          print(Control_Signals)    
          msgFromServer_str = json.dumps({"Message":"Control_Signals","Content":Control_Signals})
          bytesToSend         = str.encode(msgFromServer_str)  
          # Sending a reply to client
          UDPServerSocket.sendto(bytesToSend, address)
      elif Command=="Write_actual_output": 
           """Store the output measurement to a medication_times_actual.csv file"""
           path=path_sink
           isExist=os.path.exists(path)
           # print(isExist)
           header = ['date', 'daytime', 'triggered_times', 'opened_times']
           data=Value
           print (header)
           print (data)
           if (isExist)==False:
              f = open(path, 'a+', newline='', encoding='utf-8')
              writer = csv.writer(f)
              writer.writerow(header)
              writer.writerow(data)
              # print("Exist 1st time")
           else:
              f = open(path, 'a+', newline='', encoding='utf-8')
              writer = csv.writer(f)
              writer.writerow(data)
              # print("Exist 2nd time")
           f.close()
           print("Write request was handeled")
      time.sleep(0.1)
