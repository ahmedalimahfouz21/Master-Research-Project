# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 22:19:26 2022

@author: mahfo
"""

import time, threading
import datetime
from datetime import date

def foo():
    print("Thread")
    threading.Timer(1, foo).start()
foo()
# while True:
#   print("Main loop")

 