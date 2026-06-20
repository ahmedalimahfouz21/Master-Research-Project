# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 10:41:06 2022

@author: mahfouz
"""
import socket
import json
import ast
import csv
class UDP_Client:
      def __init__(self,serverAddress,serverPort,bufferSize):
          self.serverAddressPort=(serverAddress,serverPort)
          self.bufferSize=bufferSize
          # Create a UDP socket at client side
          self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
          self.path_sink="control_signals_"
    
      def UDP_Send_Client(self,command,value):
          msgFromClient       = {"Command":command, "Value":value} #"Hello UDP Server"

          msgFromClient_string = json.dumps(msgFromClient)

          bytesToSend         = str.encode(msgFromClient_string)
          
          # Send to server using created UDP socket

          self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
         
      def UDP_Recv_Client(self,daytime):
          msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)

          msg = msgFromServer[0] # "Message from Server {}".format(msgFromServer[0])

          dict_str = msg.decode("UTF-8")
          
          mydata = ast.literal_eval(dict_str)

          print(mydata)

          message=mydata["Message"]
          content=mydata["Content"]
          if  message== "Control_Signals":
              header = ['Speaker_control', 'LEDs_control']
              control_data=content
              data = [control_data["Speaker_control"],control_data["LEDs_control"]]
              path=self.path_sink + daytime + ".csv"
              print(path)
              f = open(path, 'w+', newline='', encoding='utf-8')
              writer = csv.writer(f)
              writer.writerow(header)
              writer.writerow(data)
              f.close()
if __name__ == "__main__":
    client = UDP_Client(serverAddress="127.0.0.1",serverPort=8080,bufferSize=1024)
    client.UDP_Send_Client(command="Get_control_signals",value="None")
    client.UDP_Recv_Client("evening")      
