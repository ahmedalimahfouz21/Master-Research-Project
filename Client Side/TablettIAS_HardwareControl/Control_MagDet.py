from HardwareList import HardwareList
from Control_Detection import Control_Detection
from Control_LED import Control_LED
import time


class Control_MagDet:
	def __init__(self, led_obj: Control_LED, det_obj: Control_Detection, turn_off_time):
	
		
		self.led = led_obj
		self.det = det_obj
		self.turn_off_time = turn_off_time
		defaultvalue = 0
		timestamp = time.time()
		timestamp_monotonic = time.monotonic()
		self.dictMagazines = \
		{ "Detection":
				{"Monday": {"value" : defaultvalue , "timestamp": timestamp , "time_monotonic" :timestamp_monotonic },
				 "Tuesday": {"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic},
				 "Wednesday": {"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic},
                 "Thursday": {"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic},
                 "Friday": {"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic},
                 "Saturday": {"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic},
                 "Sunday": {"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic},
                 "Reserve":{"value" : defaultvalue , "timestamp": timestamp,"time_monotonic" :timestamp_monotonic}
                }
		}
	
	def magazin_detection(self):
		dict_det = self.det.get_magazines_in_Dispenser().get("status" , None)
		timestamp_new = time.time()
		timestamp_monotonic_new = time.monotonic()
		
		for x in dict_det:
			
			value = dict_det.get(x)
			det_weekday = self.dictMagazines.get("Detection").get(x)
			if value == 0:
				det_weekday.update({"value" : value , "timestamp" : timestamp_new, "time_monotonic" :timestamp_monotonic_new})
				self.led.show_detection_status_weekday(x, value)
			if value == 1:
				if value != det_weekday.get("value"):
					det_weekday.update({"value" :  value, "timestamp" : timestamp_new, "time_monotonic" :timestamp_monotonic_new})
					self.led.show_detection_status_weekday(x, value)
					
				else:
					diff =  timestamp_monotonic_new - det_weekday.get("time_monotonic")
					if diff < self.turn_off_time:
						self.led.show_detection_status_weekday(x, value)
					else :
						self.led.turn_off_weekday(x)
	
	def entry(self):
		self.led.led.turn_off_all()
		timestamp = time.time()
		timestamp_monotonic = time.monotonic()
		for x in self.dictMagazines:
			x.update({"value" : 0 , "timestamp" : timestamp, "time_monotonic" :timestamp_monotonic})
		
		self.magazin_detection()
