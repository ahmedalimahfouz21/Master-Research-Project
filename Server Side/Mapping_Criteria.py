# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 16:32:26 2022

@author: mahfouz

@Discription: This software component is responsible for mapping the output discrepancies to their present context values. 
"""

import json
import re
import pandas as pd
import os
import csv
from py2neo import Relationship
from py2neo import Node
from datetime import timedelta

from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "poolloop"))

#############################################################################################################
NUM_SECONDS_IN_A_MIN = 60
#############################################################################################################
"""
    Name: query_present_context_csv
    
    Discription: It queries the context values corresponding to the output the discrepancies
                   calculated by the previous software component and write them on the 
                   confirmation_times_discrepancy_with_context.csv file.
    Arguments: 
             path_source: str (path of the source .csv file)
             path_sink: str  (path of the output .csv file)
             
    Returns: None
"""
#############################################################################################################
def query_present_context_csv(path_source,path_sink):
    """Read actual medication_times.csv"""
    medication_times = pd.read_csv(path_source)
    timestamps=medication_times["timestamp"]
    daytimes=medication_times["daytime"]
    discrepancies=medication_times["discrepancy_in_user_confirmation_time"]
    """Query The related context values"""
    query=("  MATCH (f:function {name: 'Alarm'}) "
           "  MATCH (c)-[:AFFECTS]->(f)"
           "  RETURN c.name " )
    graph_data= graph.run(query).to_table()
    # print(graph_data)
    header = ['timestamp', 'daytime', 'discrepancy_in_user_confirmation_time','discrepancy_in_minutes']
    init_header_len=len(header)
    """Write file header"""
    for row in graph_data:
        header.append(row[0])
    f = open(path_sink, 'a+', newline='', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(header)
    f.close() 
    """Write the queried context values for each discrepancy value"""
    for i in range(0, len(timestamps)):
        timestamp=str(timestamps[i])
        daytime= str(daytimes[i])
        discrepancy=str(discrepancies[i])
        if(discrepancy!='not_opened'):
           discrepancy_in_timeformat_str= discrepancy[1:len(discrepancy)].split(':') 
           discrepancy_in_timeformat=timedelta(hours=int(discrepancy_in_timeformat_str[0]),minutes=int(discrepancy_in_timeformat_str[1]),seconds=float(discrepancy_in_timeformat_str[2]))
           discrepancy_in_minutes=discrepancy_in_timeformat.total_seconds()/ NUM_SECONDS_IN_A_MIN
           if(discrepancy[0]=='-'):
              discrepancy_in_minutes=-abs(discrepancy_in_minutes)
        else:
            discrepancy_in_minutes=timedelta(hours=4, minutes=30).total_seconds()/ NUM_SECONDS_IN_A_MIN
        query=( " MATCH (f:function {name: 'Alarm'}) "
                " MATCH (c)-[:AFFECTS]->(f)"
                " MATCH (c)-[:has]->(m)"
                " MATCH (m)-[:measured_at]->(t) WHERE t.value= $timestamp"
                " RETURN m.value ")
        graph_data= graph.run(query,timestamp=timestamp).to_table()
        if len(graph_data) == len(header)-init_header_len:
           data = []
           data.append(timestamp)
           data.append(daytime)
           data.append(discrepancy)
           data.append(discrepancy_in_minutes)
           for row in graph_data:
               data.append(row[0])
           f = open(path_sink, 'a+', newline='', encoding='utf-8')
           writer = csv.writer(f)
           writer.writerow(data)
           f.close()
#############################################################################################################
"""
    Name: mapping_equation_alarm_from_matlab
    
    Discription: It calculates a learned output discrepancy value based on the given context values
                 and the mapping equation generated via MATLAB script.
    Arguments: 
              path_source: str (path of the source .csv file)
              context: dict (contains mapping equation parameters () for noise and light)
        
    Returns: 
           mapping_output: dict (learned discrepancy, noise contribution in discrepancy, light contributionin discrepancy)
"""
#############################################################################################################
def mapping_equation_alarm_from_matlab(path_source,context):
    """Read mapping_equation.csv"""
    mapping_equ = pd.read_csv(path_source) 
    """Extract equation paramters"""
    noise_param= mapping_equ['noise']
    light_param= mapping_equ['light']
    discrepancy_param=mapping_equ['discrepancy']
    """Extract input context"""
    noise= context["noise"]
    light= context["light"]
    """Extract context mean value used for values normalization calculated via MATLAB"""
    noise_mu=noise_param[0]
    light_mu=light_param[0]
    discrepancy_mu=discrepancy_param[0]
    """Extract context standard deviation value used for values normalization calculated via MATLAB"""
    noise_S=noise_param[1]
    light_S=light_param[1]
    discrepancy_S=discrepancy_param[1]   
    """Extract context coefficient value used for values normalization calculated via MATLAB"""
    noise_coeff=noise_param[2]
    light_coeff=light_param[2] 
    """Publish the context coefficients to the the Graph model"""
    context_weights = [noise_coeff,light_coeff]
    query=( " MATCH (f:function {name: 'Alarm'}) "
            " MATCH (c)-[:AFFECTS]->(f)"
            " RETURN c.name LIMIT 2")
    graph_data= graph.run(query).to_table()
    i=0
    # print(context_weights)
    # print (graph_data)
    for context in graph_data:
        context_name = context[0]
        context_weight=str(context_weights[i])
        query=( " MATCH (f:function {name: 'Alarm'}) "
                " MATCH (c)-[:AFFECTS]->(f) WHERE c.name= $context_name"
                " SET c.Alarm_weight = $context_weight"
                " RETURN c.Alarm_weight")
        graph_data= graph.run(query,context_name=context_name,context_weight=context_weight).to_table()
        i=i+1
    """Normailze the given context values and calculate normaized learnned discrepancy value"""
    noise_norm= (noise-noise_mu)/noise_S
    light_norm= (light-light_mu)/light_S
    noise_part= noise_coeff*noise_norm
    light_part= light_coeff*light_norm
    discrepancy_mapped_norma=noise_part+light_part
    """Denormalize the learnned discrepancy value"""
    discrepancy_mapped = discrepancy_mapped_norma*discrepancy_S+discrepancy_mu
    # print(noise_norm)
    # print(light_norm)
    # print(discrepancy_mapped_norma)
    # print(discrepancy_mapped)
    mapping_output={"Discrepancy": discrepancy_mapped, "noise_effect":noise_part, "light_effect":light_part}
    return mapping_output
if __name__ == "__main__":
    # query_present_context_csv('actual_output\confirmation_times_discrepancy.csv','actual_output\confirmation_times_discrepancy_with_context.csv') 
    out=mapping_equation_alarm_from_matlab('actual_output\mapping_equation.csv',{"noise":60.36483428,"light":13.95})
    print(out)