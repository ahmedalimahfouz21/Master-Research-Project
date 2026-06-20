# -*- coding: utf-8 -*-
"""
Created on Septemper 2021

@author: shukla

@updated by: mahfouz
updates: - Adding Function, Behavior, Structure, Internal context, External Context.
         - Adding Alarm, Position Motors, Pill dispensing nodes to represent the system functionalities.
         - Adding AFFECTS, INPUT_TO,OUTPUT_TO, CONTROLS, MONITORS relationships between related nodes.

Discription:  uses the file 'metamodel_json.json' to create the metamodel.
Usage: From this file you can rest and create the meta model
"""

import json
import re
import pandas as pd
from py2neo import Relationship
from py2neo import Node

from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "poolloop"))

def reset_model_space():      
    graph.delete_all()


def reset_and_create_model():
    reset_model_space()
    
    f = open('metamodel_json.json')
    meta_model = json.load(f)
    
    
    
    #Data is a dictionary
    data = meta_model["metamodel"]
    #list of nodes to create
    nodes=list(data.keys())  
    
    
    for node in nodes:
        
        #Extract labels for a node
        labels= [data[node]["labels"]]
        string_of_labels="n"+":"+labels[0]
        
        #Extract properties a node
        properties_dict=data[node]['properties']
        properties=""
        
        for key, value in properties_dict.items():
            properties=properties+key+":'"+str(value)+"',"
        
        properties=properties[:-1]
        
        query =(  "CREATE ("+string_of_labels+" {name:'"+node+"',"+properties+"})")  
       
        graph.run(query)
       
        
       
    for node in nodes:    
               
        relationships_to= data[node]["relationships"]['to']
        relationships_from= data[node]["relationships"]['from']
    
           
        
        if len(relationships_to):
            
            for key, value in relationships_to.items():
             
                query =(" MATCH (m{name:'"+node+"'}) "
                        " MATCH (n{name:'"+key+"'}) "
                        "CREATE (m)-[r:"+value+"]->(n)"                        
                        )
                
                graph.run(query)
           
        
        if len(relationships_from):
            
            for key, value in relationships_from.items():
                
                query =(" MATCH (m{name:'"+node+"'}) "
                        " MATCH (n{name:'"+key+"'}) "
                        "CREATE (n)-[r:"+value+"]->(m)"                        
                        )
                
                graph.run(query)

reset_and_create_model()
     
      
