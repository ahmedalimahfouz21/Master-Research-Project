# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 10:41:06 2022

@author: Shukla

updated: Mahfouz

Discription: This software component is responsible for pulling the data coming from 
            the XDK over an MQTT broker and storing them in xdk_data.csv 
"""

import paho.mqtt.client as mqttClient
import time
import datetime
import pandas as pd

def on_connect(client, userdata, flags, rc):
  
    if rc == 0:
  
        print("Connected to broker")
  
        global Connected                #Use global variable
        Connected = True                #Signal connection 
  
    else:
  
        print("Connection failed")
  
    
def on_message(client, userdata, message):
    msg=message.payload.decode("utf-8")    
    print(msg)
    
    timestamp=str(datetime.datetime.now())[:-7]
        
    row=[timestamp]
    print('timestamp:   '+timestamp)
    
    
    for i in msg.split(','):
        if (len(i)!=0):
            row.append(i.split(':')[1])
    try:
        stored_data=pd.read_csv('xdk_data.csv')
        
    except:
        stored_data=pd.DataFrame(columns=['Timestamp','xdk_id', 'Humidity', 'Pressure', 'Temperature', 'Light', 'Noise'])
             
        
        
    new_data=pd.DataFrame(row).T

    new_data.columns=stored_data.columns
    
    frame=[stored_data,new_data]
    
    dataset=pd.concat(frame)
    
    dataset.to_csv('xdk_data.csv',index=False)
    
    
  
Connected = False   #global variable for the state of the connection
  
broker_address= "100.64.176.113"  #Broker address
port = 1883                         #Broker port
  
client = mqttClient.Client("Python")               #create new instance
#client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                     #attach function to callback
  
client.connect(broker_address, port=port)          #connect to broker
  
client.loop_start()        #start the loop
  
while Connected != True:    #Wait for connection
    time.sleep(0.1)
  
client.subscribe("mqtt/environment_parameters")
  
try:
    while True:
        time.sleep(1)
  
except KeyboardInterrupt:
    print ("exiting")
    client.disconnect()
    client.loop_stop()
    
    
#TO DO
    
#if file does not exist create it    
    
    
    
    


