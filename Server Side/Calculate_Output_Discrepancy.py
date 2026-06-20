# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 16:03:08 2022

@author: mahfouz

Dicription: This software component is responsible for calculating the system output discrepancy.
"""
import json
import re
import pandas as pd
import os
import csv
from py2neo import Relationship
from py2neo import Node
from datetime import timedelta
from Integrator import medication_times_to_json
from Populating_metamodel import populate_model_medication_times
from Calculate_Expected_Output import calculate_average_conformation_time

from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "poolloop"))
path_source='actual_output\medication_times_actual.csv'
path_sink="actual_output\confirmation_times_discrepancy.csv"
#############################################################################################################
delay_threshold = 100 # minutes
#############################################################################################################
"""
    Name: populate_actual_conformation_time_csv_data
    
    Discription: It Creates the .json files for the actual medication_times measured from the system
                 and populate them to the context model.
    Arguments: None
        
    Returns: None
"""
#############################################################################################################
def populate_actual_conformation_time_csv_data():
    """Create json file"""
    path=path_source
    medication_times_actual = pd.read_csv(path)
    medication_times_to_json(medication_times_actual,path.split('.')[0]+".json")
    """Populate to graph """
    medication_times_data = json.load(open(path.split('.')[0]+".json"))
    populate_model_medication_times(medication_times_data)
#############################################################################################################    
"""
    Name: calculate_discrepancy_in_conformation_time
    
    Discription: It Queries the user actual medication_times stored in the graph at certain timestamp
                 and daytime and compare them with its relative day time expected output  
    Arguments: 
        daytime : str (morning,noon,evening, or night)
        timestamp: str (time format as used in the graph model)
        delay_threshold: time (Maximum accepted user confirmation time)
    Returns: None
"""
#############################################################################################################    
def calculate_discrepancy_in_conformation_time(daytime,timestamp,delay_threshold):    
    discrepency_in_user_confirmation_time=timedelta(hours=0,minutes=0,seconds=0)
    """Query user actual medication_times"""
    query=(            
     "  MATCH (f:function {name: 'Alarm'})"
     "  MATCH (f)-[:OUTPUT_TO]->(ys)"
     "  MATCH (ys)-[:has]->(m) Where m.daytime = $daytime"
     "  MATCH (m)-[:measured_at]->(t) Where t.value = $timestamp"
     "  RETURN m.opened_at"               
        )
     
    data= graph.run(query,daytime=daytime,timestamp=timestamp).to_table()
    actual_opened_at_time = str(data[0][0])
    """Extract confirmation time from triggered and confirmed time stamps"""
    if actual_opened_at_time != "not_opened":
       actual_confirmed_time_str= (actual_opened_at_time).split(' ')[1]
       actual_confirmed_time_splitted=actual_confirmed_time_str.split(':')
       actual_confirmed_time_hours=int(actual_confirmed_time_splitted[0])
       actual_confirmed_time_mintues=int(actual_confirmed_time_splitted[1])
       actual_confirmed_time_seconds=float(actual_confirmed_time_splitted[2])
       actual_confirmed_time = timedelta(hours=actual_confirmed_time_hours, minutes=actual_confirmed_time_mintues, seconds=actual_confirmed_time_seconds)
    
       actual_triggered_time_str= (str(timestamp).split('T'))[1]
       actual_triggered_time_hours=int(actual_triggered_time_str[0:2])
       actual_triggered_time_minutes=int(actual_triggered_time_str[2:])
       actual_triggered_time = timedelta(hours=actual_triggered_time_hours, minutes=actual_triggered_time_minutes) 
       """Calculate Actual user confirmation time"""
       actual_user_confirmation_time=actual_confirmed_time-actual_triggered_time
       # print(actual_user_confirmation_time)
       """Calculate Expected user confirmation time"""
       expected_user_confirmation_time=calculate_average_conformation_time(delay_threshold)[daytime]
       # print(expected_user_confirmation_time)
       """Calculate Discrepency in user confirmation time"""
       discrepency_in_user_confirmation_time_abs=abs(actual_user_confirmation_time-expected_user_confirmation_time)
       """Check Discrepency sign over or under expected"""
       if actual_user_confirmation_time>expected_user_confirmation_time:
           discrepency_in_user_confirmation_time_dict= {"Value":discrepency_in_user_confirmation_time_abs,"Sign":"+"}
           return discrepency_in_user_confirmation_time_dict
       else:
           discrepency_in_user_confirmation_time_dict={"Value":discrepency_in_user_confirmation_time_abs,"Sign":"-"}
           return discrepency_in_user_confirmation_time_dict
       # print(discrepancy_in_user_confirmation_time)
    else:
       discrepency_in_user_confirmation_time_dict={"Value":actual_opened_at_time,"Sign":""}
       return  discrepency_in_user_confirmation_time_dict
#############################################################################################################    
"""
    Name: write_discrepency_in_conformation_time_csv
    
    Discription: It output the calculated output discrepancy at a certain timestamp and daytime
                 into confirmation_times_ discrepancy.csv file.
    Arguments:         
               daytime : str (morning,noon,evening, or night)
               timestamp: str (time format as used in the graph model)
        
    Returns: None
"""
#############################################################################################################   
def write_discrepency_in_conformation_time_csv(daytime,timestamp):
    data_dict = calculate_discrepancy_in_conformation_time(daytime=daytime,timestamp=timestamp,delay_threshold=delay_threshold)
    header = ['timestamp', 'daytime', 'discrepancy_in_user_confirmation_time']
    data = [timestamp,daytime,data_dict["Sign"]+str(data_dict["Value"])]
    path = path_sink
    """Check if the output file exists """
    isExist=os.path.exists(path)
    # print(isExist)
    """Create the file and add the data"""
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
#############################################################################################################
"""
    Name: write_discrepency_in_conformation_time_csv_graph
    
    Discription: It queries all the stored medication_times at different timestamps and medication times
                 and writes all their respective discrepancies values into 
                 confirmation_times_ discrepancy.csv file.

    Arguments: None
        
    Returns: None
"""
#############################################################################################################
def write_discrepency_in_conformation_time_csv_graph():
    # populate_actual_conformation_time_csv_data()
    query=(            
     "  MATCH (f:function {name: 'Alarm'})"
     "  MATCH (f)-[:OUTPUT_TO]->(ys)"
     "  MATCH (ys)-[:has]->(m)"
     "  MATCH (m)-[:measured_at]->(t)" 
     "  RETURN m.daytime, t.value"               
        )
    data= graph.run(query).to_table()
    for row in data: 
      write_discrepency_in_conformation_time_csv(daytime=row[0],timestamp=row[1])
#############################################################################################################      
if __name__ == "__main__":
   # populate_actual_conformation_time_csv_data()
   # out=calculate_discrepancy_in_conformation_time(daytime="morning",timestamp="_12_07_2021T0800",delay_threshold=15)
   # print(out["Sign"]+str(out["Value"]))
   write_discrepency_in_conformation_time_csv_graph()