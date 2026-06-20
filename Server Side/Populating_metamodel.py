# -*- coding: utf-8 -*-
"""
Created on Septemper 2021

@author: shukla
@updated by: mahfouz 
Updates: - Adding populate_model_medication_times method to populate the medication_times data 
         to the current context model at which xdk data and user context data are stored.


Discription: middleware that uses the created metamodel and the json datasets created and
             populates the metamodel with all the values.
Usage: populates different sets of the data model
"""

import json
import re
import pandas as pd
from py2neo import Relationship
from py2neo import Node

from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "poolloop"))

#############################################################################################################

#############################################################################################################

def populate_model_xdk(xdk_data):
    
    parent_nodes=  xdk_data['end parameters']
    common_labels= xdk_data['labels']   
    sources= xdk_data['sources']
    units= xdk_data['unit']
    
        
    data = xdk_data['values'] 
    for j in range(0, len(data)):
        
        
        timestamp= data[j]['time']
        
        value=data[j]['value']
        
        
        for i in range(0,len(parent_nodes)):
            print(i)
            #Timestamp node                
            query = ("MATCH (m:temporal{value:'"+timestamp+"'}) return 1")   
    
            if len(str((graph.run(query))))==9: #(no data) is a string of length 9
                 #timestamp not found
                 print("time stamp not found")
                 query = (
                     "CREATE (n:Dynamic:end_parameter:temporal{name:'timestamp_value', value:'"+timestamp+"' }) "
                     "WITH n "
                     
                     "MATCH (m:meta{name:'timestamp'})"
                     "CREATE (m)-[f:has]->(n)" 
                     
                     #We create the timestamp and link it with its parent node
                     ) 
            
                 graph.run(query)
                
                #dont do anything if a node is already there, just link it with the data node 
                
    
    
    
    
            query =(  "CREATE (n:"+str(parent_nodes[i])+":dynamic:"+common_labels+"{name:'"+str(parent_nodes[i])+"_value', units:'"+units[i]+"',value:'"+value[i]+"'})"  
                 
                 "WITH n "            
                 "MATCH (m{name:'"+parent_nodes[i]+"'}),(o{name:'"+sources[i]+"'}),(p:temporal{name:'timestamp_value',value:'"+timestamp+"'})"
                 "CREATE (m)-[r:has ]->(n)"
                 "CREATE (o)-[s:measures ]->(n)"
                 "CREATE (n)-[t:measured_at ]->(p)"          
             )
            graph.run(query)
    
def populate_model_medication_times(medication_times):
    
    parent_nodes=  medication_times['end parameters']
    common_labels= medication_times['labels']   
    #sources= medication_times['sources']
       
    data = medication_times['values'] 
    for j in range(0, len(data)):
        
        
        timestamp= data[j]['time']
        
        value=data[j]['value']
        
        
        for i in range(0,len(parent_nodes)):
            print(i)
            #Timestamp node                
            query = ("MATCH (m:temporal{value:'"+timestamp+"'}) return 1")   
    
            if len(str((graph.run(query))))==9: #(no data) is a string of length 9
                 #timestamp not found
                 print("time stamp not found")
                 query = (
                     "CREATE (n:Dynamic:end_parameter:temporal{name:'timestamp_value', value:'"+timestamp+"' }) "
                     "WITH n "
                     
                     "MATCH (m:meta{name:'timestamp'})"
                     "CREATE (m)-[f:has]->(n)" 
                     
                     #We create the timestamp and link it with its parent node
                     ) 
            
                 graph.run(query)
                
                #dont do anything if a node is already there, just link it with the data node 
                
    
    
    
    
            query =(  "CREATE (n:"+str(parent_nodes[i])+":dynamic:"+common_labels+"{name:'"+str(parent_nodes[i])+"_value', opened_at:'"+value[1]+"',daytime:'"+value[0]+"'})"   
                 
                 "WITH n "            
                 # "MATCH (m{name:'"+parent_nodes[i]+"'}),(o{name:'"+sources[i]+"'}),(p:temporal{name:'timestamp_value',value:'"+timestamp+"'})"
                 "MATCH (m{name:'"+parent_nodes[i]+"'}),(p:temporal{name:'timestamp_value',value:'"+timestamp+"'})"
                 "CREATE (m)-[r:has ]->(n)"
            #    "CREATE (o)-[s:measures ]->(n)"
                 "CREATE (n)-[t:measured_at ]->(p)"
    
                    
             )
            graph.run(query)


