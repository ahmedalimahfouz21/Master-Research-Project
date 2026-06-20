# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 17:46:12 2022

@author: mahfouz

Discription: This software component is responsible for generating the control the hardware structure 
             based on the given context values and the learned discrepancy values calculated as output
             of the estimated mapping equation.
"""
import json
import re
import pandas as pd
import os
import csv
from py2neo import Relationship
from py2neo import Node
from datetime import timedelta
from Mapping_Criteria import mapping_equation_alarm_from_matlab
from py2neo import Graph
import math
graph = Graph("bolt://localhost:7687", auth=("neo4j", "poolloop"))
#############################################################################################################
NUM_SECONDS_IN_A_MIN = 60
path_source= 'actual_output\mapping_equation.csv'
path_sink = 'actual_output\control_signals.csv'
#############################################################################################################
"""
    Name: Control_PillDispenser_AlarmOutput
    
    Discription: It applies the mapping equation on the given context to calculate the discrepancy values. 
    
    Arguments: 
        context : dict (noise, and light)
        
    Returns:
        Output_control_signal : dict (Speaker_control, and LEDs_control)
"""
#############################################################################################################
def Control_PillDispenser_AlarmOutput(context):
    """Calculate the the learned discrepancy value, noise"""
    Discrepancy_learned_value = mapping_equation_alarm_from_matlab(path_source,context)
    # print(Discrepancy_learned_value )
    discrepancy=Discrepancy_learned_value["Discrepancy"]
    noise_part =Discrepancy_learned_value["noise_effect"] 
    light_part =Discrepancy_learned_value["light_effect"] 
    """Calculate noise and light contribution for the discrepancy value"""
    noise_ratio=100*abs(noise_part)/(abs(noise_part)+abs(light_part)) #%
    light_ratio=100*abs(light_part)/(abs(noise_part)+abs(light_part)) #%
    print("Discrepancy: " + str(discrepancy))
    print("Nosie Ratio: " + str(noise_ratio))
    print("Light Ratio: " + str(light_ratio))
    """Number of """
    Discrepancy_levels = 4
    """Tune the control signal gain based on the discrepancy range"""
    if (0.0 < discrepancy <= 10.0):
        print("Discrepancy level: Too small Discrepancy")
        Speaker_control_ratio=noise_ratio/Discrepancy_levels
        LEDs_control_ratio   =light_ratio/Discrepancy_levels
    elif (10.0 < discrepancy <= 50.0):
        print("Discrepancy level: Small Discrepancy")
        Speaker_control_ratio=4*noise_ratio/Discrepancy_levels
        LEDs_control_ratio   =4*light_ratio/Discrepancy_levels
    elif (50.0 < discrepancy <= 90.0):
        print("Discrepancy level: Reasonable Discrepancy")
        Speaker_control_ratio=4*noise_ratio/Discrepancy_levels
        LEDs_control_ratio   =4*light_ratio/Discrepancy_levels
    elif (90.0 < discrepancy <= 130.0):
        print("Discrepancy level: Large Discrepancy")
        Speaker_control_ratio=4*noise_ratio/Discrepancy_levels
        LEDs_control_ratio   =4*light_ratio/Discrepancy_levels
    elif ( discrepancy > 130.0 ):
        print("Discrepancy level: Too large Discrepancy")
        Speaker_control_ratio=noise_ratio
        LEDs_control_ratio   =light_ratio
    else:
        print("Alarm was confirmed withen the expected time")
        Speaker_control_ratio=0
        LEDs_control_ratio   =0
    Speaker_control_signal=Map_valueRatio_to_controlSignal(abs(Speaker_control_ratio),0,100,0,50)
    LEDs_control_signal=Map_valueRatio_to_controlSignal(abs(LEDs_control_ratio),0,100,0,5)
    # if noise_part < 0:
    #     Speaker_control_signal = -1*Speaker_control_signal
    # if light_part < 0:
    #     LEDs_control_signal = -1*LEDs_control_signal
    # print(Speaker_control_signal)
    # print(LEDs_control_signal)
    header = ['Speaker_control', 'LEDs_control']
    data = [Speaker_control_signal,LEDs_control_signal ]
    f = open(path_sink, 'w+', newline='', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerow(data)
    f.close()
    
    query=( " MATCH (f:function {name: 'Alarm'}) "
            " MATCH (f)-[:CONTROLS]->(s:structure) WHERE s.name='speaker'"
            " MATCH (s)-[:has]->(b:behaviour) WHERE b.name= 'Speaker_Sound_Level'"
            " SET b.value = $speakervolume"
            " SET b.unit = '%'"
            " RETURN b")
    graph_data= graph.run(query,speakervolume=50+Speaker_control_signal).to_table()
    
    query=( " MATCH (f:function {name: 'Alarm'}) "
            " MATCH (f)-[:CONTROLS]->(s:structure) WHERE s.name='8color'"
            " MATCH (s)-[:has]->(b:behaviour) WHERE b.name= 'LEDs_Brightness'"
            " SET b.value = $LEDbrightness"
            " SET b.unit = '%'"
            " RETURN b")
    graph_data= graph.run(query,LEDbrightness=10*(5+LEDs_control_signal)).to_table()
    
    Output_control_signal={"Speaker_control":Speaker_control_signal,"LEDs_control":LEDs_control_signal}
    print(Output_control_signal)
    return Output_control_signal
#############################################################################################################
"""
    Name: Map_valueRatio_to_controlSignal
    
    Discription: : It map any input value from one range to another range
    
    Arguments: 
        value: float (value to be mapped)
        leftMin,leftMax: int (range of the first domain)
        rightMin,rightMax: int (range of the second domain)
      
    Returns: 
        mapped_value: float (value after mapping)
"""
#############################################################################################################
def Map_valueRatio_to_controlSignal(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    mapped_value = rightMin + (valueScaled * rightSpan)
    return mapped_value
if __name__ == "__main__":
    Control_PillDispenser_AlarmOutput({"noise":40,"light":8})