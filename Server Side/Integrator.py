# -*- coding: utf-8 -*-
"""
Created on Septemper 2021

@author: shukla
@updated by: mahfouz 
Updates: - Adding medication_times_to_json method to generating the json file for the medication_times.csv file.

Discription: processes different datasets and creates structures json datasets that can be validated using
             their respective set schemas
Usage: From this file you can generate the json file populated the meta model
"""

import json
import re
import pandas as pd


#########################################################################



# read data from the context_states.csv and create a json dump. 
def context_states_to_json(context_states):
    
    days = context_states['day']
    for i in range(len(days)):
        temp=days[i].split('-')
        days[i]=temp[2]+'-'+temp[1]+'-'+temp[0]
        
    
    times = context_states['time']
    medicines = context_states['medicines']
    
    for i in range(len(medicines)):
        if medicines[i]==medicines[i]:  #eliminating nan
            b=""
            for a in medicines[i]:
                if (a!="'") and (a!="[") and (a!="]") and (a!="[") :  #removing these characters from individual strings
                    b=b+str(a)
                medicines[i]=b        
    
    
    df = context_states[context_states.columns.difference(['day', 'time','medicines'])]
    
    df['medicines']=medicines

    nodes_names = df.columns.values.tolist() 
    print('Parameters:'+str(nodes_names))
    
    context_states_json={
        
            'end parameters':['activity',
             'blood_pressure',
             'heart_rate',
             'humidity',
             'location',
             'medication_rate',
             'respiration_rate',
             'skin_temperature',
             'temperature','medicines'],  
            
            'unit':          ['','mmHg','bpm','%','','','','bmp','cel','cel'],
            'sources':['fitbit','human_simulator','human_simulator',
                       'XDK_sensor_array','pill_dispenser','pill_dispenser',
                       'pill_dispenser','human_simulator','human_simulator',
                       'XDK_sensor_array'],
            'labels':'end_parameter',
            
        }
                 
        
    timestamps_values=[]
        
    df_matrix=df.to_numpy()        
    
    for values, day, time in zip(df_matrix, days, times):
        
        #timestamp = '_' + re.sub('-', '_', day) + 'T' + re.match('.+?(?=:)', time).group(0)
        timestamp = '_' + re.sub('-', '_', day) + 'T' + time.replace(':','')
      
        temp_dict={'time':timestamp,'value':[i for i in values]}
    
        timestamps_values.append(temp_dict)
        
        
        
    values={'values':timestamps_values}    
    context_states_json.update(values)  
    
    
    with open('context_states.json', 'w') as f:
        json.dump(context_states_json, f)
    
        
    
# read data from the Consolidated_xdk_data.csv and create a json dump. 
def xdk_data_to_json(Consolidated_xdk_data):
    
    days = Consolidated_xdk_data['day']
    times = Consolidated_xdk_data['time']
    df = Consolidated_xdk_data[Consolidated_xdk_data.columns.difference(['day', 'time'])]
    nodes_names = df.columns.values.tolist() 
    print('Parameters:'+str(nodes_names))
    
    xdk_data_json={
        
            'end parameters':['humidity',
             'light',
             'noise',
             'temperature'],  
            
            'unit':        ['%','cd','dB','cel'],
            'sources':['XDK_sensor_array','XDK_sensor_array','XDK_sensor_array',
                       'XDK_sensor_array'],
            
            'labels':'end_parameter',
            
        }
                 
        
    timestamps_values=[]
        
    df_matrix=df.to_numpy()        
    
    for values, day, time in zip(df_matrix, days, times):
        
        #timestamp = '_' + re.sub('-', '_', day) + 'T' + re.match('.+?(?=:)', time).group(0)
        timestamp = '_' + re.sub('-', '_', day) + 'T' + time.replace(':','')
     
        temp_dict={'time':timestamp,'value':[str(i) for i in values]}
    
        timestamps_values.append(temp_dict)
        
        
        
    values={'values':timestamps_values}    
    xdk_data_json.update(values)  
    
    
    with open('xdk_data.json', 'w') as f:
        json.dump(xdk_data_json, f)

# read data from the medication_times.csv and create a json dump. 
def medication_times_to_json(medication_times,path):
    
    days = medication_times['date']
    for i in range(len(days)):
        temp=days[i].split('-')
        days[i]=temp[2]+'-'+temp[1]+'-'+temp[0]
        
    times = medication_times['triggered_times']
    df = medication_times[medication_times.columns.difference(['date',                                                             
                                                               'triggered_times'])]
    nodes_names = df.columns.values.tolist() 
    print('Parameters:'+str(nodes_names))
    
    medication_times_json={
        
            'end parameters':['medication_times'],  
             'node parameters':['daytime','opened_times'],
              
            'sources':['database'],
            'labels':'user_context:end_parameter',
            
        }
                 
        
    timestamps_values=[]
        
    df_matrix=df.to_numpy()        
    
    for values, day, time in zip(df_matrix, days, times):
        
        #timestamp = '_' + re.sub('-', '_', day) + 'T' + re.match('.+?(?=:)', time).group(0)
        timestamp = '_' + re.sub('-', '_', day) + 'T' + time.replace(':','')
     
        temp_dict={'time':timestamp,'value':[str(i) for i in values]}
    
        timestamps_values.append(temp_dict)
        
        
        
    values={'values':timestamps_values}    
    medication_times_json.update(values)  
    
    
    with open(path, 'w') as f:
        json.dump(medication_times_json, f)   