def add_user_medical_context(medicaiton_plan):
    
    medicines = []
    dosages = []
    doses_per_day = []
    brandname=[]
    dosage_form=[]
    
    data = medicaiton_plan['medication_plan']['medicines']
    
    for i in range(1, len(data)+1):
       
        #brandname.append(data['medicine_' + str(i)]['brandname_str'])
        #dosage_form.append(data['medicine_' + str(i)]['dosage_form_str'])
        #medicines.append(data['medicine_' + str(i)]['active_ingredient_str'])
        #dosages.append(data['medicine_' + str(i)]['dosage'])
        #doses_per_day.append(data['medicine_' + str(i)]['dose_per_day'])
        
        brandname=data['medicine_' + str(i)]['brandname_str']
        dosage_form=data['medicine_' + str(i)]['dosage_form_str']
        medicines=data['medicine_' + str(i)]['active_ingredient_str']
        dosages=data['medicine_' + str(i)]['dosage']
        doses_per_day=data['medicine_' + str(i)]['dose_per_day']
        
        query =(  "CREATE (n:Static:medication_context{name:'"+brandname+"', dosage_form:'"+dosage_form+"', medicines:'"+medicines+"', dosages:"+str(dosages)+", doses_per_day:"+str(doses_per_day)+"})"  
            
            "WITH n "            
            "MATCH (m{name:'medication_plan'}) "
            "CREATE (m)-[r:includes ]->(n)"
            
        )
        graph.run(query)
        
        
    return ""



def populate_model_power(power_measurement_data):
    # read medication_plan json file
    
    parent_nodes=  power_measurement_data['end parameters']
    common_labels= power_measurement_data['labels']   
    sources= power_measurement_data['sources']
    units= power_measurement_data['unit']
    

        
    data = power_measurement_data['values']
   
    for j in range(0,len(data)):
        
        
        timestamp= data[j]['time']
        
        value=data[j]['value']
        
        
        for i in range(0,len(parent_nodes)):
            print(i)
            #Timestamp node                
            query = ("MATCH (m:temporal{value:'"+timestamp+"'}) return 1")   
    
            if len(str((graph.run(query))))==9: #(no data) is a string of length 9
                 #timestamp not found
                 print("time stamp not found")
                 query = (
                     "CREATE (n:Dynamic:end_parameter:temporal{name:'timestamp_value', value:'"+timestamp+"' }) "
                     "WITH n "
                     
                     "MATCH (m:meta{name:'timestamp'})"
                     "CREATE (m)-[f:has]->(n)" 
                     
                     #We create the timestamp and link it with its parent node
                     ) 
            
                 graph.run(query)
                
                #dont do anything if a node is already there, just link it with the data node 
                
    
    
    
    
            query =(  "CREATE (n:"+str(parent_nodes[i])+":dynamic:"+common_labels+"{name:'"+str(parent_nodes[i])+"_value', units:'"+units[i]+"',value:'"+value[i]+"'})"  
                 
                 "WITH n "            
                 "MATCH (m{name:'"+parent_nodes[i]+"'}),(o{name:'"+sources[i]+"'}),(p:temporal{name:'timestamp_value',value:'"+timestamp+"'})"
                 "CREATE (m)-[r:has ]->(n)"
                 "CREATE (o)-[s:measures ]->(n)"
                 "CREATE (n)-[t:measured_at ]->(p)"
    
    
                 
             )
            graph.run(query)
    



def populate_model_context_states(context_states):
  
    
    parent_nodes=  context_states['end parameters']
    common_labels= context_states['labels']   
    sources= context_states['sources']
    units= context_states['unit']
    
        
    data = context_states['values']
    
    
    for j in range(0, len(data)):
        
        print(j)
        
        timestamp= data[j]['time']
        
        value=data[j]['value']
        
        
        for i in range(0,len(parent_nodes)):
            
            
            if (value[i]== value[i]): #eliminating nan values
        
                #Timestamp node                
                query = ("MATCH (m:temporal{value:'"+timestamp+"'}) return 1")   
        
                if len(str((graph.run(query))))==9: #(no data) is a string of length 9
                     #timestamp not found
                     print("time stamp not found")
                     query = (
                         "CREATE (n:Dynamic:end_parameter:temporal{name:'timestamp_value', value:'"+timestamp+"' }) "
                         "WITH n "
                         
                         "MATCH (m:meta{name:'timestamp'})"
                         "CREATE (m)-[f:has]->(n)" 
                         
                         #We create the timestamp and link it with its parent node
                         ) 
                
                     graph.run(query)
                    
                    #dont do anything if a node is already there, just link it with the data node 
                    
        
        
        
        
                query =(  "CREATE (n:"+str(parent_nodes[i])+":dynamic:"+common_labels+"{name:'"+str(parent_nodes[i])+"_value', units:'"+str(units[i])+"',value:'"+str(value[i])+"'})"  
                     
                     "WITH n "            
                     "MATCH (m{name:'"+parent_nodes[i]+"'}),(o{name:'"+sources[i]+"'}),(p:temporal{name:'timestamp_value',value:'"+timestamp+"'})"
                     "CREATE (m)-[r:has ]->(n)"
                     "CREATE (o)-[s:measures ]->(n)"
                     "CREATE (n)-[t:measured_at ]->(p)"
        
        
                     
                 )
                graph.run(query)
        


