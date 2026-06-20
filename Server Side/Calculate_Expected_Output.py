# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 15:41:12 2022

@author: mahfouz

Dicription: This software component is responsible for calculating the system expected output.

"""
import json
import re
import pandas as pd
from py2neo import Relationship
from py2neo import Node
from datetime import timedelta

from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "poolloop"))

#############################################################################################################

#############################################################################################################
"""
    Name: calculate_average_conformation_time
    Discription: - Query the populated medication times.
                 - Calculate the user average confirmation times in different daytimes and output it as 
                 an expected confirmation time.
    Arguments:
        delay_threshold: time (Maximum accepted user confirmation time)
    Returns:
        average_user_confirmation_time_dict: dict (Expected confirmation time for different daytime)
"""
def calculate_average_conformation_time(delay_threshold):
    """Query previous recorded data"""
    query=(                                      
     "  MATCH (f:function {name: 'Alarm'}) "
     "  MATCH (x)-[:INPUT_TO]->(f)"
     "  MATCH (x)-[:has]->(m) Where m.opened_at <> 'not_opened' "
     "  MATCH (m)-[:measured_at]->(t) "
     "  RETURN m.opened_at, m.daytime, t.value "               
        )
    data= graph.run(query).to_table() 
    # print(data)
    # print(data[0])
    """Initialize average user confirmation time"""
    average_user_confirmation_time_mornings=timedelta(hours=0,minutes=0)
    counter_mornings=0
    average_user_confirmation_time_noons=timedelta(hours=0,minutes=0)
    counter_noons=0
    average_user_confirmation_time_evenings=timedelta(hours=0,minutes=0)
    counter_evenings=0
    average_user_confirmation_time_nights=timedelta(hours=0,minutes=0)
    counter_nights=0
    average_user_confirmation_time=timedelta(hours=0,minutes=0)
    # delay_threshold=15 # In minutes
    """ Loop for all quired data """
    for row in data:
      """Extract confirmation time from triggered and confirmed time stamps"""
      confirmed_time_str= (str(row[0]).split(' '))[1]
      triggered_time_str= (str(row[2]).split('T'))[1]
      confirmed_time_splitted=confirmed_time_str.split(':')
      confirmed_time_hours=int(confirmed_time_splitted[0])
      confirmed_time_mintues=int(confirmed_time_splitted[1])
      confirmed_time_seconds=float(confirmed_time_splitted[2])
      triggered_time_hours=int(triggered_time_str[0:2])
      # print(triggered_time_hours)
      triggered_time_minutes=int(triggered_time_str[2:])
      confirmed_time = timedelta(hours=confirmed_time_hours, minutes=confirmed_time_mintues, seconds=confirmed_time_seconds)
      triggered_time = timedelta(hours=triggered_time_hours, minutes=triggered_time_minutes)      
      """Calculate diffrence between alarm triggered and confirmed in a each row in queried data 
         and added to the total time based on different  daytimes"""
      user_confirmation_time=confirmed_time-triggered_time 
      if(user_confirmation_time<=timedelta(hours=0,minutes=delay_threshold)):
          average_user_confirmation_time=average_user_confirmation_time+user_confirmation_time
          if str(row[1])=="morning":
            average_user_confirmation_time_mornings=average_user_confirmation_time_mornings+user_confirmation_time
            counter_mornings=counter_mornings+1
            # print(confirmed_time)
            # print(triggered_time)
            # print(user_confirmation_time_mornings)
          elif str(row[1])=="noon":
            average_user_confirmation_time_noons=average_user_confirmation_time_noons+user_confirmation_time
            counter_noons=counter_noons+1 
          elif str(row[1])=="evening":
            average_user_confirmation_time_evenings=average_user_confirmation_time_evenings+user_confirmation_time
            counter_evenings=counter_evenings+1 
          else:
            average_user_confirmation_time_nights=average_user_confirmation_time_nights+user_confirmation_time
            counter_nights=counter_nights+1 
    """Calculate the average user confirmation time for each daytime """    
    average_user_confirmation_time_mornings= average_user_confirmation_time_mornings/counter_mornings
    average_user_confirmation_time_noons= average_user_confirmation_time_noons/counter_noons
    average_user_confirmation_time_evenings= average_user_confirmation_time_evenings/counter_evenings
    average_user_confirmation_time_nights= average_user_confirmation_time_nights/counter_nights
    average_user_confirmation_time=average_user_confirmation_time/(counter_mornings+counter_noons+counter_evenings+counter_nights)
    average_user_confirmation_time_dict={"morning": average_user_confirmation_time_mornings, "noon": average_user_confirmation_time_noons,\
                                         "evening": average_user_confirmation_time_evenings, "night": average_user_confirmation_time_nights,\
                                         "day": average_user_confirmation_time}
    # print(counter_mornings+counter_noons+counter_evenings+counter_nights)
    # print(len(data))
    # print(str(average_user_confirmation_time_dict["Mornings"]))                                     
    print("Mornings: "+str(average_user_confirmation_time_mornings)+ " delay")
    print("Noons: "+str(average_user_confirmation_time_noons)+" delay")
    print("Evenings: "+str(average_user_confirmation_time_evenings) +" delay")
    print("Nights: " +str(average_user_confirmation_time_nights)+" delay")
    print("Days: " +str(average_user_confirmation_time)+" delay")
    return average_user_confirmation_time_dict     
calculate_average_conformation_time(100)