# read data from the power_measurement.csv and create context json dump. 
def power_measurement_to_json(power_measurement):
    
    days = power_measurement['day']
    times = power_measurement['time']
    df = power_measurement[power_measurement.columns.difference(['day', 'time',
                                                                 'date_and_time'])]
    nodes_names = df.columns.values.tolist() 
    print('Parameters:'+str(nodes_names))
    
   
    power_measurement_json={
        
            'end parameters':['core_temperature',
             'mode',
             'power'],  
            
            'unit':        ['cel','','W'],
            'sources':['stationary_pill_dispenser','stationary_pill_dispenser','stationary_pill_dispenser'],
            
            'labels':'end_parameter'    
        }
                 
        
    timestamps_values=[]
        
    df_matrix=df.to_numpy()        
    
    for values, day, time in zip(df_matrix, days, times):
        
        #timestamp = '_' + re.sub('-', '_', day) + 'T' + re.match('.+?(?=:)', time).group(0)
        timestamp = '_' + re.sub('-', '_', day) + 'T' + time.replace(':','')
      
        temp_dict={'time':timestamp,'value':[str(i) for i in values]}
    
        timestamps_values.append(temp_dict)
        
        
        
    values={'values':timestamps_values}    
    power_measurement_json.update(values)  
    
    
    with open('power_measurement.json', 'w') as f:
        json.dump(power_measurement_json, f)
    
 

############################### pd 
       
def user_to_json(user):
    
    df=user.drop('Unnamed: 0', axis=1)
    
    nodes_names = df.columns.values.tolist() 
    
    
    user_data_json={
        
            'end parameters':['user'],
            'node parameters':['username',
             'first_name',
             'last_name',
             'gender',
             'password',
             'email',
             'phone',
             'id_std',
             'modilemode',
             'dob'],
            
            'sources':['database'],
            'labels':'user_context:end_parameter',
            
        }
                 
        
        
    df_matrix=df.to_numpy()        
        
    temp_val=[]
    
    for i in range(len(df)):
    
        user_id=df_matrix[i][0]
        
        
        temp_dict={'user_id':user_id,'data':[df_matrix[i][j] for j in range(1,len(df_matrix[i]))]}
    
        temp_val.append(temp_dict)
        
        
        
    values={'values':temp_val}    
    user_data_json.update(values)  
    
    
    with open('user.json', 'w') as f:
        json.dump(user_data_json, f)
    
       
    

def alarm_to_json(alarm):
    
    df=alarm.drop('Unnamed: 0', axis=1)
    
    nodes_names = df.columns.values.tolist() 
   
     
      
    user_id=list(df[ 'id_user'])
    df=df.drop('id_user', axis=1)
  
    
    alarm_data_json={
        
            'end parameters':['alarms'],
            'node parameters':['id_alarm_setting',
               'alarm_tone',
               'alarm_light',
               'daytime',
               'weekday',
               'timestamp'],
            
            'sources':['database'],
            'labels':'user_context:end_parameter',
            
        }
                 
        
        
    df_matrix=df.to_numpy()        
        
    temp_val=[]
    
    for i in range(len(df)):
        
        
        temp_dict={'user_id':str(user_id[i]),'data':[df_matrix[i][j] for j in range(0,len(df_matrix[i]))]}
    
        temp_val.append(temp_dict)
        
        
        
    values={'values':temp_val}    
    alarm_data_json.update(values)  
    
    
    with open('alarm.json', 'w') as f:
        json.dump(alarm_data_json, f)
    
           
         
########################################################################
def port_data_dynamic():

    user= pd.read_csv(r'data_from_pd\user.csv')
    alarm= pd.read_csv(r'data_from_pd\alarm_settings.csv')
    user_to_json(user)  
    print('user ported')

    alarm_to_json(alarm)
    print('ported alarm')


def port_data_static():
    
    context_states = pd.read_csv('datasets_to_convert\context_states.csv')
    Consolidated_xdk_data = pd.read_csv('datasets_to_convert\Consolidated_xdk_data.csv')
    power_measurement = pd.read_csv('datasets_to_convert\power_measurement.csv')
    medication_times = pd.read_csv('datasets_to_convert\medication_times.csv')
    #Mediacl plan is already stored as a json file so directly used by populator
    
    
    
    
    context_states_to_json(context_states)
    
    xdk_data_to_json(Consolidated_xdk_data)
   
    power_measurement_to_json(power_measurement)
   
    medication_times_to_json(medication_times,medication_times.json)
   
    print('-------- ported')



#if __name__ == '__main__':
 #   port_data()
   