def populate_model_user_data ( user_data ):
    
    parent_nodes=   user_data ['end parameters']
    common_labels=  user_data ['labels']       
    sources=  user_data ['sources']
   
    properties=  user_data ['node parameters']
   

    
    values=user_data ['values']
        
 
   
    for j in range(len(values)):
        
        user_id=values[j]['user_id']
        data=values[j]['data']
        
        properties_string=""
        
        for i in range(len(data)):
            
            
            properties_string += properties[i]+":'"+ str(data[i])+"',"
            
        properties_string=properties_string[:-1]
        
        
        query = (
            "CREATE (n:"+common_labels+":"+parent_nodes[0]+"_parameter {name:'"+str(user_id)+"'," +properties_string+" }) "
            "WITH n "
            
            "MATCH (m:meta{name:'user'})"#",(o:meta{name:'"+str(sources[0])+"'})"
            "CREATE (m)-[f:has]->(n)" 
            #"CREATE (o)-[g:stores]->(n)" 
            
            ) 
   
        graph.run(query)
       
    
def purge_model_user_data ( user_data ):
    
    parent_nodes=   user_data ['end parameters']
        
    query = ("MATCH (n:"+parent_nodes[0]+"_parameter )"
             "detach delete n"             
        ) 
     
    graph.run(query)



def populate_model_alarm ( alarm_data ):
    
    parent_nodes=   alarm_data ['end parameters']
    common_labels=  alarm_data ['labels']       
    sources=  alarm_data ['sources']
   
    properties=  alarm_data ['node parameters']
   

    
    values=alarm_data ['values']
        
 
   
    for j in range(len(values)):
        
        user_id=values[j]['user_id']
        data=values[j]['data']
        
        properties_string=""
        
        for i in range(len(data)):
            
            
            properties_string += properties[i]+":'"+ str(data[i])+"',"
            
        properties_string=properties_string[:-1]
        
        
        query = (
            "CREATE (n:"+common_labels+":"+parent_nodes[0]+"_parameter {name:'"+str(user_id)+"'," +properties_string+" }) "
            "WITH n "
            
            "MATCH (m:meta{name:'"+parent_nodes[0]+"'}),(o:user_parameter{name:'"+  str(user_id)       +"'})"
            "CREATE (m)-[f:has]->(n)" 
            "CREATE (o)-[g:sets]->(n)" 
            
            ) 
   
        graph.run(query)
       
def purge_model_alarm ( alarm_data ):
    
    parent_nodes=   alarm_data ['end parameters']
    query = ("MATCH (n:"+parent_nodes[0]+"_parameter )"
             "detach delete n"             
        ) 
   
    graph.run(query)


######################################################################################
                

#############################################################################################################
def model_data_dynamic():
    #Loop the ones below to capture changes 
    user_data = json.load(open('user.json'))
    alarm_data = json.load(open('alarm.json'))
    
    purge_model_user_data ( user_data )
    print('purged users')

    populate_model_user_data ( user_data )
    print('created users')
    
    
    purge_model_alarm ( alarm_data )
    print('purged alarms')
    populate_model_alarm ( alarm_data )
    print('created alarms')
   
    


def model_data_static():
    #LOAD
    #context_states = pd.read_csv('context_states.csv')
    #context_states = pd.read_csv('datasets/context_states2.csv')

    context_states = json.load(open('context_states.json'))  
    xdk_data = json.load(open('xdk_data.json'))
    medicaiton_plan = json.load(open('medication_plan.json'))
    power_measurement_data = json.load(open('power_measurement.json'))
    medication_times_data = json.load(open('medication_times.json'))

    #PUSH
    
    populate_model_xdk(xdk_data)
    add_user_medical_context(medicaiton_plan)
    populate_model_power(power_measurement_data)
    populate_model_context_states(context_states)
    populate_model_medication_times(medication_times_data)
    

########################################################################################################



#if __name__ == '__main__':
 #   model_data()
    