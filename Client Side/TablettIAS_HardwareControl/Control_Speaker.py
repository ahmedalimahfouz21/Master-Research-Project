# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 17:46:12 2022

@author: mahfouz

Discription: This software component is responsible for generating the control the hardware structure 
             based on the given context values and the learned discrepancy values calculated as output
             of the estimated mapping equation.
"""
import alsaaudio as audio
import csv
import os
class Control_Speaker:
        def __init__(self,default_volume):
            self.scanCards= audio.cards()
            #print("cards:", scanCards)
            for card in self.scanCards:
                self.scanMixers = audio.mixers(self.scanCards.index(card))
                print("mixers:", self.scanMixers)
            self.mixer = audio.Mixer('Speaker', cardindex=1)
            self.default_volume=default_volume
            self.control_signals_path='control_signals_'
        def volumeMasterControl(self,control_signal):  
            # volume = self.mixer.getvolume()
            volume = self.default_volume
            self.mixer = audio.Mixer('Speaker', cardindex=1)
            #print(volume)
            newVolume = int(volume[0])+int(control_signal)
            if 0<= newVolume <= 100:
                self.mixer.setvolume(newVolume)
                #print("Done")
        def extract_control_signal(self,daytime):
          """Speaker Control"""
          path=self.control_signals_path + daytime + '.csv'
          isExist=os.path.exists(path)
          # print(isExist)
          speaker_signal=0
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
                if str(element)=="Speaker_control":
                    #print ("Debug")
                    #print (data[i])
                    speaker_signal= int(float(data[i]))
                i=i=1
            return speaker_signal
          else:
              return 0
        
if __name__ == "__main__":
   speaker_handler= Control_Speaker(default_volume=[50])
   speaker_handler.volumeMasterControl()
